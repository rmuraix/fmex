from __future__ import annotations

import time

import pytest

from fmex.services import FrameSession


@pytest.mark.performance
def test_navigation_latency_p95(fake_decoder_class, tmp_path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    session = FrameSession(
        video_file=video, outdir=tmp_path, decoder_factory=fake_decoder_class
    )
    timings = []
    for _ in range(30):
        start = time.perf_counter()
        try:
            session.next_frame()
        except Exception:
            session.previous_frame()
        timings.append((time.perf_counter() - start) * 1000)

    sorted_timings = sorted(timings)
    p95 = sorted_timings[int(len(sorted_timings) * 0.95) - 1]
    assert p95 <= 120.0
