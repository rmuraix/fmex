from __future__ import annotations

from pathlib import Path

import typer

from fmex.app import FMEXApp
from fmex.services import FrameSession, VideoDecodeError

cli = typer.Typer(
    add_completion=False, invoke_without_command=True, no_args_is_help=False
)


def _validate_video_path(video_file: Path) -> None:
    if not video_file.exists():
        raise typer.BadParameter(f"Video file does not exist: {video_file}")
    if not video_file.is_file():
        raise typer.BadParameter(f"Path is not a file: {video_file}")


@cli.callback()
def run(
    video_file: Path = typer.Argument(..., exists=False),
    outdir: Path | None = typer.Option(
        None, "--outdir", help="Directory for PNG exports"
    ),
) -> None:
    """Open a video in the terminal and export selected frames."""
    _validate_video_path(video_file)
    resolved_outdir = outdir if outdir is not None else Path.cwd()

    try:
        session = FrameSession(video_file=video_file, outdir=resolved_outdir)
        app = FMEXApp(session)
        app.run()
    except VideoDecodeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
