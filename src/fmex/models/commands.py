from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CommandType(str, Enum):
    OPEN = "open"
    NEXT_FRAME = "next_frame"
    PREV_FRAME = "prev_frame"
    SAVE_FRAME = "save_frame"
    QUIT = "quit"


@dataclass(slots=True)
class UserCommand:
    command_type: CommandType
    source: str
    issued_at: datetime
    result: str
    result_reason: str | None = None
