from __future__ import annotations

import tracemalloc

import pytest

from fmex.services import FrameSession


@pytest.mark.performance
def test_memory_budget_navigation(fake_decoder_class, tmp_path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    session = FrameSession(video_file=video, outdir=tmp_path, decoder_factory=fake_decoder_class)

    tracemalloc.start()
    for _ in range(200):
        try:
            session.next_frame()
        except Exception:
            session.previous_frame()

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert peak <= 300 * 1024 * 1024
