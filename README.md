# fmex

Terminal-based frame extractor for video files.

## About

`fmex` opens a local video, lets you move frame-by-frame in a Textual TUI, previews the selected frame, and saves the current frame as PNG.

## Usage

```bash
# Save to current directory
fmex /path/to/video.mp4

# Save to custom output directory (auto-created if missing)
fmex /path/to/video.mp4 --outdir ./exports
```

Keyboard controls:

- `Left` / `h`: Previous frame
- `Right` / `l`: Next frame
- `s`: Save selected frame as PNG
- `q`: Quit

## Testing

```bash
.venv/bin/pytest -q
.venv/bin/pytest --cov=src/fmex --cov-report=term-missing -q
```

## Contributing

Your contribution is always welcome. Please read [Contributing Guide](https://github.com/rmuraix/.github/blob/main/.github/CONTRIBUTING.md).
