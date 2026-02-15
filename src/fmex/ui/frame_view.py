from __future__ import annotations

from textual.widget import Widget
from textual.widgets import Static

from fmex.ui.keymap import controls_text


class ControlsLegend(Static):
    def __init__(self) -> None:
        self.text = controls_text()
        super().__init__(self.text)


class StatusLine(Static):
    def __init__(self, text: str, **kwargs) -> None:
        self.text = text
        super().__init__(text, **kwargs)

    def set_status(self, text: str) -> None:
        self.text = text
        self.update(text)


def build_footer_widgets() -> list[Widget]:
    return [ControlsLegend()]
