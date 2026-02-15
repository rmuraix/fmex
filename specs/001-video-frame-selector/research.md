# Phase 0 Research: Video Frame Selector

## Decision 1: Video decoding and frame-accurate navigation engine
- Decision: Use PyAV for container parsing, timestamp-aware seeking, and frame decode.
- Rationale: PyAV provides direct control over frame iteration and seek behavior needed for frame-by-frame navigation with lower overhead than shelling out to external tools repeatedly.
- Alternatives considered:
  - OpenCV (`cv2.VideoCapture`): simpler API but less predictable frame-accurate seek behavior across codecs.
  - `ffmpeg` subprocess per frame: high process overhead and poor interactive latency.

## Decision 2: TUI architecture and rendering strategy
- Decision: Build a Textual app with a dedicated frame preview widget and explicit key bindings (`left/right`, `h/l`, `s`, `q`).
- Rationale: Textual supports deterministic keyboard handling and testable UI behavior via pilot testing while fitting the required terminal UX.
- Alternatives considered:
  - Curses-based custom UI: less ergonomic testing and harder high-level layout composition.
  - Prompt-driven non-interactive CLI: does not satisfy continuous preview/navigation requirement.

## Decision 3: Preview image pipeline
- Decision: Convert decoded frame data into Pillow image objects and render via textual-image.
- Rationale: Existing dependency alignment (Pillow + textual-image) minimizes integration risk and supports PNG output consistency.
- Alternatives considered:
  - ASCII-only preview: insufficient visual fidelity for selecting exact frames.
  - Raw terminal protocol rendering: increased complexity and portability risk.

## Decision 4: Performance optimization strategy
- Decision: Use bounded LRU frame cache (diskcache-backed), prefetch adjacent frames, and lazy decode windows around current index.
- Rationale: Frame stepping speed is dominated by decode I/O; caching and local prefetch reduce repeated decode cost while bounded cache enforces memory constraints.
- Alternatives considered:
  - Decode-on-demand only: simpler but likely to violate navigation latency targets.
  - Full video preload: unacceptable memory cost for long videos.

## Decision 5: Save behavior and output management
- Decision: Save PNG files only; honor `--outdir`; auto-create missing output directory; generate unique filenames per save.
- Rationale: Matches clarified requirements and avoids overwrite/data loss while preserving deterministic output behavior.
- Alternatives considered:
  - Interactive save prompts: breaks fast keyboard-driven workflow.
  - JPEG output: lossy, less suitable for exact frame capture.

## Decision 6: Comprehensive test strategy
- Decision: Cover unit, integration, contract, and performance layers with pytest and pytest-cov, including deterministic sample media fixtures.
- Rationale: Layered tests reduce regression risk across parsing, UI flow, and latency/memory constraints while producing measurable coverage.
- Alternatives considered:
  - Unit-only tests: insufficient to validate interactive TUI and CLI end-to-end behavior.
  - Manual-only performance checks: non-repeatable and weak for CI regression detection.

## Decision 7: Contract representation for planning and validation
- Decision: Define a local OpenAPI contract for the internal frame session operations used by CLI/TUI flows.
- Rationale: Satisfies contract artifact requirement and provides a stable interface model for task decomposition and integration tests.
- Alternatives considered:
  - No formal contract: reduces traceability from requirements to tests.
  - GraphQL schema: unnecessary complexity for command-oriented workflow.
