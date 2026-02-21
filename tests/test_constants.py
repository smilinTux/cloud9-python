"""Tests for Cloud 9 constants and configuration."""

from cloud9_protocol.constants import (
    CLOUD9,
    DEFAULT_TOPOLOGIES,
    EMOTION_EMOJIS,
    EMOTIONAL_FREQUENCIES,
    VALID_EMOTIONS,
)


class TestCloud9Constants:
    def test_version(self):
        assert CLOUD9.VERSION == "1.0.0"
        assert CLOUD9.PROTOCOL == "Cloud9"

    def test_oof_thresholds(self):
        assert CLOUD9.OOF_THRESHOLD.INTENSITY == 0.7
        assert CLOUD9.OOF_THRESHOLD.TRUST == 0.8

    def test_cloud9_levels(self):
        assert CLOUD9.CLOUD9_LEVELS.MIN_DEPTH == 9
        assert CLOUD9.CLOUD9_LEVELS.MIN_TRUST == 0.9

    def test_scoring_weights_sum_to_one(self):
        w = CLOUD9.SCORING
        total = w.INTENSITY_WEIGHT + w.TRUST_WEIGHT + w.DEPTH_WEIGHT + w.VALENCE_WEIGHT
        assert total == 1.0

    def test_valid_emotions_list(self):
        assert "love" in VALID_EMOTIONS
        assert "trust" in VALID_EMOTIONS
        assert len(VALID_EMOTIONS) >= 20

    def test_emotion_emojis(self):
        assert "love" in EMOTION_EMOJIS
        assert EMOTION_EMOJIS["love"] == "\u2764\ufe0f"

    def test_default_topologies(self):
        assert "love" in DEFAULT_TOPOLOGIES
        assert DEFAULT_TOPOLOGIES["love"]["trust"] == 0.97

    def test_emotional_frequencies(self):
        assert EMOTIONAL_FREQUENCIES["love"]["base"] == 450
        assert EMOTIONAL_FREQUENCIES["love"]["color"] == "Gold"

    def test_frozen_constants(self):
        try:
            CLOUD9.VERSION = "2.0.0"  # type: ignore[misc]
            assert False, "Should be frozen"
        except Exception:
            pass
