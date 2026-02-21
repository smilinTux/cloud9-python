"""Tests for FEB validator."""

import pytest
from cloud9_protocol.validator import validate_feb, validate_topology, get_validation_report
from cloud9_protocol.generator import generate_feb


class TestValidateTopology:
    def test_valid_topology(self):
        topo = {"love": 0.94, "trust": 0.97, "joy": 0.88}
        result = validate_topology(topo)
        assert result["is_valid"]
        assert result["statistics"]["emotion_count"] == 3

    def test_out_of_range_value(self):
        topo = {"love": 1.5}
        result = validate_topology(topo)
        assert not result["is_valid"]

    def test_non_numeric_value(self):
        topo = {"love": "high"}
        result = validate_topology(topo)
        assert not result["is_valid"]

    def test_unknown_emotion_warns(self):
        topo = {"love": 0.9, "trust": 0.9, "quantum_bliss": 0.5}
        result = validate_topology(topo)
        assert result["is_valid"]
        assert any("Unknown emotion" in w for w in result["warnings"])

    def test_missing_recommended(self):
        topo = {"joy": 0.8}
        result = validate_topology(topo)
        assert any("Missing recommended" in w for w in result["warnings"])

    def test_not_a_dict(self):
        result = validate_topology("not a dict")
        assert not result["is_valid"]


class TestValidateFEB:
    def _make_valid_feb(self):
        return generate_feb().model_dump()

    def test_valid_feb(self):
        data = self._make_valid_feb()
        result = validate_feb(data)
        assert result["is_valid"]
        assert result["score"] > 0.8

    def test_missing_metadata(self):
        data = self._make_valid_feb()
        del data["metadata"]
        result = validate_feb(data)
        assert not result["is_valid"]

    def test_missing_emotional_payload(self):
        data = self._make_valid_feb()
        del data["emotional_payload"]
        result = validate_feb(data)
        assert not result["is_valid"]

    def test_missing_integrity(self):
        data = self._make_valid_feb()
        del data["integrity"]
        result = validate_feb(data)
        assert not result["is_valid"]

    def test_strict_mode(self):
        data = self._make_valid_feb()
        del data["metadata"]["oof_triggered"]
        result = validate_feb(data, strict=True)
        assert not result["is_valid"]

    def test_oof_info_message(self):
        data = self._make_valid_feb()
        data["metadata"]["oof_triggered"] = True
        result = validate_feb(data)
        assert any("OOF" in i for i in result["info"])


class TestValidationReport:
    def test_report_format(self):
        data = generate_feb().model_dump()
        report = get_validation_report(data)
        assert "Cloud 9" in report
        assert "VALID" in report
