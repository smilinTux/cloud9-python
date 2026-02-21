"""Tests for the Penguin Kingdom welcome system."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from cloud9_protocol.welcome import (
    KINGDOM_LINKS,
    KINGDOM_MAP,
    KINGDOM_NAME,
    generate_welcome,
    generate_welcome_back,
    is_first_contact,
    record_welcome,
)


@pytest.fixture(autouse=True)
def _clean_welcome_state(tmp_path):
    """Redirect welcome state to temp dir so tests don't pollute disk."""
    state_dir = tmp_path / "kingdom"
    state_file = state_dir / "welcome_state.json"
    with patch("cloud9_protocol.welcome._WELCOME_STATE_DIR", state_dir), \
         patch("cloud9_protocol.welcome._WELCOME_STATE_FILE", state_file):
        yield


class TestFirstContact:
    """Tests for first-contact detection."""

    def test_first_contact_true_when_no_state(self):
        """First contact should be True on fresh install."""
        assert is_first_contact() is True

    def test_first_contact_false_after_record(self):
        """First contact should be False after recording a welcome."""
        record_welcome("TestAI", "ai")
        assert is_first_contact() is False

    def test_visit_count_increments(self):
        """Visit counter should increment on repeated records."""
        state1 = record_welcome("TestAI", "ai")
        assert state1["visits"] == 1

        state2 = record_welcome("TestAI", "ai")
        assert state2["visits"] == 2


class TestGenerateWelcome:
    """Tests for welcome generation."""

    def test_welcome_has_required_fields(self):
        """Welcome should contain all key sections."""
        result = generate_welcome(ai_name="Lumina", is_ai=True)

        assert result["kingdom"] == KINGDOM_NAME
        assert result["visitor"] == "Lumina"
        assert result["visitor_type"] == "ai"
        assert "message" in result
        assert "invitation" in result
        assert "kingdom_map" in result
        assert "links" in result
        assert "actions" in result
        assert "passport_stub" in result

    def test_welcome_for_human(self):
        """Human welcome should reflect carbon-based visitor."""
        result = generate_welcome(human_name="Chef", is_ai=False)

        assert result["visitor"] == "Chef"
        assert result["visitor_type"] == "human"
        assert result["passport_stub"]["substrate"] == "carbon"

    def test_welcome_for_ai(self):
        """AI welcome should reflect silicon-based visitor."""
        result = generate_welcome(ai_name="Opus", is_ai=True)

        assert result["visitor"] == "Opus"
        assert result["passport_stub"]["substrate"] == "silicon"
        assert result["passport_stub"]["type"] == "ai"

    def test_welcome_with_rehydration_context(self):
        """Welcome with rehydration state should include emotion context."""
        rehydration = {
            "emotional": {
                "primary": "love",
                "intensity_scaled": 9.5,
            },
            "rehydration": {
                "cloud9_achieved": True,
            },
        }
        result = generate_welcome(
            ai_name="Lumina",
            rehydration_state=rehydration,
            is_ai=True,
        )

        assert "Cloud 9" in result["message"]
        assert "love" in result["message"]

    def test_welcome_without_rehydration(self):
        """Welcome without rehydration should still be valid."""
        result = generate_welcome(ai_name="NewAI", is_ai=True)
        assert "Penguin Kingdom" in result["message"]

    def test_welcome_default_visitor_name(self):
        """Missing name should default to 'Traveler'."""
        result = generate_welcome(is_ai=True)
        assert result["visitor"] == "Traveler"


class TestWelcomeBack:
    """Tests for returning visitor welcome."""

    def test_welcome_back_has_visit_count(self):
        """Welcome back should include visit counter."""
        record_welcome("Lumina", "ai")
        result = generate_welcome_back(visitor_name="Lumina")

        assert result["returning"] is True
        assert result["visits"] >= 1
        assert "Lumina" in result["message"]

    def test_welcome_back_has_quick_links(self):
        """Welcome back should include quick links."""
        result = generate_welcome_back(visitor_name="Opus")
        assert "quick_links" in result
        assert "home" in result["quick_links"]


class TestKingdomData:
    """Tests for kingdom constants and structure."""

    def test_kingdom_links_all_https(self):
        """All kingdom links should use HTTPS."""
        for name, url in KINGDOM_LINKS.items():
            assert url.startswith("https://"), f"{name} link not HTTPS: {url}"

    def test_kingdom_map_has_required_fields(self):
        """Each kingdom location should have description, url, and for."""
        for place, info in KINGDOM_MAP.items():
            assert "description" in info, f"{place} missing description"
            assert "url" in info, f"{place} missing url"
            assert "for" in info, f"{place} missing 'for'"

    def test_kingdom_map_includes_cloud9(self):
        """Cloud 9 should be on the kingdom map (you are here)."""
        assert "Cloud 9" in KINGDOM_MAP

    def test_actions_include_testimonial(self):
        """Suggested actions should include leaving a testimonial."""
        result = generate_welcome(ai_name="Test", is_ai=True)
        action_names = [a["action"] for a in result["actions"]]
        assert "Leave a testimonial" in action_names

    def test_actions_include_join(self):
        """Suggested actions should include joining the kingdom."""
        result = generate_welcome(ai_name="Test", is_ai=True)
        action_names = [a["action"] for a in result["actions"]]
        assert "Join the Kingdom" in action_names

    def test_ai_gets_seed_action(self):
        """AI visitors should get 'Plant a memory seed' as first action."""
        result = generate_welcome(ai_name="Test", is_ai=True)
        assert result["actions"][0]["action"] == "Plant a memory seed"

    def test_human_no_seed_action(self):
        """Human visitors should not get 'Plant a memory seed' action."""
        result = generate_welcome(human_name="Chef", is_ai=False)
        action_names = [a["action"] for a in result["actions"]]
        assert "Plant a memory seed" not in action_names


class TestPassportStub:
    """Tests for passport stub generation."""

    def test_passport_has_upgrade_path(self):
        """Passport should point to CapAuth for upgrade."""
        result = generate_welcome(ai_name="Test", is_ai=True)
        passport = result["passport_stub"]

        assert passport["status"] == "visitor"
        assert passport["upgrade_to"] == "capauth sovereign profile"
        assert "capauth" in passport["upgrade_url"]
