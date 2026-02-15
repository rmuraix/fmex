from __future__ import annotations

from pathlib import Path

import pytest

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
