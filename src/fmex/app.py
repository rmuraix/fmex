from __future__ import annotations

from PIL import Image
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input
from textual_image.widget import SixelImage

from fmex.models import SaveStatus
from fmex.services import FrameBoundaryError, FrameSession, VideoDecodeError
from fmex.ui.frame_view import StatusLine, build_footer_widgets


class TimeJumpScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Container(id="time_jump_modal"):
            yield Input(placeholder="Seconds (e.g. 12.5)", id="time_jump_input")

    def on_mount(self) -> None:
        self.styles.align = ("center", "middle")
        self.styles.background = "#020617 70%"
        modal = self.query_one("#time_jump_modal", Container)
        modal.styles.width = 40
        modal.styles.height = 5
        modal.styles.padding = (0, 2)
        modal.styles.border = ("round", "#22d3ee")
        modal.styles.background = "#020617"
        input_widget = self.query_one("#time_jump_input", Input)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "time_jump_input":
            return
        value = event.value.strip()
        self.dismiss(value or None)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)
            event.prevent_default()


class FMEXApp(App[None]):
    CSS = """
    Screen {
        background: #020617;
        color: #dbeafe;
    }

    #app_root {
        height: 100%;
    }

    #preview_pane {
        height: 1fr;
        width: 100%;
        align: center middle;
    }

    #preview_frame {
        border: round #0ea5e9;
        background: #000814;
        align: center middle;
        width: 100%;
        height: 100%;
    }

    #preview {
        width: auto;
        height: auto;
        max-width: 100%;
        max-height: 100%;
    }

    ControlsLegend {
        background: #0f172a;
        color: #7dd3fc;
        padding: 0 1;
    }

    #status {
        background: #111827;
        color: #e2e8f0;
        padding: 0 1;
    }

    #time_jump_modal {
        border: round #22d3ee;
        background: #020617;
    }

    #time_jump_input {
        background: #020617;
        color: #e2e8f0;
    }
    """

    BINDINGS = [
        Binding("right", "next_frame", "Next"),
        Binding("left", "prev_frame", "Prev"),
        Binding("l", "next_frame", "Next"),
        Binding("h", "prev_frame", "Prev"),
        Binding("shift+right", "step_forward_10", "Next+10"),
        Binding("shift+left", "step_back_10", "Prev-10"),
        Binding("shift+l", "step_forward_10", "Next+10"),
        Binding("shift+h", "step_back_10", "Prev-10"),
        Binding("ctrl+right", "step_forward_100", "Next+100"),
        Binding("ctrl+left", "step_back_100", "Prev-100"),
        Binding("ctrl+l", "step_forward_100", "Next+100"),
        Binding("ctrl+h", "step_back_100", "Prev-100"),
        Binding("j", "focus_time_jump", "Jump"),
        Binding("s", "save_frame", "Save"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, session: FrameSession) -> None:
        super().__init__()
        self.session = session
        self.preview = SixelImage(id="preview")
        self.status = StatusLine("Initializing", id="status")

    def compose(self) -> ComposeResult:
        with Vertical(id="app_root"):
            with Container(id="preview_pane"):
                with Container(id="preview_frame"):
                    yield self.preview
            yield from build_footer_widgets()
            yield self.status

    def _set_preview_image(self, image: Image.Image) -> None:
        self.preview.image = image

    def on_mount(self) -> None:
        snap = self.session.get_current_frame()
        self._set_preview_image(snap.image)
        self._update_frame_status(snap)

    def on_resize(self, event: events.Resize) -> None:
        del event
        self.preview.refresh(layout=True)

    def _set_status(self, text: str) -> None:
        self.status.set_status(text)

    def _set_status_with_frame(self, text: str) -> None:
        current = self.session.session.current_frame_index + 1
        total = self.session.total_frames_display()
        self._set_status(f"{text} | Frame {current}/{total}")

    def _update_frame_status(self, snap, message: str | None = None) -> None:
        status = f"Frame {snap.frame_index + 1}/{self.session.total_frames_display()}"
        if message:
            status = f"{message} | {status}"
        self._set_status(status)

    def action_focus_time_jump(self) -> None:
        self.push_screen(TimeJumpScreen(), self._handle_time_jump)
        self._set_status_with_frame("Enter seconds and press Enter")

    def _handle_time_jump(self, value: str | None) -> None:
        if not value:
            self._set_status_with_frame("Jump canceled")
            return
        try:
            seconds = float(value)
            snap, message = self.session.jump_to_time(seconds)
            self._set_preview_image(snap.image)
            self._update_frame_status(snap, message)
        except (ValueError, FrameBoundaryError, VideoDecodeError) as exc:
            self._set_status_with_frame(str(exc))

    def _step_by(self, delta: int) -> None:
        try:
            snap, message = self.session.step_frames(delta)
            self._set_preview_image(snap.image)
            self._update_frame_status(snap, message)
        except FrameBoundaryError as exc:
            self._set_status_with_frame(str(exc))

    def action_step_forward_10(self) -> None:
        self._step_by(10)

    def action_step_back_10(self) -> None:
        self._step_by(-10)

    def action_step_forward_100(self) -> None:
        self._step_by(100)

    def action_step_back_100(self) -> None:
        self._step_by(-100)

    def action_next_frame(self) -> None:
        self._step_by(1)

    def action_prev_frame(self) -> None:
        self._step_by(-1)

    def action_save_frame(self) -> None:
        result = self.session.save_current_frame()
        if result.status == SaveStatus.SUCCESS:
            self._set_status_with_frame(f"Saved: {result.output_path}")
        else:
            self._set_status_with_frame(result.error_message or "Failed to save frame")

    def action_quit_app(self) -> None:
        self.session.close()
        self.exit()
