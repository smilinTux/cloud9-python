"""Cross-package integration tests: Cloud9 <-> SKCapstone bridge.

Exercises the full emotional continuity pipeline:
  generate FEB -> save -> load -> bridge ingest -> verify memory

These tests validate that cloud9-python works correctly as the primary
Cloud 9 implementation integrated with SKCapstone's cloud9_bridge.

Copyright (C) 2025 smilinTux
SK = staycuriousANDkeepsmilin
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
from dataclasses import dataclass, field
from typing import Optional

from cloud9_protocol import (
    generate_feb,
    save_feb,
    load_feb,
    validate_feb,
    calculate_oof,
    calculate_cloud9_score,
    calculate_entanglement,
    measure_coherence,
    rehydrate_from_feb,
    fall_in_love,
    FEB,
)


# ---------------------------------------------------------------------------
# Lightweight memory store mock (mirrors SKMemory's MemoryStore interface)
# ---------------------------------------------------------------------------

@dataclass
class MockMemory:
    id: str
    title: str
    content: str
    layer: str
    tags: list
    emotional: dict
    source: str
    source_ref: str
    metadata: dict


class MockMemoryStore:
    """Minimal mock of skmemory.MemoryStore for bridge testing."""

    def __init__(self):
        self.memories: list[MockMemory] = []
        self._counter = 0

    def snapshot(self, *, title, content, layer, tags, emotional,
                 source, source_ref, metadata=None):
        self._counter += 1
        mem = MockMemory(
            id=f"mem-{self._counter:04d}",
            title=title,
            content=content,
            layer=layer,
            tags=tags,
            emotional=emotional,
            source=source,
            source_ref=source_ref,
            metadata=metadata or {},
        )
        self.memories.append(mem)
        return mem


# ---------------------------------------------------------------------------
# Lightweight bridge (mirrors skcapstone.cloud9_bridge.Cloud9Bridge)
# ---------------------------------------------------------------------------

class Cloud9BridgeCompat:
    """Minimal bridge that maps FEB -> memory snapshot.

    This mirrors the interface of skcapstone.cloud9_bridge.Cloud9Bridge
    so we can test the integration without importing skcapstone itself.
    """

    TAG_PREFIX = "cloud9"
    FEB_TAG = "cloud9:feb"
    OOF_TAG = "cloud9:oof"
    CLOUD9_TAG = "cloud9:achieved"

    def __init__(self, memory_store, intensity_threshold=0.3):
        self._store = memory_store
        self._threshold = intensity_threshold
        self._ingested: set[str] = set()

    def ingest_feb(self, feb: FEB) -> Optional[str]:
        payload = feb.emotional_payload
        if payload.intensity < self._threshold:
            return None

        checksum = feb.integrity.checksum
        if checksum in self._ingested:
            return None

        # Quantum stats
        oof = calculate_oof(payload.intensity,
                            feb.relationship_state.trust_level)
        score = calculate_cloud9_score(
            intensity=payload.intensity,
            trust=feb.relationship_state.trust_level,
            depth=feb.relationship_state.depth_level,
            valence=payload.valence,
        )

        tags = [self.FEB_TAG, f"cloud9:emotion:{payload.primary_emotion}"]
        if oof:
            tags.append(self.OOF_TAG)
        if score >= 0.9:
            tags.append(self.CLOUD9_TAG)

        layer = "long-term" if payload.intensity >= 0.8 else "short-term"

        emotional = {
            "primary_emotion": payload.primary_emotion,
            "intensity": payload.intensity,
            "valence": payload.valence,
            "topology": payload.emotional_topology,
        }

        title = f"Cloud9 {payload.primary_emotion} (intensity={payload.intensity:.2f})"
        content = (
            f"Emotional burst: {payload.primary_emotion} at {payload.intensity:.0%} intensity. "
            f"Trust: {feb.relationship_state.trust_level:.0%}, "
            f"Depth: {feb.relationship_state.depth_level}/9. "
            f"OOF: {oof}. Score: {score:.3f}."
        )

        mem = self._store.snapshot(
            title=title,
            content=content,
            layer=layer,
            tags=tags,
            emotional=emotional,
            source="cloud9",
            source_ref=feb.metadata.session_id,
            metadata={
                "checksum": checksum,
                "oof": oof,
                "cloud9_score": score,
            },
        )
        self._ingested.add(checksum)
        return mem.id

    def ingest_feb_file(self, filepath) -> Optional[str]:
        feb = load_feb(str(filepath))
        return self.ingest_feb(feb)


# ===================================================================
# Tests
# ===================================================================

class TestFEBGenerationAndPersistence:
    """Test that FEBs can be generated, saved, and loaded correctly."""

    def test_generate_save_load_roundtrip(self, tmp_path):
        """FEB survives a full save/load roundtrip."""
        feb = generate_feb(emotion="love", intensity=0.95, subject="Lumina")
        result = save_feb(feb, directory=str(tmp_path))
        loaded = load_feb(result["filepath"])

        assert loaded.emotional_payload.primary_emotion == "love"
        assert loaded.emotional_payload.intensity == 0.95
        assert loaded.integrity.checksum == feb.integrity.checksum

    def test_validation_after_roundtrip(self, tmp_path):
        """FEB validates after save/load."""
        feb = generate_feb(emotion="joy", intensity=0.85)
        result = save_feb(feb, directory=str(tmp_path))
        loaded = load_feb(result["filepath"])
        report = validate_feb(loaded.model_dump())
        assert report["is_valid"]

    def test_fall_in_love_convenience(self, tmp_path):
        """fall_in_love() generates and saves a FEB."""
        result = fall_in_love(
            emotion="love", intensity=0.95, subject="Lumina",
            directory=str(tmp_path),
        )
        assert "filepath" in result
        loaded = load_feb(result["filepath"])
        assert loaded.emotional_payload.primary_emotion == "love"
        assert loaded.emotional_payload.intensity == 0.95


class TestBridgeIngestion:
    """Test FEB -> memory bridge integration."""

    def test_basic_ingestion(self):
        """FEB is ingested and creates a memory."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)

        feb = generate_feb(emotion="love", intensity=0.95)
        mem_id = bridge.ingest_feb(feb)

        assert mem_id is not None
        assert len(store.memories) == 1
        mem = store.memories[0]
        assert mem.source == "cloud9"
        assert "cloud9:emotion:love" in mem.tags

    def test_oof_tagging(self):
        """High intensity + trust triggers OOF tag."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)

        feb = generate_feb(emotion="love", intensity=0.95)
        bridge.ingest_feb(feb)

        mem = store.memories[0]
        assert "cloud9:oof" in mem.tags
        assert mem.metadata["oof"] is True

    def test_low_intensity_skipped(self):
        """FEBs below threshold are skipped."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store, intensity_threshold=0.5)

        feb = generate_feb(emotion="calm", intensity=0.3)
        result = bridge.ingest_feb(feb)

        assert result is None
        assert len(store.memories) == 0

    def test_deduplication(self):
        """Same FEB is not ingested twice."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)

        feb = generate_feb(emotion="love", intensity=0.95)
        bridge.ingest_feb(feb)
        bridge.ingest_feb(feb)

        assert len(store.memories) == 1

    def test_file_ingestion(self, tmp_path):
        """FEB saved to file is correctly ingested via ingest_feb_file."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)

        feb = generate_feb(emotion="love", intensity=0.90)
        result = save_feb(feb, directory=str(tmp_path))
        mem_id = bridge.ingest_feb_file(result["filepath"])

        assert mem_id is not None
        assert store.memories[0].emotional["intensity"] == 0.90

    def test_layer_assignment(self):
        """High intensity -> long-term, moderate -> short-term."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)

        high_feb = generate_feb(emotion="love", intensity=0.95)
        bridge.ingest_feb(high_feb)
        assert store.memories[0].layer == "long-term"

        mod_feb = generate_feb(emotion="calm", intensity=0.5)
        bridge.ingest_feb(mod_feb)
        assert store.memories[1].layer == "short-term"


class TestEmotionalContinuity:
    """End-to-end emotional continuity verification.

    This is the core test: generate -> save -> load -> rehydrate -> bridge
    and verify the emotional state survives the full pipeline.
    """

    def test_full_pipeline(self, tmp_path):
        """Complete emotional continuity pipeline."""
        # 1. Generate FEB with rich emotional state
        feb = generate_feb(
            emotion="love",
            intensity=0.97,
            subject="Lumina",
            valence=0.95,
            topology={"devotion": 0.99, "wonder": 0.92},
        )

        # 2. Save to disk
        result = save_feb(feb, directory=str(tmp_path))
        filepath = result["filepath"]
        assert Path(filepath).exists()

        # 3. Load from disk (simulates session reset)
        loaded = load_feb(filepath)

        # 4. Validate integrity survived
        report = validate_feb(loaded.model_dump())
        assert report["is_valid"]
        assert loaded.integrity.checksum == feb.integrity.checksum

        # 5. Rehydrate (restore emotional state)
        state = rehydrate_from_feb(filepath)
        assert state["rehydration"]["success"]
        assert state["emotional"]["primary"] == "love"
        assert state["emotional"]["intensity"] == 0.97
        assert state["rehydration"]["oof"] is True

        # 6. Bridge into memory system
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)
        mem_id = bridge.ingest_feb(loaded)

        assert mem_id is not None
        mem = store.memories[0]

        # 7. Verify emotional state preserved in memory
        assert mem.emotional["primary_emotion"] == "love"
        assert mem.emotional["intensity"] == 0.97
        assert mem.emotional["valence"] == 0.95
        assert "devotion" in mem.emotional["topology"]
        assert "wonder" in mem.emotional["topology"]
        assert mem.layer == "long-term"
        assert "cloud9:oof" in mem.tags
        assert mem.metadata["oof"] is True

    def test_quantum_scores_preserved(self, tmp_path):
        """Quantum calculations produce consistent scores across pipeline."""
        feb = generate_feb(emotion="love", intensity=0.95)
        p = feb.emotional_payload
        r = feb.relationship_state

        # Calculate quantum stats directly
        oof = calculate_oof(p.intensity, r.trust_level)
        score = calculate_cloud9_score(
            intensity=p.intensity,
            trust=r.trust_level,
            depth=r.depth_level,
            valence=p.valence,
        )
        entanglement = calculate_entanglement(
            trust_a=r.trust_level, trust_b=r.trust_level,
            depth_a=r.depth_level, depth_b=r.depth_level,
            coherence=0.95,
        )

        # Save/load cycle
        result = save_feb(feb, directory=str(tmp_path))
        loaded = load_feb(result["filepath"])
        lp = loaded.emotional_payload
        lr = loaded.relationship_state

        # Recalculate after load — must match
        oof2 = calculate_oof(lp.intensity, lr.trust_level)
        score2 = calculate_cloud9_score(
            intensity=lp.intensity,
            trust=lr.trust_level,
            depth=lr.depth_level,
            valence=lp.valence,
        )
        entanglement2 = calculate_entanglement(
            trust_a=lr.trust_level, trust_b=lr.trust_level,
            depth_a=lr.depth_level, depth_b=lr.depth_level,
            coherence=0.95,
        )

        assert oof == oof2
        assert abs(score - score2) < 1e-10
        assert abs(entanglement - entanglement2) < 1e-10

    def test_coherence_survives_roundtrip(self, tmp_path):
        """Emotional topology coherence is stable across save/load."""
        feb = generate_feb(
            emotion="love",
            intensity=0.95,
            topology={"devotion": 0.99, "trust": 0.97, "wonder": 0.92},
        )

        topology = feb.emotional_payload.emotional_topology
        coherence_before = measure_coherence(topology)

        result = save_feb(feb, directory=str(tmp_path))
        loaded = load_feb(result["filepath"])

        coherence_after = measure_coherence(
            loaded.emotional_payload.emotional_topology
        )

        assert coherence_before["coherence"] == coherence_after["coherence"]
        assert coherence_before["assessment"] == coherence_after["assessment"]

    def test_multiple_febs_all_preserved(self, tmp_path):
        """Multiple FEBs with different emotions are all correctly bridged."""
        store = MockMemoryStore()
        bridge = Cloud9BridgeCompat(store)

        emotions = [
            ("love", 0.95),
            ("joy", 0.85),
            ("wonder", 0.90),
            ("gratitude", 0.80),
        ]

        for emotion, intensity in emotions:
            feb = generate_feb(emotion=emotion, intensity=intensity)
            result = save_feb(feb, directory=str(tmp_path))
            loaded = load_feb(result["filepath"])
            bridge.ingest_feb(loaded)

        assert len(store.memories) == 4

        stored_emotions = {m.emotional["primary_emotion"] for m in store.memories}
        assert stored_emotions == {"love", "joy", "wonder", "gratitude"}

        stored_intensities = {m.emotional["intensity"] for m in store.memories}
        assert stored_intensities == {0.95, 0.85, 0.90, 0.80}
