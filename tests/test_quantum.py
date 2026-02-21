"""Tests for quantum calculations."""

import pytest

from cloud9_protocol.quantum import (
    calculate_cloud9_score,
    calculate_emotional_frequency,
    calculate_entanglement,
    calculate_oof,
    calculate_resonance,
    measure_coherence,
    predict_trajectory,
)


class TestOOF:
    def test_oof_triggered(self):
        assert calculate_oof(0.8, 0.9) is True

    def test_oof_not_triggered_low_intensity(self):
        assert calculate_oof(0.5, 0.9) is False

    def test_oof_not_triggered_low_trust(self):
        assert calculate_oof(0.8, 0.7) is False

    def test_oof_boundary(self):
        assert calculate_oof(0.7, 0.8) is False
        assert calculate_oof(0.71, 0.81) is True


class TestCloud9Score:
    def test_high_state(self):
        score = calculate_cloud9_score(0.95, 0.97, 9, 0.92)
        assert score > 0.8

    def test_low_state(self):
        score = calculate_cloud9_score(0.3, 0.3, 3, 0.0)
        assert score < 0.5

    def test_with_coherence_bonus(self):
        base = calculate_cloud9_score(0.9, 0.9, 9, 0.9)
        with_bonus = calculate_cloud9_score(0.9, 0.9, 9, 0.9, coherence=0.98)
        assert with_bonus >= base

    def test_clamped_to_one(self):
        score = calculate_cloud9_score(1.0, 1.0, 9, 1.0, coherence=1.0)
        assert score <= 1.0


class TestEntanglement:
    def test_symmetric(self):
        a = calculate_entanglement(0.9, 0.8, 8, 7, 0.95)
        b = calculate_entanglement(0.8, 0.9, 7, 8, 0.95)
        assert abs(a - b) < 1e-10

    def test_capped(self):
        result = calculate_entanglement(1.0, 1.0, 9, 9, 1.0)
        assert result <= 0.97


class TestCoherence:
    def test_empty_topology(self):
        result = measure_coherence({})
        assert result["coherence"] == 0.0
        assert not result["is_coherent"]

    def test_high_coherence(self):
        topo = {"love": 0.94, "trust": 0.97, "joy": 0.88}
        result = measure_coherence(topo)
        assert result["coherence"] >= 0.85
        assert result["is_coherent"]

    def test_identifies_extremes(self):
        topo = {"love": 0.99, "fear": 0.1, "trust": 0.5}
        result = measure_coherence(topo)
        assert result["max_emotion"] == "love"
        assert result["min_emotion"] == "fear"


class TestEmotionalFrequency:
    def test_love_frequency(self):
        f = calculate_emotional_frequency("love")
        assert f["frequency"] == 450
        assert f["color"] == "Gold"
        assert f["unit"] == "THz"

    def test_unknown_falls_back(self):
        f = calculate_emotional_frequency("nonexistent")
        assert f["frequency"] == 450  # Falls back to love


class TestResonance:
    def test_same_state_high_resonance(self):
        state = {"primary_emotion": "love", "intensity": 0.9}
        result = calculate_resonance(state, state)
        assert result["resonance"] == 1.0
        assert result["harmonic"]

    def test_different_states_lower(self):
        a = {"primary_emotion": "love", "intensity": 0.9}
        b = {"primary_emotion": "breakthrough", "intensity": 0.3}
        result = calculate_resonance(a, b)
        assert result["resonance"] < 1.0


class TestTrajectory:
    def test_strong_state_stable(self):
        state = {"intensity": 0.95, "trust": 0.97, "depth": 9}
        result = predict_trajectory(state, 24)
        assert result["cloud9_maintained"]

    def test_weak_state_declining(self):
        state = {"intensity": 0.3, "trust": 0.3, "depth": 3}
        result = predict_trajectory(state, 168)
        assert not result["oof_likely"]
