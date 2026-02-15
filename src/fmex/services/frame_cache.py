from __future__ import annotations

from collections import OrderedDict
from io import BytesIO
from pathlib import Path

from PIL import Image

try:
    from diskcache import Cache
except Exception:  # pragma: no cover - optional backend failure
    Cache = None  # type: ignore[misc,assignment]


class FrameCache:
    def __init__(self, max_items: int = 64, disk_dir: Path | None = None) -> None:
        self.max_items = max_items
        self._memory: OrderedDict[int, Image.Image] = OrderedDict()
        self._disk = Cache(str(disk_dir)) if (disk_dir and Cache is not None) else None

    def get(self, frame_index: int) -> Image.Image | None:
        if frame_index in self._memory:
            image = self._memory.pop(frame_index)
            self._memory[frame_index] = image
            return image

        if self._disk is not None:
            payload = self._disk.get(frame_index)
            if payload is None:
                return None
            image = Image.open(BytesIO(payload)).copy()
            self.put(frame_index, image)
            return image

        return None

    def put(self, frame_index: int, image: Image.Image) -> None:
        if frame_index in self._memory:
            self._memory.pop(frame_index)
        self._memory[frame_index] = image
        while len(self._memory) > self.max_items:
            self._memory.popitem(last=False)

        if self._disk is not None:
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            self._disk[frame_index] = buffer.getvalue()

    def prefetch(self, indices: list[int], fetcher: callable) -> None:
        for idx in indices:
            if idx < 0 or self.get(idx) is not None:
                continue
            try:
                image = fetcher(idx)
            except Exception:
                continue
            self.put(idx, image)

    def close(self) -> None:
        if self._disk is not None:
            self._disk.close()
