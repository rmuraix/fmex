from __future__ import annotations

import asyncio

from fmex.app import FMEXApp
from fmex.models import SessionStatus
from fmex.services import FrameBoundaryError


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


def test_app_shows_boundary_message_when_step_frames_raises(fake_session) -> None:
    def _raise_boundary(delta: int):
        raise FrameBoundaryError("Already at first frame")

    fake_session.step_frames = _raise_boundary

    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("left")
            await pilot.pause()
            status = app.query_one("#status")
            assert "Already at first frame" in status.text

    asyncio.run(runner())


def test_quit_action_closes_session_and_exits(fake_session) -> None:
    async def runner() -> None:
        app = FMEXApp(fake_session)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")

        assert fake_session.session.status == SessionStatus.CLOSED

    asyncio.run(runner())
