from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image

from fmex.services.video_decoder import PyAVVideoDecoder

# 1920x1080 RGB PIL image ~= 1920 * 1080 * 3 bytes ~= 6.2MB, matching real
# HD video frames. The shared `FakeDecoder` fixture in tests/conftest.py only
# ever returns tiny 16x16 images, so it can't catch real-world memory
# regressions in the decoder's own frame cache.
FRAME_SIZE = (1920, 1080)
FRAME_BYTES = FRAME_SIZE[0] * FRAME_SIZE[1] * 3


class _FakeAVFrame:
    def __init__(self, image: Image.Image) -> None:
        self._image = image

    def to_image(self) -> Image.Image:
        return self._image


class RealisticSizePyAVDecoder:
    """Wraps a real PyAVVideoDecoder (bypassing file I/O) whose synthetic
    decode iterator lazily yields full 1080p frames one at a time, so tests
    exercise the production get_frame/eviction/seek-threshold code path with
    realistic frame sizes instead of a hand-rolled fake."""

    def __init__(
        self,
        video_path: Path,
        total_frames: int = 3000,
        max_cache: int = 32,
        seek_threshold: int = 128,
    ) -> None:
        decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
        decoder.video_path = video_path
        decoder._max_cache = max_cache
        decoder._seek_threshold = seek_threshold
        decoder._frames = deque(maxlen=max_cache)
        decoder._cache_start = 0
        decoder._container = None
        decoder._stream = None
        decoder._decoded_complete = False
        decoder._frame_count = total_frames
        decoder._fps = None
        decoder._decode_iter = self._frame_iter(total_frames)
        self._decoder = decoder

    @staticmethod
    def _frame_iter(total_frames: int):
        for index in range(total_frames):
            color = (index % 256, (index * 2) % 256, (index * 3) % 256)
            yield _FakeAVFrame(Image.new("RGB", FRAME_SIZE, color))

    @property
    def frame_count(self) -> int:
        return self._decoder.frame_count

    @property
    def has_known_frame_count(self) -> bool:
        return self._decoder.has_known_frame_count

    def get_frame(self, frame_index: int) -> Image.Image:
        return self._decoder.get_frame(frame_index)

    def close(self) -> None:
        pass
