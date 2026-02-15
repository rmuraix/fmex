from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual_image.widget import SixelImage

from fmex.models import SaveStatus
from fmex.services import FrameBoundaryError, FrameSession
from fmex.ui.frame_view import StatusLine, build_footer_widgets


class FMEXApp(App[None]):
    BINDINGS = [
        Binding("right", "next_frame", "Next"),
        Binding("left", "prev_frame", "Prev"),
        Binding("l", "next_frame", "Next"),
        Binding("h", "prev_frame", "Prev"),
        Binding("s", "save_frame", "Save"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, session: FrameSession) -> None:
        super().__init__()
        self.session = session
        self.preview = SixelImage(id="preview")
        self.status = StatusLine("Initializing", id="status")

    def compose(self) -> ComposeResult:
        yield Vertical(self.preview, *build_footer_widgets(), self.status)

    def _fit_preview_to_terminal(self) -> None:
        width = max(1, self.size.width)
        height = max(4, self.size.height - 2)
        self.preview.styles.width = width
        self.preview.styles.height = height

    def on_mount(self) -> None:
        self._fit_preview_to_terminal()
        snap = self.session.get_current_frame()
        self.preview.image = snap.image
        self._set_status(
            f"Frame {snap.frame_index + 1}/{self.session.session.total_frames}"
        )

    def on_resize(self, event: events.Resize) -> None:
        del event
        self._fit_preview_to_terminal()

    def _set_status(self, text: str) -> None:
        self.status.set_status(text)

    def action_next_frame(self) -> None:
        try:
            snap = self.session.next_frame()
            self.preview.image = snap.image
            self._set_status(
                f"Frame {snap.frame_index + 1}/{self.session.session.total_frames}"
            )
        except FrameBoundaryError as exc:
            self._set_status(str(exc))

    def action_prev_frame(self) -> None:
        try:
            snap = self.session.previous_frame()
            self.preview.image = snap.image
            self._set_status(
                f"Frame {snap.frame_index + 1}/{self.session.session.total_frames}"
            )
        except FrameBoundaryError as exc:
            self._set_status(str(exc))

    def action_save_frame(self) -> None:
        result = self.session.save_current_frame()
        if result.status == SaveStatus.SUCCESS:
            self._set_status(f"Saved: {result.output_path}")
        else:
            self._set_status(result.error_message or "Failed to save frame")

    def action_quit_app(self) -> None:
        self.session.close()
        self.exit()
