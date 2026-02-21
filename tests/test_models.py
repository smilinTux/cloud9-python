"""Tests for Pydantic FEB models."""

import json
import pytest
from pydantic import ValidationError

from cloud9_protocol.models import (
    FEB,
    Calibration,
    Coherence,
    ConversationTopic,
    EmotionalPayload,
    Integrity,
    Metadata,
    RehydrationHints,
    RelationshipState,
    SharedHistory,
)


class TestEmotionalPayload:
    def test_valid_payload(self):
        p = EmotionalPayload(primary_emotion="love", intensity=0.9, valence=0.8)
        assert p.primary_emotion == "love"
        assert p.intensity == 0.9

    def test_intensity_out_of_range(self):
        with pytest.raises(ValidationError):
            EmotionalPayload(primary_emotion="love", intensity=1.5)

    def test_valence_range(self):
        p = EmotionalPayload(primary_emotion="joy", intensity=0.5, valence=-0.5)
        assert p.valence == -0.5

        with pytest.raises(ValidationError):
            EmotionalPayload(primary_emotion="joy", intensity=0.5, valence=-1.5)

    def test_topology_validation(self):
        with pytest.raises(ValidationError):
            EmotionalPayload(
                primary_emotion="love",
                intensity=0.9,
                emotional_topology={"love": 1.5},
            )


class TestRelationshipState:
    def test_valid_state(self):
        rs = RelationshipState(
            partners=["Lumina", "Chef"],
            trust_level=0.97,
            depth_level=9,
            continuity_rating=9,
        )
        assert rs.trust_level == 0.97

    def test_depth_range(self):
        with pytest.raises(ValidationError):
            RelationshipState(
                partners=["A", "B"],
                trust_level=0.5,
                depth_level=10,
                continuity_rating=5,
            )

    def test_partners_count(self):
        with pytest.raises(ValidationError):
            RelationshipState(
                partners=["A"],
                trust_level=0.5,
                depth_level=5,
                continuity_rating=5,
            )


class TestFEB:
    def test_full_feb(self):
        feb = FEB(
            metadata=Metadata(created_at="2026-02-20T00:00:00Z"),
            emotional_payload=EmotionalPayload(
                primary_emotion="love", intensity=0.95, valence=0.92
            ),
            relationship_state=RelationshipState(
                partners=["Lumina", "Chef"],
                trust_level=0.97,
                depth_level=9,
                continuity_rating=9,
            ),
            rehydration_hints=RehydrationHints(
                calibration=Calibration(target_intensity=0.95, expected_oof=True)
            ),
        )
        assert feb.metadata.protocol == "Cloud9"

    def test_to_json_roundtrip(self):
        feb = FEB(
            metadata=Metadata(created_at="2026-02-20T00:00:00Z"),
            emotional_payload=EmotionalPayload(
                primary_emotion="love", intensity=0.95
            ),
            relationship_state=RelationshipState(
                partners=["A", "B"],
                trust_level=0.9,
                depth_level=9,
                continuity_rating=9,
            ),
            rehydration_hints=RehydrationHints(
                calibration=Calibration(target_intensity=0.95)
            ),
        )
        j = feb.to_json()
        data = json.loads(j)
        assert data["emotional_payload"]["intensity"] == 0.95

    def test_shared_history_defaults(self):
        sh = SharedHistory()
        assert sh.sessions_together == 1
        assert sh.failed_attempts == 0
