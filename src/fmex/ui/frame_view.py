from __future__ import annotations

import re

from rich.text import Text
from textual.widget import Widget
from textual.widgets import Static

from fmex.ui.keymap import controls_text


class ControlsLegend(Static):
    def __init__(self) -> None:
        self.text = controls_text()
        super().__init__(self.text)


class StatusLine(Static):
    _FRAME_COUNTER_PATTERN = re.compile(r"Frame \d+/(?:\d+|\?)")

    def __init__(self, text: str, **kwargs) -> None:
        self.text = text
        super().__init__(self._render_status(text), **kwargs)

    def set_status(self, text: str) -> None:
        self.text = text
        self.update(self._render_status(text))

    def _render_status(self, text: str) -> Text:
        rendered = Text(text)
        for match in self._FRAME_COUNTER_PATTERN.finditer(text):
            rendered.stylize("bold #f8fafc on #0369a1", match.start(), match.end())
        return rendered


def build_footer_widgets() -> list[Widget]:
    return [ControlsLegend()]
