"""CLI surface tests. Agent is not exercised here (that's E2E)."""
import pytest
from click.testing import CliRunner

from crpg.cli import main


def test_cli_help():
    runner = CliRunner()
    r = runner.invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "generate" in r.output


def test_cli_generate_requires_brief():
    runner = CliRunner()
    r = runner.invoke(main, ["generate"])
    assert r.exit_code != 0
    assert "--brief" in r.output or "Missing option" in r.output


def test_cli_generate_help_shows_both_input_modes():
    """Help text must explain that --brief accepts a file path OR raw text."""
    runner = CliRunner()
    r = runner.invoke(main, ["generate", "--help"])
    assert r.exit_code == 0
    # Must mention both inline text and file
    assert "path" in r.output.lower() or "file" in r.output.lower()
    assert "text" in r.output.lower() or "inline" in r.output.lower() or "paragraph" in r.output.lower()
