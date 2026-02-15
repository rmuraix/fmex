from __future__ import annotations

from fmex.models.commands import CommandType

KEY_COMMANDS: dict[str, CommandType] = {
    "right": CommandType.NEXT_FRAME,
    "left": CommandType.PREV_FRAME,
    "l": CommandType.NEXT_FRAME,
    "h": CommandType.PREV_FRAME,
    "s": CommandType.SAVE_FRAME,
    "q": CommandType.QUIT,
}


def command_for_key(key: str) -> CommandType | None:
    return KEY_COMMANDS.get(key)


def controls_text() -> str:
    return (
        "Left/h: prev | Right/l: next | Shift: ±10 | Ctrl: ±100 | "
        "j: jump | s: save PNG | q: quit"
    )
