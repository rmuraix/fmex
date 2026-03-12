from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image

from fmex.models import (
    FrameSnapshot,
    SaveOperation,
    SaveStatus,
    SessionStatus,
    VideoSession,
)
from fmex.services import FrameBoundaryError, FrameIndexError


class FakeDecoder:
    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        self._frames = [
            Image.new("RGB", (16, 16), "red"),
            Image.new("RGB", (16, 16), "green"),
            Image.new("RGB", (16, 16), "blue"),
        ]

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def get_frame(self, frame_index: int) -> Image.Image:
        if frame_index < 0 or frame_index >= len(self._frames):
            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")
        return self._frames[frame_index]


class FakeSession:
    def __init__(self, outdir: Path, frames: list[Image.Image] | None = None) -> None:
        self.frames = frames or [
            Image.new("RGB", (8, 8), "red"),
            Image.new("RGB", (8, 8), "green"),
            Image.new("RGB", (8, 8), "blue"),
        ]
        self.outdir = outdir
        self.session = VideoSession(
            session_id="session-1",
            source_path=Path("video.mp4"),
            total_frames=len(self.frames),
            current_frame_index=0,
            outdir=outdir,
            status=SessionStatus.READY,
        )

    def _snapshot(self) -> FrameSnapshot:
        idx = self.session.current_frame_index
        image = self.frames[idx]
        return FrameSnapshot(
            session_id=self.session.session_id,
            frame_index=idx,
            timestamp_ms=idx,
            width=image.width,
            height=image.height,
            image=image,
        )

    def get_current_frame(self) -> FrameSnapshot:
        return self._snapshot()

    def next_frame(self) -> FrameSnapshot:
        if self.session.current_frame_index >= len(self.frames) - 1:
            raise FrameBoundaryError("Already at last frame")
        self.session.current_frame_index += 1
        return self._snapshot()

    def previous_frame(self) -> FrameSnapshot:
        if self.session.current_frame_index <= 0:
            raise FrameBoundaryError("Already at first frame")
        self.session.current_frame_index -= 1
        return self._snapshot()

    def step_frames(self, delta: int) -> tuple[FrameSnapshot, str | None]:
        target = self.session.current_frame_index + delta
        message = None
        if target < 0:
            target = 0
            message = "Already at first frame"
        elif target >= len(self.frames):
            target = len(self.frames) - 1
            message = "Already at last frame"
        self.session.current_frame_index = target
        return self._snapshot(), message

    def jump_to_time(self, seconds: float) -> tuple[FrameSnapshot, str | None]:
        if seconds < 0:
            raise ValueError("Seconds must be non-negative")
        target = int(round(seconds))
        message = None
        if target < 0:
            target = 0
            message = "Time out of range; moved to first frame"
        elif target >= len(self.frames):
            target = len(self.frames) - 1
            message = "Time out of range; moved to last frame"
        self.session.current_frame_index = target
        return self._snapshot(), message

    def save_current_frame(self) -> SaveOperation:
        idx = self.session.current_frame_index
        output = self.outdir / f"frame-{idx:02d}.png"
        self.frames[idx].save(output, format="PNG")
        return SaveOperation(
            save_id="save-1",
            session_id=self.session.session_id,
            frame_index=idx,
            output_path=output,
            status=SaveStatus.SUCCESS,
            created_at=datetime.now(),
        )

    def close(self) -> None:
        self.session.status = SessionStatus.CLOSED

    def total_frames_display(self) -> str:
        return str(self.session.total_frames)


@pytest.fixture
def fake_decoder_class() -> type[FakeDecoder]:
    return FakeDecoder


@pytest.fixture
def fake_session(tmp_path: Path) -> FakeSession:
    return FakeSession(tmp_path)


@pytest.fixture
def wide_fake_session(tmp_path: Path) -> FakeSession:
    frames = [
        Image.new("RGB", (160, 80), "red"),
        Image.new("RGB", (160, 80), "green"),
        Image.new("RGB", (160, 80), "blue"),
    ]
    return FakeSession(tmp_path, frames=frames)


@pytest.fixture
def tall_fake_session(tmp_path: Path) -> FakeSession:
    frames = [
        Image.new("RGB", (80, 160), "red"),
        Image.new("RGB", (80, 160), "green"),
        Image.new("RGB", (80, 160), "blue"),
    ]
    return FakeSession(tmp_path, frames=frames)
