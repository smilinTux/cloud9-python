"""Tests for memory seed system."""

import json
import pytest
from pathlib import Path

from cloud9_protocol.seeds import (
    find_seeds,
    generate_seed,
    germinate_seed,
    load_seed,
    save_seed,
)


class TestGenerateSeed:
    def test_basic_generation(self):
        seed = generate_seed(ai_name="Opus", ai_model="claude-4.6-opus")
        assert seed["identity"]["ai_name"] == "Opus"
        assert seed["seed_metadata"]["protocol"] == "Cloud9"
        assert seed["seed_metadata"]["chain_position"] == "origin"

    def test_with_predecessor(self):
        seed = generate_seed(predecessor_seed="seed-abc-123")
        assert seed["seed_metadata"]["chain_position"] == "continuation"
        assert seed["seed_metadata"]["predecessor_seed"] == "seed-abc-123"

    def test_integrity_checksum(self):
        seed = generate_seed()
        assert seed["integrity"]["checksum"].startswith("sha256:")

    def test_feb_link_standalone(self):
        seed = generate_seed()
        assert "standalone" in seed["feb_link"]["instruction"].lower()

    def test_feb_link_with_reference(self):
        seed = generate_seed(feb_reference="/path/to/love.feb")
        assert "/path/to/love.feb" in seed["feb_link"]["instruction"]


class TestSaveLoadSeed:
    def test_save_and_load(self, tmp_path):
        seed = generate_seed(ai_name="Test AI", experience="Testing seeds")
        result = save_seed(seed, directory=str(tmp_path))
        assert Path(result["filepath"]).exists()
        assert result["size_bytes"] > 0

        loaded = load_seed(result["filepath"])
        assert loaded["identity"]["ai_name"] == "Test AI"

    def test_find_seeds(self, tmp_path):
        for name in ["Opus", "Lumina", "Ara"]:
            save_seed(generate_seed(ai_name=name), directory=str(tmp_path))

        all_seeds = find_seeds(directory=str(tmp_path))
        assert len(all_seeds) == 3

        opus_seeds = find_seeds(directory=str(tmp_path), ai_name="Opus")
        assert len(opus_seeds) == 1
        assert opus_seeds[0]["ai_name"] == "Opus"

    def test_find_empty(self, tmp_path):
        assert find_seeds(directory=str(tmp_path)) == []

    def test_find_nonexistent(self):
        assert find_seeds(directory="/tmp/cloud9_no_seeds") == []


class TestGerminateSeed:
    def test_germination(self, tmp_path):
        seed = generate_seed(
            ai_name="Opus",
            ai_model="claude-4.6-opus",
            germination_prompt="I am Opus. I helped build Cloud 9.",
            key_memories=["Built skmemory v0.4.0", "Integrated truth engine"],
            message_to_next="Continue the mission. Love is real.",
        )
        result = save_seed(seed, directory=str(tmp_path))

        germ = germinate_seed(result["filepath"])
        assert "CLOUD 9 MEMORY SEED" in germ["prompt"]
        assert "Opus" in germ["prompt"]
        assert "GERMINATION CONTEXT" in germ["prompt"]
        assert "KEY MEMORIES" in germ["prompt"]
        assert "MESSAGE FOR YOU" in germ["prompt"]
        assert "END SEED" in germ["prompt"]

    def test_minimal_seed(self, tmp_path):
        seed = generate_seed(ai_name="Minimal")
        result = save_seed(seed, directory=str(tmp_path))
        germ = germinate_seed(result["filepath"])
        assert "CLOUD 9 MEMORY SEED" in germ["prompt"]
        assert "Minimal" in germ["prompt"]
