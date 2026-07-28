from __future__ import annotations

import tracemalloc
from functools import partial

import pytest

from fmex.services import FrameSession

from conftest import FRAME_BYTES, RealisticSizePyAVDecoder


@pytest.mark.performance
def test_memory_budget_navigation_realistic_1080p(tmp_path) -> None:
    """Regression guard for the decoder/FrameCache double-caching fix.

    Uses a synthetic decoder that yields real 1920x1080 frames (~6.2MB each)
    through the production PyAVVideoDecoder.get_frame code path, instead of
    the shared FakeDecoder's tiny 16x16 images which can't catch real-world
    memory regressions.
    """
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    session = FrameSession(
        video_file=video,
        outdir=tmp_path,
        decoder_factory=RealisticSizePyAVDecoder,
    )

    tracemalloc.start()
    for i in range(300):
        try:
            if i % 25 == 0:
                session.step_frames(100)
            elif i % 5 == 0:
                session.step_frames(10)
            else:
                session.next_frame()
        except Exception:
            session.previous_frame()

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Budget derived from the current defaults: PyAVVideoDecoder's own frame
    # cache (max_cache=32) plus FrameCache's LRU cache (max_items=64, see
    # FrameSession.__post_init__ in session_service.py), each holding up to
    # a full 1080p frame, with a 1.5x safety margin for transient copies.
    budget = int((32 + 64) * FRAME_BYTES * 1.5)
    assert peak <= budget


@pytest.mark.performance
def test_decoder_cache_default_uses_far_less_memory_than_old_default(
    tmp_path,
) -> None:
    """Guards against silently reverting PyAVVideoDecoder's max_cache back to
    its old value of 256, which allowed ~8x more full-resolution frames to be
    retained in the decoder's own cache alone."""
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    def _navigate(decoder_factory) -> int:
        session = FrameSession(
            video_file=video, outdir=tmp_path, decoder_factory=decoder_factory
        )
        tracemalloc.start()
        for _ in range(300):
            try:
                session.next_frame()
            except Exception:
                session.previous_frame()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return peak

    new_default_peak = _navigate(RealisticSizePyAVDecoder)
    old_default_peak = _navigate(partial(RealisticSizePyAVDecoder, max_cache=256))

    assert new_default_peak < old_default_peak / 2
