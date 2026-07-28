from __future__ import annotations

from pathlib import Path

from PIL import Image

from fmex.services.frame_cache import FrameCache


def test_frame_cache_put_get() -> None:
    cache = FrameCache(max_items=2)
    image = Image.new("RGB", (4, 4), "red")
    cache.put(0, image)
    cached = cache.get(0)
    assert cached is not None
    assert cached.size == (4, 4)


def test_frame_cache_lru_eviction() -> None:
    cache = FrameCache(max_items=2)
    cache.put(0, Image.new("RGB", (1, 1), "red"))
    cache.put(1, Image.new("RGB", (1, 1), "green"))
    cache.put(2, Image.new("RGB", (1, 1), "blue"))
    assert cache.get(0) is None


def test_frame_cache_falls_back_to_disk_when_memory_evicted(tmp_path: Path) -> None:
    cache = FrameCache(max_items=1, disk_dir=tmp_path)
    cache.put(0, Image.new("RGB", (4, 4), "red"))
    cache.put(1, Image.new("RGB", (4, 4), "green"))

    cached = cache.get(0)

    assert cached is not None
    assert cached.size == (4, 4)
    cache.close()


def test_frame_cache_get_returns_none_when_disk_miss(tmp_path: Path) -> None:
    cache = FrameCache(max_items=1, disk_dir=tmp_path)

    assert cache.get(0) is None
    cache.close()
