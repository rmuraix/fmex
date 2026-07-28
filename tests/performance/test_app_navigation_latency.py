from __future__ import annotations

import asyncio
import time
from pathlib import Path

import pytest
from PIL import Image

from fmex.app import FMEXApp
from fmex.services import FrameSession

DECODE_DELAY_SECONDS = 0.05


class _SlowDecoder:
    """Fake decoder that simulates a real ffmpeg decode cost, so latency
    assertions are meaningful (the shared FakeDecoder fixture returns frames
    instantly and would never expose a blocking-UI regression)."""

    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        self._total = 500

    @property
    def frame_count(self) -> int:
        return self._total

    def get_frame(self, frame_index: int) -> Image.Image:
        if frame_index < 0 or frame_index >= self._total:
            from fmex.services.video_decoder import FrameIndexError

            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")
        time.sleep(DECODE_DELAY_SECONDS)
        return Image.new("RGB", (4, 4), (frame_index % 256, 0, 0))


@pytest.mark.performance
def test_keypress_latency_is_not_doubled_by_synchronous_prefetch(
    tmp_path: Path,
) -> None:
    """With prefetch moved to a background worker, a single navigation
    keypress should cost roughly one decode (the current frame), not three
    (current frame + two synchronously-prefetched neighbors)."""
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")

    async def runner() -> None:
        session = FrameSession(
            video_file=video, outdir=tmp_path, decoder_factory=_SlowDecoder
        )
        session.session.current_frame_index = 10
        app = FMEXApp(session)
        async with app.run_test() as pilot:
            await pilot.pause()
            await app.workers.wait_for_complete()

            start = time.perf_counter()
            await pilot.press("right")
            await pilot.pause()
            elapsed = time.perf_counter() - start

            # Old synchronous-prefetch behavior would cost ~3x a single
            # decode (current frame + 2 neighbors) before returning control;
            # allow generous headroom above a single decode while still
            # catching a regression back to the fully-synchronous path.
            assert elapsed < DECODE_DELAY_SECONDS * 2.5

            await app.workers.wait_for_complete()
            assert session.cache.get(12) is not None
            assert session.cache.get(10) is not None

    asyncio.run(runner())
