from __future__ import annotations

from pathlib import Path

from PIL import Image

from fmex.models import FrameSnapshot, SaveOperation, SaveStatus, SessionStatus, VideoSession


def test_video_session_fields() -> None:
    session = VideoSession(
        session_id="abc",
        source_path=Path("video.mp4"),
        total_frames=10,
        current_frame_index=0,
        outdir=Path("."),
        status=SessionStatus.READY,
    )
    assert session.status == SessionStatus.READY
    assert session.total_frames == 10


def test_frame_snapshot_dimensions() -> None:
    image = Image.new("RGB", (20, 30), "red")
    snapshot = FrameSnapshot(
        session_id="abc",
        frame_index=1,
        timestamp_ms=100,
        width=image.width,
        height=image.height,
        image=image,
    )
    assert snapshot.width == 20
    assert snapshot.height == 30


def test_save_operation_success() -> None:
    op = SaveOperation(
        save_id="s1",
        session_id="abc",
        frame_index=2,
        output_path=Path("out.png"),
        status=SaveStatus.SUCCESS,
        created_at=__import__("datetime").datetime.now(),
    )
    assert op.status == SaveStatus.SUCCESS
