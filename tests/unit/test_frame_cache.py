from __future__ import annotations

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
