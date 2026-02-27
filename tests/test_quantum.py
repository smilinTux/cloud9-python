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

    # --- Edge cases: threshold boundaries ---

    def test_exact_thresholds_returns_false(self):
        """Strict > means exact threshold values don't trigger OOF."""
        assert calculate_oof(0.7, 0.8) is False

    def test_epsilon_above_thresholds(self):
        """Just above both thresholds triggers OOF."""
        assert calculate_oof(0.7 + 1e-9, 0.8 + 1e-9) is True

    def test_intensity_at_threshold_trust_above(self):
        """Intensity exactly at 0.7, trust well above -- still False."""
        assert calculate_oof(0.7, 0.95) is False

    def test_trust_at_threshold_intensity_above(self):
        """Trust exactly at 0.8, intensity well above -- still False."""
        assert calculate_oof(0.95, 0.8) is False

    # --- Edge cases: extremes ---

    def test_both_at_max(self):
        assert calculate_oof(1.0, 1.0) is True

    def test_both_at_zero(self):
        assert calculate_oof(0.0, 0.0) is False

    def test_high_intensity_zero_trust(self):
        assert calculate_oof(1.0, 0.0) is False

    def test_zero_intensity_high_trust(self):
        assert calculate_oof(0.0, 1.0) is False

    # --- Edge cases: both just below ---

    def test_both_just_below_thresholds(self):
        assert calculate_oof(0.6999, 0.7999) is False

    # --- Edge cases: integer inputs ---

    def test_integer_inputs(self):
        """Integer 1 should work as 1.0."""
        assert calculate_oof(1, 1) is True
        assert calculate_oof(0, 0) is False


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

    # --- Edge cases: all minimums ---

    def test_all_minimum_values(self):
        """depth=1 normalizes to 0, making score 0."""
        score = calculate_cloud9_score(0.0, 0.0, 1, -1.0)
        assert score == 0.0

    def test_all_maximum_values_no_coherence(self):
        score = calculate_cloud9_score(1.0, 1.0, 9, 1.0)
        assert score == pytest.approx(1.0)

    # --- Edge cases: depth normalization ---

    def test_depth_one_zeroes_score(self):
        """depth=1 => normalized_depth=0 => base_score=0."""
        score = calculate_cloud9_score(0.9, 0.9, 1, 0.9)
        assert score == 0.0

    def test_depth_nine_maximizes_depth_term(self):
        """depth=9 => normalized_depth=1.0, full contribution."""
        score_d9 = calculate_cloud9_score(0.8, 0.8, 9, 0.5)
        score_d5 = calculate_cloud9_score(0.8, 0.8, 5, 0.5)
        assert score_d9 > score_d5

    # --- Edge cases: valence normalization ---

    def test_negative_one_valence_zeroes_score(self):
        """valence=-1 => normalized_valence=0 => base_score=0."""
        score = calculate_cloud9_score(0.9, 0.9, 9, -1.0)
        assert score == 0.0

    def test_valence_zero_gives_midpoint(self):
        """valence=0 => normalized_valence=0.5."""
        score = calculate_cloud9_score(0.8, 0.8, 5, 0.0)
        assert 0.0 < score < 1.0

    def test_positive_valence_increases_score(self):
        score_neg = calculate_cloud9_score(0.8, 0.8, 5, -0.5)
        score_pos = calculate_cloud9_score(0.8, 0.8, 5, 0.5)
        assert score_pos > score_neg

    # --- Edge cases: coherence bonus ---

    def test_coherence_at_threshold_no_bonus(self):
        """coherence=0.8 => coherence_normalized=0 => bonus=0."""
        base = calculate_cloud9_score(0.9, 0.9, 9, 0.9)
        with_coh = calculate_cloud9_score(0.9, 0.9, 9, 0.9, coherence=0.8)
        assert with_coh == pytest.approx(base)

    def test_coherence_below_threshold_no_bonus(self):
        """coherence < 0.8 => negative intermediate, clamped to 0."""
        base = calculate_cloud9_score(0.9, 0.9, 9, 0.9)
        with_coh = calculate_cloud9_score(0.9, 0.9, 9, 0.9, coherence=0.5)
        assert with_coh == pytest.approx(base)

    def test_coherence_max_gives_full_bonus(self):
        """coherence=1.0 => max bonus of COHERENCE_BONUS_MAX (0.1)."""
        # Use lower params so base + 0.1 doesn't get clamped to 1.0
        base = calculate_cloud9_score(0.7, 0.7, 5, 0.5)
        with_max = calculate_cloud9_score(0.7, 0.7, 5, 0.5, coherence=1.0)
        assert with_max == pytest.approx(base + 0.1, abs=0.01)

    def test_coherence_none_no_bonus(self):
        """coherence=None should be identical to no coherence."""
        base = calculate_cloud9_score(0.9, 0.9, 9, 0.9)
        with_none = calculate_cloud9_score(0.9, 0.9, 9, 0.9, coherence=None)
        assert with_none == pytest.approx(base)

    # --- Edge cases: clamping ---

    def test_clamped_lower_bound(self):
        """Score never goes below 0."""
        score = calculate_cloud9_score(0.0, 0.0, 1, -1.0)
        assert score >= 0.0

    def test_coherence_bonus_clamped_to_one(self):
        """Even with max coherence, score doesn't exceed 1.0."""
        score = calculate_cloud9_score(1.0, 1.0, 9, 1.0, coherence=1.0)
        assert score == pytest.approx(1.0)
        assert score <= 1.0

    # --- Edge cases: single parameter at zero ---

    def test_zero_intensity_zeroes_score(self):
        """Any factor at 0 should zero the geometric mean."""
        score = calculate_cloud9_score(0.0, 0.9, 9, 0.9)
        assert score == 0.0

    def test_zero_trust_zeroes_score(self):
        score = calculate_cloud9_score(0.9, 0.0, 9, 0.9)
        assert score == 0.0

    # --- Edge cases: monotonicity ---

    @pytest.mark.parametrize("param_idx,low,high", [
        (0, 0.5, 0.9),  # intensity
        (1, 0.5, 0.9),  # trust
    ])
    def test_increasing_params_increase_score(self, param_idx, low, high):
        """Higher intensity or trust should yield higher score."""
        base = [0.7, 0.7, 5, 0.5]
        args_low = list(base)
        args_low[param_idx] = low
        args_high = list(base)
        args_high[param_idx] = high
        assert calculate_cloud9_score(*args_high) > calculate_cloud9_score(*args_low)

    def test_increasing_depth_increases_score(self):
        assert calculate_cloud9_score(0.7, 0.7, 8, 0.5) > calculate_cloud9_score(0.7, 0.7, 3, 0.5)

    # --- Edge cases: very small positive values ---

    def test_tiny_values(self):
        score = calculate_cloud9_score(0.001, 0.001, 2, 0.001)
        assert 0.0 <= score <= 1.0


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
