from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fmex.models import (
    FrameSnapshot,
    SaveOperation,
    SaveStatus,
    SessionStatus,
    VideoSession,
)
from fmex.services.frame_cache import FrameCache
from fmex.services.frame_saver import FrameSaveError, FrameSaver
from fmex.services.video_decoder import (
    FrameIndexError,
    PyAVVideoDecoder,
    VideoDecodeError,
)


class FrameBoundaryError(RuntimeError):
    pass


@dataclass
class FrameSession:
    video_file: Path
    outdir: Path
    decoder_factory: type[PyAVVideoDecoder] = PyAVVideoDecoder

    def __post_init__(self) -> None:
        self.session = VideoSession(
            session_id=uuid4().hex,
            source_path=self.video_file,
            total_frames=0,
            current_frame_index=0,
            outdir=self.outdir,
            status=SessionStatus.INITIALIZING,
        )
        self.cache = FrameCache(max_items=64)
        self.decoder = self.decoder_factory(self.video_file)
        self.saver = FrameSaver(self.outdir)
        self.session.total_frames = self.decoder.frame_count
        self.session.status = SessionStatus.READY

    def _snapshot(self, frame_index: int) -> FrameSnapshot:
        cached = self.cache.get(frame_index)
        image = cached if cached is not None else self.decoder.get_frame(frame_index)
        self.cache.put(frame_index, image)
        return FrameSnapshot(
            session_id=self.session.session_id,
            frame_index=frame_index,
            timestamp_ms=frame_index,
            width=image.width,
            height=image.height,
            image=image,
        )

    def get_current_frame(self) -> FrameSnapshot:
        return self._snapshot(self.session.current_frame_index)

    def next_frame(self) -> FrameSnapshot:
        target_index = self.session.current_frame_index + 1
        try:
            snap = self._snapshot(target_index)
        except FrameIndexError as exc:
            if self.decoder.frame_count:
                self.session.total_frames = self.decoder.frame_count
            raise FrameBoundaryError("Already at last frame") from exc
        self.session.current_frame_index = target_index
        self._prefetch_neighbors()
        return snap

    def previous_frame(self) -> FrameSnapshot:
        if self.session.current_frame_index <= 0:
            raise FrameBoundaryError("Already at first frame")
        self.session.current_frame_index -= 1
        snap = self._snapshot(self.session.current_frame_index)
        self._prefetch_neighbors()
        return snap

    def _prefetch_neighbors(self) -> None:
        idx = self.session.current_frame_index
        neighbors = [idx + 1, idx - 1]
        if self.session.total_frames > 0:
            candidates = [n for n in neighbors if 0 <= n < self.session.total_frames]
        else:
            candidates = [n for n in neighbors if n >= 0]
        self.cache.prefetch(
            candidates,
            self.decoder.get_frame,
        )

    def save_current_frame(self) -> SaveOperation:
        now = datetime.now()
        attempted_index = self.session.current_frame_index
        attempted_output = self.saver.build_target(attempted_index)
        try:
            snapshot = self.get_current_frame()
            output = self.saver.save_png(
                snapshot.image,
                snapshot.frame_index,
                target=attempted_output,
            )
            return SaveOperation(
                save_id=uuid4().hex,
                session_id=self.session.session_id,
                frame_index=snapshot.frame_index,
                output_path=output,
                status=SaveStatus.SUCCESS,
                created_at=now,
            )
        except (FrameSaveError, VideoDecodeError) as exc:
            return SaveOperation(
                save_id=uuid4().hex,
                session_id=self.session.session_id,
                frame_index=attempted_index,
                output_path=attempted_output,
                status=SaveStatus.FAILURE,
                created_at=now,
                error_message=str(exc),
            )

    def total_frames_display(self) -> str:
        total = self.session.total_frames
        return str(total) if total > 0 else "?"

    def close(self) -> None:
        self.session.status = SessionStatus.CLOSED
        self.cache.close()
        if hasattr(self.decoder, "close"):
            self.decoder.close()
