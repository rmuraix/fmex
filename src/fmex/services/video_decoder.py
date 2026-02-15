from __future__ import annotations

from pathlib import Path

from PIL import Image

try:
    import av
except Exception:  # pragma: no cover - environment dependent
    av = None  # type: ignore[assignment]


class VideoDecodeError(RuntimeError):
    pass


class PyAVVideoDecoder:
    """Decoder optimized for responsive stepping by decoding frames once."""

    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        self._frames: list[Image.Image] = []
        self._load()

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def _load(self) -> None:
        if av is None:
            raise VideoDecodeError("PyAV is not available in this environment")
        if not self.video_path.exists():
            raise VideoDecodeError(f"Video not found: {self.video_path}")

        try:
            with av.open(str(self.video_path)) as container:
                stream = next((s for s in container.streams if s.type == "video"), None)
                if stream is None:
                    raise VideoDecodeError("No video stream found")

                for frame in container.decode(stream):
                    self._frames.append(frame.to_image().convert("RGB"))
        except VideoDecodeError:
            raise
        except Exception as exc:  # pragma: no cover - depends on media/backend
            raise VideoDecodeError(f"Unable to decode video: {exc}") from exc

        if not self._frames:
            raise VideoDecodeError("No frames decoded from video")

    def get_frame(self, frame_index: int) -> Image.Image:
        if frame_index < 0 or frame_index >= self.frame_count:
            raise VideoDecodeError(f"Frame index out of bounds: {frame_index}")
        return self._frames[frame_index]
