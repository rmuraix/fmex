from __future__ import annotations

import asyncio

from fmex.app import FMEXApp
from fmex.ui.frame_view import ControlsLegend
from textual.widgets import Input


def test_keyboard_navigation_and_status(fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            status = app.query_one("#status")
            assert "Frame 1/3" in status.text

            await pilot.press("right")
            await pilot.pause()
            assert "Frame 2/3" in status.text

            await pilot.press("left")
            await pilot.pause()
            assert "Frame 1/3" in status.text

    asyncio.run(runner())


def test_control_legend_visible(fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            legend = app.query_one(ControlsLegend)
            assert "save PNG" in legend.text

    asyncio.run(runner())


def test_modifier_step_keys(fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            status = app.query_one("#status")
            assert "Frame 1/3" in status.text

            await pilot.press("ctrl+right")
            await pilot.pause()
            assert "Frame 3/3" in status.text

            await pilot.press("shift+left")
            await pilot.pause()
            assert "Frame 1/3" in status.text

    asyncio.run(runner())


def test_time_jump_modal(fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("t")
            await pilot.pause()
            time_input = app.screen.query_one("#time_jump_input", Input)
            time_input.value = "2"
            await pilot.press("enter")
            await pilot.pause()
            status = app.query_one("#status")
            assert "Frame 3/3" in status.text

    asyncio.run(runner())
