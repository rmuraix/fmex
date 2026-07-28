from __future__ import annotations

import threading
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
        # Read/written from both the main thread and background prefetch
        # workers; RLock (not Lock) because get()'s disk-cache hit path
        # reenters put() while already holding the lock.
        self._lock = threading.RLock()

    def get(self, frame_index: int) -> Image.Image | None:
        with self._lock:
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
        with self._lock:
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
        # Deliberately does not hold self._lock across the whole loop: get()
        # and put() each take the lock only for their own brief critical
        # section, so a slow fetcher() decode call in progress here never
        # blocks the main thread's own get()/put() calls on other indices.
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
