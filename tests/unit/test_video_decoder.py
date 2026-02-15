from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from fmex.services.video_decoder import PyAVVideoDecoder, VideoDecodeError


def test_decoder_bounds() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    decoder._frames = [object(), object()]

    assert decoder.frame_count == 2
    with pytest.raises(VideoDecodeError):
        decoder.get_frame(-1)
    with pytest.raises(VideoDecodeError):
        decoder.get_frame(2)


def test_decoder_missing_file_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import fmex.services.video_decoder as module

    monkeypatch.setattr(module, "av", object())
    with pytest.raises(VideoDecodeError):
        PyAVVideoDecoder(tmp_path / "missing.mp4")


class _FakeAVFrame:
    def __init__(self, image: Image.Image) -> None:
        self._image = image

    def to_image(self) -> Image.Image:
        return self._image


def test_decoder_cache_window_advances_and_updates_frame_count() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    decoder._max_cache = 2
    decoder._frames = []
    decoder._cache_start = 0
    decoder._container = None
    decoder._stream = None
    decoder._decoded_complete = False
    decoder._frame_count = 0
    decoder._decode_iter = iter(
        [
            _FakeAVFrame(Image.new("RGB", (2, 2), "red")),
            _FakeAVFrame(Image.new("RGB", (2, 2), "green")),
            _FakeAVFrame(Image.new("RGB", (2, 2), "blue")),
        ]
    )

    image = decoder.get_frame(2)

    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert decoder._cache_start == 1
    assert len(decoder._frames) == 2
    assert decoder.frame_count == 3


def test_decoder_resets_when_requesting_frame_before_cache_start() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    decoder._max_cache = 2
    decoder._frames = [
        Image.new("RGB", (2, 2), "green"),
        Image.new("RGB", (2, 2), "blue"),
    ]
    decoder._cache_start = 1
    decoder._container = None
    decoder._stream = None
    decoder._decoded_complete = False
    decoder._frame_count = 0
    decoder._decode_iter = iter(())

    expected = Image.new("RGB", (2, 2), "red")

    def _reset_decode() -> None:
        decoder._frames = [expected]
        decoder._cache_start = 0
        decoder._decoded_complete = True
        decoder._decode_iter = iter(())

    decoder._reset_decode = _reset_decode

    image = decoder.get_frame(0)

    assert image is expected
