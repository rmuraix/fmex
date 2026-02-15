from __future__ import annotations

from pathlib import Path

import pytest

from fmex.models import SaveStatus
from fmex.services import FrameSession, VideoDecodeError


class _FailingDecoder:
    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path

    @property
    def frame_count(self) -> int:
        return 0

    def get_frame(self, frame_index: int):  # noqa: ANN201
        raise VideoDecodeError(f"boom at frame {frame_index}")


def test_save_current_frame_passes_attempted_target_to_saver(
    fake_decoder_class, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    outdir = tmp_path / "exports"
    session = FrameSession(
        video_file=video, outdir=outdir, decoder_factory=fake_decoder_class
    )
    attempted = outdir / "attempted.png"

    monkeypatch.setattr(session.saver, "build_target", lambda _: attempted)
    monkeypatch.setattr(
        session.saver,
        "save_png",
        lambda image, frame_index, target=None: target,
    )

    result = session.save_current_frame()

    assert result.status == SaveStatus.SUCCESS
    assert result.frame_index == 0
    assert result.output_path == attempted


def test_save_current_frame_failure_uses_attempted_target(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    outdir = tmp_path / "exports"
    session = FrameSession(
        video_file=video, outdir=outdir, decoder_factory=_FailingDecoder
    )
    session.session.current_frame_index = 2
    attempted = outdir / "failed-target.png"
    session.saver.build_target = lambda _: attempted

    result = session.save_current_frame()

    assert result.status == SaveStatus.FAILURE
    assert result.frame_index == 2
    assert result.output_path == attempted
    assert result.error_message is not None
    assert "boom at frame 2" in result.error_message
