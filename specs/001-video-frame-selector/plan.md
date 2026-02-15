# Implementation Plan: Video Frame Selector

**Branch**: `001-video-frame-selector` | **Date**: 2026-02-15 | **Spec**: `/home/rmuraix/ghq/github.com/rmuraix/fmex/specs/001-video-frame-selector/spec.md`
**Input**: Feature specification from `/specs/001-video-frame-selector/spec.md`

## Summary

Build a local CLI/TUI application invoked as `fmex <video-file> [--outdir <directory>]` that lets users navigate video frames with keyboard controls, preview frames in a Textual interface, and save the selected frame as PNG. The implementation will prioritize responsive frame navigation by combining efficient frame decoding/indexing, lightweight frame caching, and predictable file output behavior.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Typer (CLI), Textual + textual-image (TUI and preview), Pillow (PNG writing), PyAV (video decode/index), diskcache (frame cache)  
**Storage**: Local filesystem (video input + PNG output), local ephemeral cache  
**Testing**: pytest, pytest-cov, Typer CLI tests, Textual pilot tests, performance regression tests  
**Target Platform**: Linux/macOS terminal environments with local file access
**Project Type**: Single Python CLI/TUI application  
**Performance Goals**: Frame step latency p95 <= 120 ms on 1080p H.264 sample; initial load to first preview <= 2.0 s on 2-minute sample video  
**Constraints**: Memory budget <= 300 MB during interactive navigation on 1080p sample; no network requirement; graceful error handling for invalid/corrupt media and save failures  
**Scale/Scope**: Single-user local usage; videos up to 60 minutes; frame-by-frame navigation and PNG export only (no playback, no editing)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Gate 1: Feature spec exists and includes testable requirements and success criteria. **PASS**
- Gate 2: Constitution policy source at `.specify/memory/constitution.md` is not present in repository. Using default project quality gates (tests, measurable performance, no contradiction with spec). **PASS (no ratified constitution to violate)**
- Gate 3: User-mandated stack constraints (Textual + Typer) are reflected in technical context. **PASS**
- Gate 4: Performance and comprehensive testing are explicitly planned with measurable targets. **PASS**

Post-Design Re-check:

- Gate 1: Design artifacts map to all functional requirements and clarified decisions. **PASS**
- Gate 2: No design artifact contradicts explicit user constraints or spec clarifications. **PASS**
- Gate 3: Contracts, data model, and quickstart include validation/performance testability. **PASS**

## Project Structure

### Documentation (this feature)

```text
specs/001-video-frame-selector/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── frame-extraction.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── fmex/
    ├── __init__.py
    ├── cli.py
    ├── app.py
    ├── models/
    │   ├── session.py
    │   └── commands.py
    ├── services/
    │   ├── video_decoder.py
    │   ├── frame_cache.py
    │   └── frame_saver.py
    └── ui/
        ├── frame_view.py
        └── keymap.py

tests/
├── contract/
│   └── test_contract_conformance.py
├── integration/
│   ├── test_cli_to_tui_flow.py
│   └── test_outdir_and_save_flow.py
├── performance/
│   ├── test_navigation_latency.py
│   └── test_memory_budget.py
└── unit/
    ├── test_video_decoder.py
    ├── test_frame_cache.py
    ├── test_frame_saver.py
    └── test_keymap.py
```

**Structure Decision**: Single Python project structure with a domain-service split under `src/fmex` and layered tests (`unit`, `integration`, `contract`, `performance`) to satisfy comprehensive coverage and performance verification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
