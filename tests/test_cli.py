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


def test_cli_generate_missing_file(tmp_path):
    runner = CliRunner()
    r = runner.invoke(main, ["generate", "--brief", str(tmp_path / "nope.md"),
                             "--out", str(tmp_path / "bundle")])
    assert r.exit_code != 0
