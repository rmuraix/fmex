from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fmex.cli import cli

runner = CliRunner()


def test_cli_missing_video_error() -> None:
    result = runner.invoke(cli, ["missing.mp4"])
    assert result.exit_code != 0


def test_cli_non_file_error(tmp_path: Path) -> None:
    result = runner.invoke(cli, [str(tmp_path)])
    assert result.exit_code != 0
