from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image

from fmex.models import FrameSnapshot, SaveOperation, SaveStatus, SessionStatus, VideoSession
from fmex.services import FrameBoundaryError


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
        return self._frames[frame_index]


class FakeSession:
    def __init__(self, outdir: Path) -> None:
        self.frames = [
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


@pytest.fixture
def fake_decoder_class() -> type[FakeDecoder]:
    return FakeDecoder


@pytest.fixture
def fake_session(tmp_path: Path) -> FakeSession:
    return FakeSession(tmp_path)
