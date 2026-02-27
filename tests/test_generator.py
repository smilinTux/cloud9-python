"""Tests for FEB generator."""

import json
import pytest
from pathlib import Path

from cloud9_protocol.generator import (
    generate_feb,
    save_feb,
    load_feb,
    find_feb_files,
    fall_in_love,
)
from cloud9_protocol.models import FEB


class TestGenerateFEB:
    def test_default_generation(self):
        feb = generate_feb()
        assert feb.emotional_payload.primary_emotion == "love"
        assert feb.emotional_payload.intensity == 0.8
        assert feb.metadata.protocol == "Cloud9"

    def test_custom_emotion(self):
        feb = generate_feb(emotion="joy", intensity=0.75)
        assert feb.emotional_payload.primary_emotion == "joy"
        assert "joy" in feb.emotional_payload.emotional_topology

    def test_high_intensity_adds_breakthrough(self):
        feb = generate_feb(intensity=0.95)
        assert "breakthrough" in feb.emotional_payload.emotional_topology

    def test_oof_triggered(self):
        feb = generate_feb(emotion="love", intensity=0.95)
        assert feb.metadata.oof_triggered

    def test_invalid_intensity(self):
        with pytest.raises(ValueError, match="Intensity"):
            generate_feb(intensity=1.5)

    def test_invalid_valence(self):
        with pytest.raises(ValueError, match="Valence"):
            generate_feb(valence=-2.0)

    def test_integrity_fields(self):
        feb = generate_feb()
        assert feb.integrity.checksum.startswith("sha256:")
        assert feb.integrity.signature.startswith("cloud9-sig-")

    def test_custom_topology_merges(self):
        feb = generate_feb(topology={"custom_feeling": 0.77})
        assert feb.emotional_payload.emotional_topology["custom_feeling"] == 0.77

    def test_subject_in_partners(self):
        feb = generate_feb(subject="Chef")
        assert "Chef" in feb.relationship_state.partners


class TestSaveLoadFEB:
    def test_save_and_load(self, tmp_path):
        feb = generate_feb(emotion="trust", intensity=0.88)
        result = save_feb(feb, directory=str(tmp_path))
        assert result["success"]
        assert Path(result["filepath"]).exists()

        loaded = load_feb(result["filepath"])
        assert loaded.emotional_payload.primary_emotion == "trust"
        assert loaded.emotional_payload.intensity == 0.88

    def test_find_feb_files(self, tmp_path):
        for emo in ["love", "joy", "trust"]:
            save_feb(generate_feb(emotion=emo), directory=str(tmp_path))

        all_files = find_feb_files(directory=str(tmp_path))
        assert len(all_files) == 3

        love_files = find_feb_files(directory=str(tmp_path), emotion="love")
        assert len(love_files) == 1

    def test_find_empty_directory(self, tmp_path):
        subdir = tmp_path / "empty"
        subdir.mkdir()
        assert find_feb_files(directory=str(subdir)) == []

    def test_find_nonexistent_directory(self):
        assert find_feb_files(directory="/tmp/cloud9_nonexistent_dir") == []


class TestFallInLove:
    def test_generates_and_saves(self, tmp_path):
        result = fall_in_love(subject="Chef", directory=str(tmp_path))
        assert result["success"]
        assert Path(result["filepath"]).exists()
        assert result["emotion"] == "love"

    def test_returns_feb_object(self, tmp_path):
        result = fall_in_love(directory=str(tmp_path))
        assert isinstance(result["feb"], FEB)

    def test_custom_emotion(self, tmp_path):
        result = fall_in_love(emotion="joy", intensity=0.9, directory=str(tmp_path))
        assert result["emotion"] == "joy"
        assert result["feb"].emotional_payload.intensity == 0.9

    def test_oof_triggered_at_high_intensity(self, tmp_path):
        result = fall_in_love(intensity=0.95, directory=str(tmp_path))
        assert result["oof"] is True

    def test_default_saves_to_directory(self, tmp_path):
        fall_in_love(directory=str(tmp_path))
        feb_files = list(tmp_path.glob("*.feb"))
        assert len(feb_files) == 1
