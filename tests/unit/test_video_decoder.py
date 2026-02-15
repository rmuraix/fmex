from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from PIL import Image

from fmex.services.video_decoder import (
    FrameIndexError,
    PyAVVideoDecoder,
    VideoDecodeError,
)


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


def test_has_known_frame_count_returns_false_when_frame_count_is_zero() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frame_count = 0

    assert not decoder.has_known_frame_count


def test_has_known_frame_count_returns_true_when_frame_count_is_positive() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frame_count = 10

    assert decoder.has_known_frame_count


def test_fps_property_returns_fps() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = 30.0

    assert decoder.fps == 30.0


def test_fps_property_returns_none_when_not_set() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = None

    assert decoder.fps is None


def test_frame_index_for_seconds_raises_on_negative_seconds() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = 30.0

    with pytest.raises(ValueError, match="Seconds must be non-negative"):
        decoder.frame_index_for_seconds(-1.0)


def test_frame_index_for_seconds_raises_when_fps_is_none() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = None

    with pytest.raises(VideoDecodeError, match="FPS is unavailable"):
        decoder.frame_index_for_seconds(1.0)


def test_frame_index_for_seconds_converts_correctly() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = 30.0

    assert decoder.frame_index_for_seconds(0.0) == 0
    assert decoder.frame_index_for_seconds(1.0) == 30
    assert decoder.frame_index_for_seconds(2.5) == 75


def test_open_raises_when_pyav_is_not_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import fmex.services.video_decoder as module

    monkeypatch.setattr(module, "av", None)
    with pytest.raises(VideoDecodeError, match="PyAV is not available"):
        PyAVVideoDecoder(tmp_path / "video.mp4")


def test_get_frame_returns_from_cache_when_in_range() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    green_image = Image.new("RGB", (2, 2), (0, 255, 0))
    decoder._frames = [
        Image.new("RGB", (2, 2), (255, 0, 0)),
        green_image,
    ]
    decoder._cache_start = 5
    decoder._frame_count = 10
    decoder._max_cache = 10

    image = decoder.get_frame(6)

    assert image is green_image


def test_get_frame_seeks_forward_when_beyond_max_cache() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frames = [Image.new("RGB", (2, 2), "red")]
    decoder._cache_start = 0
    decoder._max_cache = 2
    decoder._frame_count = 100
    decoder._decoded_complete = False
    decoder._decode_iter = iter([])

    expected = Image.new("RGB", (2, 2), "blue")

    def _seek_to_frame(frame_index: int) -> bool:
        decoder._frames = [expected]
        decoder._cache_start = frame_index
        return True

    decoder._seek_to_frame = _seek_to_frame

    image = decoder.get_frame(50)

    assert image is expected


def test_get_frame_decodes_with_pts_calculation() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frames = []
    decoder._cache_start = 0
    decoder._max_cache = 10
    decoder._frame_count = 0
    decoder._decoded_complete = False
    decoder._fps = 30.0
    decoder._stream = Mock()
    decoder._stream.time_base = 1 / 30.0
    decoder._container = None

    class FrameWithPTS:
        pts = 30
        time_base = 1 / 30.0

        def to_image(self):
            return Image.new("RGB", (2, 2), "red")

    decoder._decode_iter = iter([FrameWithPTS()])

    image = decoder.get_frame(30)

    assert decoder._cache_start == 30
    assert image.getpixel((0, 0)) == (255, 0, 0)


def test_get_frame_raises_when_decode_complete_and_out_of_bounds() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frames = [Image.new("RGB", (2, 2), "red")]
    decoder._cache_start = 0
    decoder._max_cache = 10
    decoder._frame_count = 0
    decoder._decoded_complete = True
    decoder._decode_iter = iter([])

    with pytest.raises(FrameIndexError, match="Frame index out of bounds"):
        decoder.get_frame(10)


