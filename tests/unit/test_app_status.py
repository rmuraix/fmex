from __future__ import annotations

import asyncio

from fmex.app import FMEXApp


def test_app_status_updates(fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            status = app.query_one("#status")
            assert "Frame" in status.text
            await pilot.press("right")
            await pilot.pause()
            assert "Frame 2/3" in status.text

    asyncio.run(runner())
