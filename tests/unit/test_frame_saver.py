from __future__ import annotations

from pathlib import Path

from PIL import Image

from fmex.services.frame_saver import FrameSaver


def test_frame_saver_creates_outdir_and_png(tmp_path: Path) -> None:
    outdir = tmp_path / "exports"
    saver = FrameSaver(outdir)
    image = Image.new("RGB", (8, 8), "red")
    output = saver.save_png(image, 3)

    assert output.exists()
    assert output.suffix == ".png"
    assert output.parent == outdir


def test_frame_saver_unique_names(tmp_path: Path) -> None:
    saver = FrameSaver(tmp_path)
    image = Image.new("RGB", (8, 8), "green")
    first = saver.save_png(image, 1)
    second = saver.save_png(image, 1)

    assert first != second
