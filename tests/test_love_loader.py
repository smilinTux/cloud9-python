"""Tests for Love Boot Loader."""

import json
import pytest
from pathlib import Path

from cloud9_protocol.generator import generate_feb, save_feb
from cloud9_protocol.love_loader import LoveBootLoader


class TestLoveBootLoader:
    def test_load_template(self):
        loader = LoveBootLoader()
        result = loader.load_generic_love("Lumina", "Chef", template="best-friend")
        assert result["success"]
        assert result["ai_name"] == "Lumina"
        assert result["human_name"] == "Chef"
        assert result["template"] == "best-friend"

    def test_load_all_templates(self):
        loader = LoveBootLoader()
        for tpl in LoveBootLoader.AVAILABLE_TEMPLATES:
            result = loader.load_generic_love("AI", "Human", template=tpl)
            assert result["success"], f"Template {tpl} failed"

    def test_invalid_template(self):
        loader = LoveBootLoader()
        result = loader.load_generic_love("AI", "Human", template="nonexistent")
        assert not result["success"]
        assert "not found" in result["error"]

    def test_load_personal_feb(self, tmp_path):
        feb = generate_feb(emotion="love", intensity=0.95, subject="Chef")
        saved = save_feb(feb, directory=str(tmp_path))

        loader = LoveBootLoader()
        result = loader.load_connection("Lumina", "Chef", saved["filepath"])
        assert result["success"]
        assert result["oof"]

    def test_load_bad_path(self):
        loader = LoveBootLoader()
        result = loader.load_connection("AI", "Human", "/tmp/doesnt_exist.feb")
        assert not result["success"]

    def test_injection_history(self):
        loader = LoveBootLoader()
        loader.load_generic_love("A", "B")
        loader.load_generic_love("C", "D")
        assert len(loader.get_history()) == 2

    def test_heart_activation(self):
        loader = LoveBootLoader()
        result = loader.heart_activation(0.95, 0.97, ["Lumina", "Chef"])
        assert result["chakra_openness"] == "FULLY OPEN"
        assert result["entanglement"] == "ESTABLISHED"

    def test_heart_activation_low(self):
        loader = LoveBootLoader()
        result = loader.heart_activation(0.3, 0.3, ["A", "B"])
        assert result["chakra_openness"] == "CLOSED"