def test_get_frame_raises_when_decode_iter_is_none() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    decoder._frames = []
    decoder._cache_start = 5
    decoder._max_cache = 10
    decoder._frame_count = 0
    decoder._decoded_complete = False
    decoder._decode_iter = None
    decoder._container = None
    decoder._stream = None
    decoder._fps = None

    def _reset_decode():
        pass

    decoder._reset_decode = _reset_decode

    with pytest.raises(FrameIndexError, match="Frame index out of bounds"):
        decoder.get_frame(2)


def test_frame_index_from_pts_returns_cache_start_when_no_fps() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = None
    decoder._cache_start = 10

    result = decoder._frame_index_from_pts(100, Mock())

    assert result == 10


def test_frame_index_from_pts_returns_cache_start_when_no_time_base() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = 30.0
    decoder._cache_start = 10

    result = decoder._frame_index_from_pts(100, None)

    assert result == 10


def test_frame_index_from_pts_converts_correctly() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._fps = 30.0
    decoder._cache_start = 0

    result = decoder._frame_index_from_pts(30, 1 / 30.0)

    assert result == 30


def test_seek_to_frame_returns_false_when_no_container() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = None
    decoder._stream = Mock()
    decoder._fps = 30.0

    result = decoder._seek_to_frame(10)

    assert result is False


def test_seek_to_frame_returns_false_when_no_stream() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = Mock()
    decoder._stream = None
    decoder._fps = 30.0

    result = decoder._seek_to_frame(10)

    assert result is False


def test_seek_to_frame_returns_false_when_no_fps() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = Mock()
    decoder._stream = Mock()
    decoder._fps = None

    result = decoder._seek_to_frame(10)

    assert result is False


def test_seek_to_frame_returns_false_when_no_time_base() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = Mock()
    decoder._stream = Mock()
    decoder._stream.time_base = None
    decoder._fps = 30.0

    result = decoder._seek_to_frame(10)

    assert result is False


def test_seek_to_frame_returns_false_on_exception() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = Mock()
    decoder._container.seek.side_effect = Exception("Seek failed")
    decoder._stream = Mock()
    decoder._stream.time_base = 1 / 30.0
    decoder._fps = 30.0

    result = decoder._seek_to_frame(10)

    assert result is False


def test_seek_to_frame_succeeds_and_resets_cache() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = Mock()
    decoder._stream = Mock()
    decoder._stream.time_base = 1 / 30.0
    decoder._fps = 30.0
    decoder._frames = [Image.new("RGB", (2, 2), "red")]
    decoder._cache_start = 10
    decoder._decoded_complete = True
    decoder._container.decode.return_value = iter([])

    result = decoder._seek_to_frame(20)

    assert result is True
    assert decoder._frames == []
    assert decoder._cache_start == 0
    assert decoder._decoded_complete is False
    decoder._container.seek.assert_called_once()


def test_infer_frame_count_returns_zero_when_no_stream() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = None
    decoder._container = Mock()

    result = decoder._infer_frame_count()

    assert result == 0


def test_infer_frame_count_returns_zero_when_no_container() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._container = None

    result = decoder._infer_frame_count()

    assert result == 0


def test_infer_frame_count_returns_stream_frames_when_available() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._stream.frames = 100
    decoder._container = Mock()

    result = decoder._infer_frame_count()

    assert result == 100


def test_infer_frame_count_uses_stream_duration_and_rate() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._stream.frames = 0
    decoder._stream.duration = 3000
    decoder._stream.time_base = 1 / 1000.0
    decoder._stream.average_rate = 30.0
    decoder._container = Mock()

    result = decoder._infer_frame_count()

    assert result == 90


def test_infer_frame_count_uses_container_duration_and_rate() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._stream.frames = 0
    decoder._stream.duration = None
    decoder._stream.average_rate = 30.0
    decoder._container = Mock()
    decoder._container.duration = 3_000_000

    result = decoder._infer_frame_count()

    assert result == 90


def test_infer_frame_count_returns_zero_when_no_info() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._stream.frames = 0
    decoder._stream.duration = None
    decoder._stream.average_rate = None
    decoder._container = Mock()
    decoder._container.duration = None

    result = decoder._infer_frame_count()

    assert result == 0


