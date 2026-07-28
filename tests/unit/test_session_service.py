from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from fmex.models import SaveStatus
from fmex.services import (
    FrameBoundaryError,
    FrameIndexError,
    FrameSession,
    VideoDecodeError,
)


class _FailingDecoder:
    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path

    @property
    def frame_count(self) -> int:
        return 0

    def get_frame(self, frame_index: int):  # noqa: ANN201
        raise VideoDecodeError(f"boom at frame {frame_index}")


class _UnknownCountDecoder:
    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        from PIL import Image

        self._frames = [
            Image.new("RGB", (8, 8), "red"),
            Image.new("RGB", (8, 8), "green"),
            Image.new("RGB", (8, 8), "blue"),
        ]

    @property
    def frame_count(self) -> int:
        return 1

    @property
    def has_known_frame_count(self) -> bool:
        return False

    def frame_index_for_seconds(self, seconds: float) -> int:
        return int(round(seconds))

    def get_frame(self, frame_index: int):  # noqa: ANN201
        if frame_index < 0 or frame_index >= len(self._frames):
            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")
        return self._frames[frame_index]


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


def test_step_frames_does_not_set_unknown_total_frames(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    outdir = tmp_path / "exports"
    session = FrameSession(
        video_file=video, outdir=outdir, decoder_factory=_UnknownCountDecoder
    )
    session.session.total_frames = 0
    session.session.current_frame_index = 0

    snap, message = session.step_frames(-10)

    assert snap.frame_index == 0
    assert message == "Already at first frame"
    assert session.session.total_frames == 0


def test_jump_to_time_with_unknown_total_frames(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    outdir = tmp_path / "exports"
    session = FrameSession(
        video_file=video, outdir=outdir, decoder_factory=_UnknownCountDecoder
    )
    session.session.total_frames = 0

    snap, message = session.jump_to_time(2)

    assert snap.frame_index == 2
    assert message is None
    assert session.session.total_frames == 0


def test_jump_to_time_out_of_range_with_unknown_total_frames(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    outdir = tmp_path / "exports"
    session = FrameSession(
        video_file=video, outdir=outdir, decoder_factory=_UnknownCountDecoder
    )
    session.session.total_frames = 0

    with pytest.raises(FrameBoundaryError):
        session.jump_to_time(10)


def test_navigation_methods_do_not_auto_prefetch(
    fake_decoder_class, tmp_path: Path
) -> None:
    """Prefetching must be opt-in (triggered by the caller, e.g. a background
    worker) so navigation's critical path never blocks on speculative decode
    of neighboring frames."""
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    session = FrameSession(
        video_file=video, outdir=tmp_path, decoder_factory=fake_decoder_class
    )
    session.prefetch_neighbors = Mock()

    session.step_frames(1)
    session.next_frame()
    session.previous_frame()

    session.prefetch_neighbors.assert_not_called()
