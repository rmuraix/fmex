# fmex

[![PyPI - Version](https://img.shields.io/pypi/v/fmex)](https://pypi.org/project/fmex/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fmex)](https://pypi.org/project/fmex/)
[![GitHub License](https://img.shields.io/github/license/rmuraix/fmex)](https://github.com/rmuraix/fmex/blob/main/LICENSE)
[![Check](https://github.com/rmuraix/fmex/actions/workflows/check.yaml/badge.svg)](https://github.com/rmuraix/fmex/actions/workflows/check.yaml)
[![codecov](https://codecov.io/gh/rmuraix/fmex/graph/badge.svg?token=z6XwE8PkrK)](https://codecov.io/gh/rmuraix/fmex)

Terminal-based frame extractor for video files.

## About

`fmex` opens a local video, lets you move frame-by-frame in a TUI, previews the selected frame, and saves the current frame as PNG.

![fmex](https://github.com/rmuraix/fmex/raw/main/assets/ui.png)

## Usage

```bash
# Save to current directory
fmex /path/to/video.mp4

# Save to custom output directory (auto-created if missing)
fmex /path/to/video.mp4 --outdir ./exports
```

Keyboard controls:

- `Left` / `h`: Prev
- `Right` / `l`: Next
- `Shift` + `Left`/`Right`: ±10
- `Ctrl` + `Left`/`Right`: ±100
- `j`: Jump to time (seconds)
- `s`: Save PNG
- `q`: Quit

## Contributing

Your contribution is always welcome. Please read [Contributing Guide](https://github.com/rmuraix/.github/blob/main/.github/CONTRIBUTING.md).