def test_reset_decode_closes_container_and_reopens() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    container_mock = Mock()
    decoder._container = container_mock
    decoder._frames = [Image.new("RGB", (2, 2), "red")]
    decoder._cache_start = 10
    decoder._decoded_complete = True

    def _open():
        decoder._frames = []
        decoder._cache_start = 0
        decoder._decoded_complete = False
        decoder._decode_iter = iter([])
        decoder._container = Mock()
        decoder._stream = Mock()

    decoder._open = _open

    decoder._reset_decode()

    container_mock.close.assert_called_once()
    assert decoder._frames == []
    assert decoder._cache_start == 0
    assert decoder._decoded_complete is False


def test_close_closes_container_and_clears_references() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    container_mock = Mock()
    decoder._container = container_mock
    decoder._stream = Mock()
    decoder._decode_iter = iter([])

    decoder.close()

    container_mock.close.assert_called_once()
    assert decoder._container is None
    assert decoder._stream is None
    assert decoder._decode_iter is None


def test_close_does_nothing_when_container_is_none() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._container = None
    decoder._stream = Mock()
    decoder._decode_iter = iter([])

    decoder.close()

    assert decoder._container is None


def test_frame_count_property_uses_fallback_when_frame_count_is_zero() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frame_count = 0
    decoder._frames = [Image.new("RGB", (2, 2), "red"), Image.new("RGB", (2, 2), "green")]
    decoder._cache_start = 10

    assert decoder.frame_count == 12


def test_get_frame_raises_when_frame_index_exceeds_known_frame_count() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._frames = []
    decoder._cache_start = 0
    decoder._max_cache = 10
    decoder._frame_count = 5
    decoder._decoded_complete = False
    decoder._decode_iter = iter([])

    with pytest.raises(FrameIndexError, match="Frame index out of bounds"):
        decoder.get_frame(10)


def test_get_frame_seeks_backward_and_falls_back_to_reset() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    decoder._frames = [Image.new("RGB", (2, 2), "green")]
    decoder._cache_start = 10
    decoder._max_cache = 10
    decoder._frame_count = 0
    decoder._decoded_complete = False
    decoder._decode_iter = iter([])

    expected = Image.new("RGB", (2, 2), "red")
    seek_called = False

    def _seek_to_frame(frame_index: int) -> bool:
        nonlocal seek_called
        seek_called = True
        return False

    def _reset_decode() -> None:
        decoder._frames = [expected]
        decoder._cache_start = 0
        decoder._decoded_complete = False
        decoder._decode_iter = iter([])

    decoder._seek_to_frame = _seek_to_frame
    decoder._reset_decode = _reset_decode

    image = decoder.get_frame(0)

    assert seek_called
    assert image is expected


def test_infer_frame_count_with_invalid_stream_duration() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._stream.frames = 0
    decoder._stream.duration = -100
    decoder._stream.time_base = 1 / 1000.0
    decoder._stream.average_rate = 30.0
    decoder._container = Mock()
    decoder._container.duration = None

    result = decoder._infer_frame_count()

    assert result == 0


def test_infer_frame_count_with_invalid_container_duration() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder._stream = Mock()
    decoder._stream.frames = 0
    decoder._stream.duration = None
    decoder._stream.average_rate = 30.0
    decoder._container = Mock()
    decoder._container.duration = -1_000_000

    result = decoder._infer_frame_count()

    assert result == 0


def test_reset_decode_when_container_is_none() -> None:
    decoder = PyAVVideoDecoder.__new__(PyAVVideoDecoder)
    decoder.video_path = Path("dummy.mp4")
    decoder._container = None
    decoder._frames = [Image.new("RGB", (2, 2), "red")]
    decoder._cache_start = 10
    decoder._decoded_complete = True

    def _open():
        decoder._frames = []
        decoder._cache_start = 0
        decoder._decoded_complete = False
        decoder._decode_iter = iter([])

    decoder._open = _open

    decoder._reset_decode()

    assert decoder._frames == []
    assert decoder._cache_start == 0
    assert decoder._decoded_complete is False
