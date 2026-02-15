# Data Model: Video Frame Selector

## Entity: VideoSession
- Description: Runtime representation of an opened video file.
- Fields:
  - `session_id` (string, unique): Identifier for an active session.
  - `source_path` (string): Absolute or relative path to input video.
  - `total_frames` (integer, >= 1): Total decoded frame count.
  - `current_frame_index` (integer, 0..total_frames-1): Selected frame pointer.
  - `outdir` (string): Effective output directory (CLI `--outdir` or cwd).
  - `status` (enum): `initializing | ready | errored | closed`.
  - `error_message` (string|null): User-facing error when status is `errored`.
- Validation rules:
  - `source_path` must exist and be readable before status can become `ready`.
  - `outdir` must be writable; if missing, creation attempted before first save.
  - `current_frame_index` must never exceed boundaries.
- Relationships:
  - One `VideoSession` has many `FrameSnapshot` records.
  - One `VideoSession` has many `SaveOperation` records.

## Entity: FrameSnapshot
- Description: Decoded previewable representation of a frame index.
- Fields:
  - `session_id` (string): Owning session.
  - `frame_index` (integer): Zero-based frame location.
  - `timestamp_ms` (integer, >= 0): Approximate media timestamp.
  - `width` (integer, > 0): Frame width.
  - `height` (integer, > 0): Frame height.
  - `cache_key` (string): Key used for cache retrieval.
  - `is_prefetched` (boolean): Indicates speculative prefetch.
- Validation rules:
  - `(session_id, frame_index)` is unique.
  - Image payload must be decodable to preview and exportable to PNG.
- Relationships:
  - Belongs to one `VideoSession`.

## Entity: SaveOperation
- Description: Result of a user save action for selected frame.
- Fields:
  - `save_id` (string, unique): Identifier of save attempt.
  - `session_id` (string): Owning session.
  - `frame_index` (integer): Selected frame at save time.
  - `output_path` (string): Final PNG path.
  - `status` (enum): `success | failure`.
  - `error_message` (string|null): Failure reason when status is `failure`.
  - `created_at` (datetime): Save attempt timestamp.
- Validation rules:
  - `output_path` must end in `.png`.
  - `output_path` must be unique by default unless explicit overwrite is introduced in future scope.
- Relationships:
  - Belongs to one `VideoSession`.
  - References one `FrameSnapshot` via `(session_id, frame_index)`.

## Entity: UserCommand
- Description: Normalized keyboard or CLI command interpreted by the application.
- Fields:
  - `command_type` (enum): `open | next_frame | prev_frame | save_frame | quit`.
  - `issued_at` (datetime): Time command was handled.
  - `source` (enum): `cli | tui_keyboard`.
  - `result` (enum): `applied | rejected`.
  - `result_reason` (string|null): Error/boundary explanation.
- Validation rules:
  - `next_frame` and `prev_frame` must enforce boundary checks.
  - `save_frame` requires `VideoSession.status == ready`.

## State Transitions
- `VideoSession.status`
  - `initializing -> ready` on successful video parse and first frame decode.
  - `initializing -> errored` on invalid/unreadable/corrupt video.
  - `ready -> errored` on unrecoverable runtime failure.
  - `ready -> closed` on quit command.
  - `errored -> closed` on quit command.
- `SaveOperation.status`
  - Starts as implicit pending during save action.
  - `pending -> success` when PNG write completes.
  - `pending -> failure` on directory creation, permission, disk, or encode errors.
