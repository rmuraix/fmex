from __future__ import annotations

from pathlib import Path

import pytest

from fmex.services import FrameBoundaryError, FrameSession


def test_contract_open_get_save_close(fake_decoder_class, tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    session = FrameSession(video_file=video, outdir=tmp_path / "exports", decoder_factory=fake_decoder_class)

    current = session.get_current_frame()
    assert current.frame_index == 0

    save_op = session.save_current_frame()
    assert save_op.output_path.exists()
    assert save_op.output_path.suffix == ".png"

    session.close()
    assert session.session.status.value == "closed"


def test_contract_next_prev_boundaries(fake_decoder_class, tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    session = FrameSession(video_file=video, outdir=tmp_path, decoder_factory=fake_decoder_class)
    session.next_frame()
    session.next_frame()
    with pytest.raises(FrameBoundaryError):
        session.next_frame()

    session.previous_frame()
    session.previous_frame()
    with pytest.raises(FrameBoundaryError):
        session.previous_frame()
