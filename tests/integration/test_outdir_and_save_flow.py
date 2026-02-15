from __future__ import annotations

from pathlib import Path

from fmex.services import FrameSession


def test_outdir_autocreate_and_save(fake_decoder_class, tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake")
    outdir = tmp_path / "nested" / "exports"

    session = FrameSession(
        video_file=video, outdir=outdir, decoder_factory=fake_decoder_class
    )
    result = session.save_current_frame()

    assert outdir.exists()
    assert result.output_path.exists()
    assert result.output_path.parent == outdir
