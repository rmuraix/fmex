from __future__ import annotations

import threading
import time
from pathlib import Path

from PIL import Image

from fmex.services import FrameSession


class _SlowNonReentrantDecoder:
    """Fake decoder whose get_frame sleeps briefly and records any
    re-entrant call, i.e. a second get_frame() starting before the first
    one returns. Used to verify FrameSession serializes decoder access
    across the main thread and a background prefetch thread."""

    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        self._guard = threading.Lock()
        self.reentrant_calls = 0

    @property
    def frame_count(self) -> int:
        return 100_000

    def get_frame(self, frame_index: int) -> Image.Image:
        if not self._guard.acquire(blocking=False):
            self.reentrant_calls += 1
            self._guard.acquire()
        try:
            time.sleep(0.01)
            return Image.new("RGB", (2, 2), "red")
        finally:
            self._guard.release()


def test_prefetch_and_navigation_do_not_race_on_decoder(tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    session = FrameSession(
        video_file=video, outdir=tmp_path, decoder_factory=_SlowNonReentrantDecoder
    )

    stop = threading.Event()

    def _prefetch_loop() -> None:
        while not stop.is_set():
            session.prefetch_neighbors()

    prefetch_thread = threading.Thread(target=_prefetch_loop)
    prefetch_thread.start()
    try:
        for _ in range(30):
            session.step_frames(1)
    finally:
        stop.set()
        prefetch_thread.join(timeout=5)

    assert session.decoder.reentrant_calls == 0
