from fmex.models.commands import CommandType
from fmex.ui.keymap import command_for_key, controls_text


def test_keymap_translation() -> None:
    assert command_for_key("right") == CommandType.NEXT_FRAME
    assert command_for_key("left") == CommandType.PREV_FRAME
    assert command_for_key("s") == CommandType.SAVE_FRAME
    assert command_for_key("q") == CommandType.QUIT


def test_controls_text_contains_hints() -> None:
    text = controls_text()
    assert "Left" in text
    assert "save" in text
