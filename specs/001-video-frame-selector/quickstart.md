# Quickstart: Video Frame Selector

## Prerequisites
- Python 3.11+
- Local dependencies installed (`.venv` created)
- Any local video file (for example: `/path/to/video.mp4`)

## Run Application
1. Launch with default output directory (current working directory):
   - `fmex /path/to/video.mp4`
2. Launch with explicit output directory:
   - `fmex /path/to/video.mp4 --outdir ./exports`

## Keyboard Controls
- `Right` / `l`: Next frame
- `Left` / `h`: Previous frame
- `s`: Save current frame as PNG
- `q`: Quit application

## Expected Behavior Checks
1. Initial frame preview appears after load.
2. Frame index indicator changes on navigation.
3. Save action writes `.png` file under `--outdir` or cwd.
4. Missing `--outdir` is created automatically.
5. Invalid/corrupt input file fails with actionable error.

## Test Commands
- Full suite:
  - `.venv/bin/pytest -q`
- With coverage:
  - `.venv/bin/pytest --cov=src/fmex --cov-report=term-missing -q`
- Unit tests only:
  - `.venv/bin/pytest tests/unit -q`
- Integration tests:
  - `.venv/bin/pytest tests/integration -q`
- Contract tests:
  - `.venv/bin/pytest tests/contract -q`
- Performance tests:
  - `.venv/bin/pytest tests/performance -m performance -q`

## Latest Validation Snapshot (2026-02-15)
- Test result: `21 passed`
- Coverage result: `85%` total line coverage (`src/fmex`)
- Warnings: 6 deprecation warnings from `textual-image`/Pillow interaction (non-blocking)

## Performance Validation Targets
- p95 single-step navigation latency <= 120 ms on reference sample.
- First-frame render <= 2.0 s on reference sample.
- Memory use <= 300 MB during sustained frame stepping.
