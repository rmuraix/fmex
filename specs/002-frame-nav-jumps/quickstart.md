# Quickstart: Faster Frame Navigation & Time Jump

## Prerequisites

- Python 3.11+
- Local video file for testing

## Run

```bash
fmex /path/to/video.mp4
```

## Navigation

- `Left` / `h`: Previous frame (1 frame)
- `Right` / `l`: Next frame (1 frame)
- `Shift` + step: Jump 10 frames
- `Ctrl` + step: Jump 100 frames
- `t`: Open time jump input, enter seconds, press `Enter`
- `s`: Save selected frame as PNG
- `q`: Quit

## Performance Expectations

- Frame stepping and time jumps should feel instantaneous.
- Initial open to first frame should complete within ~3 seconds on baseline media.

## Tests

```bash
cd /home/rmuraix/ghq/github.com/rmuraix/fmex
.venv/bin/pytest -q
```
