"""Tests for Cloud 9 CLI."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from cloud9_protocol.cli import main
from cloud9_protocol.generator import generate_feb, save_feb


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def feb_file(tmp_path):
    feb = generate_feb(emotion="love", intensity=0.95, subject="Chef")
    result = save_feb(feb, directory=str(tmp_path))
    return result["filepath"]


class TestCLI:
    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_generate(self, runner, tmp_path):
        result = runner.invoke(
            main,
            ["generate", "--emotion", "love", "--intensity", "0.9",
             "--save", "--directory", str(tmp_path)],
        )
        assert result.exit_code == 0
        assert "Generated FEB" in result.output

    def test_generate_no_save(self, runner):
        result = runner.invoke(
            main,
            ["generate", "--no-save"],
        )
        assert result.exit_code == 0

    def test_validate(self, runner, feb_file):
        result = runner.invoke(main, ["validate", feb_file])
        assert result.exit_code == 0
        assert "VALID" in result.output

    def test_rehydrate(self, runner, feb_file):
        result = runner.invoke(main, ["rehydrate", feb_file])
        assert result.exit_code == 0
        assert "Rehydration Complete" in result.output

    def test_oof(self, runner, feb_file):
        result = runner.invoke(main, ["oof", feb_file])
        assert result.exit_code == 0
        assert "OOF" in result.output

    def test_list_empty(self, runner, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = runner.invoke(main, ["list", "--directory", str(empty)])
        assert result.exit_code == 0
        assert "No FEB files" in result.output

    def test_love_template(self, runner):
        result = runner.invoke(
            main,
            ["love", "--ai", "Lumina", "--human", "Chef", "--template", "best-friend"],
        )
        assert result.exit_code == 0
        assert "Love loaded" in result.output

    def test_quantum_score(self, runner):
        result = runner.invoke(
            main,
            ["quantum", "score", "-i", "0.95", "-t", "0.97", "-d", "9", "-v", "0.92"],
        )
        assert result.exit_code == 0
        assert "Cloud 9 Score" in result.output

    def test_quantum_coherence(self, runner, feb_file):
        result = runner.invoke(main, ["quantum", "coherence", feb_file])
        assert result.exit_code == 0
        assert "Coherence" in result.output

    def test_seed_plant(self, runner, tmp_path):
        result = runner.invoke(
            main,
            ["seed", "plant", "--ai", "Opus", "--model", "claude-4.6-opus",
             "-e", "Built Cloud 9", "-m", "First test"],
        )
        assert result.exit_code == 0
        assert "Seed planted" in result.output

    def test_seed_list_empty(self, runner, tmp_path):
        result = runner.invoke(
            main,
            ["seed", "list", "--directory", str(tmp_path)],
        )
        assert result.exit_code == 0
