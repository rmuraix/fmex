from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from PIL import Image


class SessionStatus(str, Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    ERRORED = "errored"
    CLOSED = "closed"


class SaveStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass(slots=True)
class VideoSession:
    session_id: str
    source_path: Path
    total_frames: int
    current_frame_index: int
    outdir: Path
    status: SessionStatus
    error_message: str | None = None


@dataclass(slots=True)
class FrameSnapshot:
    session_id: str
    frame_index: int
    timestamp_ms: int
    width: int
    height: int
    image: Image.Image


@dataclass(slots=True)
class SaveOperation:
    save_id: str
    session_id: str
    frame_index: int
    output_path: Path
    status: SaveStatus
    created_at: datetime
    error_message: str | None = None
