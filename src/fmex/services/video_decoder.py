from __future__ import annotations

from pathlib import Path

from PIL import Image

try:
    import av
except Exception:  # pragma: no cover - environment dependent
    av = None  # type: ignore[assignment]


class VideoDecodeError(RuntimeError):
    pass


class FrameIndexError(VideoDecodeError):
    pass


class PyAVVideoDecoder:
    """Lazy decoder optimized for fast startup and on-demand frame access."""

    def __init__(self, video_path: Path, max_cache: int = 256) -> None:
        self.video_path = video_path
        self._max_cache = max_cache
        self._frames: list[Image.Image] = []
        self._cache_start = 0
        self._container = None
        self._stream = None
        self._decode_iter = None
        self._decoded_complete = False
        self._frame_count = 0
        self._open()

    @property
    def frame_count(self) -> int:
        frame_count = getattr(self, "_frame_count", 0)
        if frame_count:
            return frame_count
        frames = getattr(self, "_frames", [])
        cache_start = getattr(self, "_cache_start", 0)
        return cache_start + len(frames)

    def _open(self) -> None:
        if av is None:
            raise VideoDecodeError("PyAV is not available in this environment")
        if not self.video_path.exists():
            raise VideoDecodeError(f"Video not found: {self.video_path}")

        try:
            self._container = av.open(str(self.video_path))
            self._stream = next(
                (s for s in self._container.streams if s.type == "video"), None
            )
            if self._stream is None:
                raise VideoDecodeError("No video stream found")
            self._frame_count = self._infer_frame_count()
            self._decode_iter = self._container.decode(self._stream)
        except VideoDecodeError:
            raise
        except Exception as exc:  # pragma: no cover - depends on media/backend
            raise VideoDecodeError(f"Unable to decode video: {exc}") from exc

    def get_frame(self, frame_index: int) -> Image.Image:
        frames = getattr(self, "_frames", [])
        decode_iter = getattr(self, "_decode_iter", None)
        decoded_complete = getattr(self, "_decoded_complete", False)
        frame_count = getattr(self, "_frame_count", 0)
        cache_start = getattr(self, "_cache_start", 0)
        max_cache = max(1, int(getattr(self, "_max_cache", 1)))
        if frame_index < 0:
            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")
        if frame_count and frame_index >= frame_count:
            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")
        cache_end = cache_start + len(frames)
        if cache_start <= frame_index < cache_end:
            return frames[frame_index - cache_start]
        if frame_index < cache_start:
            self._reset_decode()
            frames = self._frames
            decode_iter = self._decode_iter
            decoded_complete = self._decoded_complete
            cache_start = self._cache_start
            cache_end = cache_start + len(frames)
            if cache_start <= frame_index < cache_end:
                return frames[frame_index - cache_start]
        if decode_iter is None:
            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")

        while (cache_start + len(frames)) <= frame_index and not decoded_complete:
            try:
                frame = next(decode_iter)
            except StopIteration:
                decoded_complete = True
                self._decoded_complete = True
                break
            except Exception as exc:  # pragma: no cover - backend/media dependent
                raise VideoDecodeError(f"Unable to decode frame: {exc}") from exc
            frames.append(frame.to_image().convert("RGB"))
            if len(frames) > max_cache:
                frames.pop(0)
                cache_start += 1
                self._cache_start = cache_start
            self._frames = frames

        cache_end = cache_start + len(frames)
        if cache_start <= frame_index < cache_end:
            return frames[frame_index - cache_start]

        if decoded_complete:
            self._frame_count = cache_start + len(frames)
            raise FrameIndexError(f"Frame index out of bounds: {frame_index}")

        raise VideoDecodeError(f"Unable to decode frame: {frame_index}")

    def _infer_frame_count(self) -> int:
        if self._stream is None or self._container is None:
            return 0
        if self._stream.frames:
            return int(self._stream.frames)
        if self._stream.duration and self._stream.average_rate:
            seconds = float(self._stream.duration * self._stream.time_base)
            fps = float(self._stream.average_rate)
            if seconds > 0 and fps > 0:
                return max(1, int(round(seconds * fps)))
        if self._container.duration and self._stream.average_rate:
            seconds = float(self._container.duration) / 1_000_000.0
            fps = float(self._stream.average_rate)
            if seconds > 0 and fps > 0:
                return max(1, int(round(seconds * fps)))
        return 0

    def _reset_decode(self) -> None:
        if self._container is not None:
            self._container.close()
        self._frames = []
        self._cache_start = 0
        self._decoded_complete = False
        self._decode_iter = None
        self._container = None
        self._stream = None
        self._open()

    def close(self) -> None:
        if self._container is not None:
            self._container.close()
            self._container = None
            self._stream = None
            self._decode_iter = None
