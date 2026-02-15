from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image


class FrameSaveError(RuntimeError):
    pass


class FrameSaver:
    def __init__(self, outdir: Path) -> None:
        self.outdir = outdir

    def ensure_outdir(self) -> Path:
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise FrameSaveError(f"Failed to create output directory '{self.outdir}': {exc}") from exc

        if not self.outdir.is_dir():
            raise FrameSaveError(f"Output path is not a directory: {self.outdir}")
        return self.outdir

    def build_filename(self, frame_index: int) -> str:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        suffix = uuid4().hex[:8]
        return f"frame-{frame_index:06d}-{stamp}-{suffix}.png"

    def save_png(self, image: Image.Image, frame_index: int) -> Path:
        outdir = self.ensure_outdir()
        target = outdir / self.build_filename(frame_index)

        try:
            image.save(target, format="PNG")
        except Exception as exc:
            raise FrameSaveError(f"Failed to save PNG '{target}': {exc}") from exc

        return target
