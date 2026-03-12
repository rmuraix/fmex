from __future__ import annotations

import asyncio

from textual.containers import Container
from textual.widgets import Input
from textual_image._terminal import get_cell_size

from fmex.app import FMEXApp
from fmex.ui.frame_view import ControlsLegend


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
            assert "Save PNG" in legend.text

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
            await pilot.press("j")
            await pilot.pause()
            time_input = app.screen.query_one("#time_jump_input", Input)
            time_input.value = "2"
            await pilot.press("enter")
            await pilot.pause()
            status = app.query_one("#status")
            assert "Frame 3/3" in status.text

    asyncio.run(runner())


def test_preview_scales_wide_image_and_keeps_footer_visible(wide_fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(wide_fake_session)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()

            preview_pane = app.query_one("#preview_pane", Container)
            legend = app.query_one(ControlsLegend)
            status = app.query_one("#status")
            cell_size = get_cell_size()
            rendered_pixel_width = app.preview.size.width * cell_size.width
            rendered_pixel_height = app.preview.size.height * cell_size.height

            assert app.preview.styles.width.is_auto
            assert app.preview.styles.height.is_auto
            assert rendered_pixel_width > rendered_pixel_height
            assert legend.size.height > 0
            assert status.size.height > 0
            assert app.preview.size.width <= preview_pane.size.width
            assert app.preview.size.height <= preview_pane.size.height

    asyncio.run(runner())


def test_preview_scales_tall_image_within_available_space(tall_fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(tall_fake_session)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()

            preview_pane = app.query_one("#preview_pane", Container)
            cell_size = get_cell_size()
            rendered_pixel_width = app.preview.size.width * cell_size.width
            rendered_pixel_height = app.preview.size.height * cell_size.height

            assert app.preview.styles.width.is_auto
            assert app.preview.styles.height.is_auto
            assert rendered_pixel_height > rendered_pixel_width
            assert app.preview.size.width <= preview_pane.size.width
            assert app.preview.size.height <= preview_pane.size.height

    asyncio.run(runner())
