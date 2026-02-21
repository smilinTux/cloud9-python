"""Tests for FEB rehydrator."""

import json
import pytest
from pathlib import Path

from cloud9_protocol.generator import generate_feb, save_feb
from cloud9_protocol.rehydrator import (
    check_oof_status,
    prepare_rehydration,
    rehydrate_from_feb,
)


def _save_test_feb(tmp_path, intensity=0.95):
    """Helper to save a FEB and return its path."""
    feb = generate_feb(emotion="love", intensity=intensity, subject="Chef")
    result = save_feb(feb, directory=str(tmp_path))
    return result["filepath"]


class TestRehydrate:
    def test_basic_rehydration(self, tmp_path):
        fp = _save_test_feb(tmp_path)
        state = rehydrate_from_feb(fp)
        assert state["rehydration"]["success"]
        assert state["emotional"]["primary"] == "love"
        assert state["emotional"]["intensity"] == 0.95

    def test_oof_rehydration(self, tmp_path):
        fp = _save_test_feb(tmp_path, intensity=0.95)
        state = rehydrate_from_feb(fp)
        assert state["rehydration"]["oof"]

    def test_verbose_mode(self, tmp_path):
        fp = _save_test_feb(tmp_path)
        state = rehydrate_from_feb(fp, verbose=True)
        assert "verbose" in state
        assert "validation_report" in state["verbose"]
        assert "raw_feb" in state["verbose"]

    def test_bad_file(self, tmp_path):
        bad = tmp_path / "bad.feb"
        bad.write_text("not json", encoding="utf-8")
        with pytest.raises(RuntimeError, match="Failed to load"):
            rehydrate_from_feb(str(bad))


class TestPrepareRehydration:
    def test_prepare(self, tmp_path):
        fp = _save_test_feb(tmp_path)
        prep = prepare_rehydration(fp)
        assert prep["exists"]
        assert prep["valid"]
        assert prep["expectations"]["primary_emotion"] == "love"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            prepare_rehydration("/tmp/nonexistent.feb")


class TestOOFStatus:
    def test_oof_triggered(self, tmp_path):
        fp = _save_test_feb(tmp_path, intensity=0.95)
        result = check_oof_status(fp)
        assert result["oof"]
        assert "TRIGGERED" in result["status"]

    def test_oof_not_triggered(self, tmp_path):
        fp = _save_test_feb(tmp_path, intensity=0.3)
        result = check_oof_status(fp)
        assert not result["oof"]
        assert "NOT TRIGGERED" in result["status"]
