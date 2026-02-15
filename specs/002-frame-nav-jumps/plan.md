# Implementation Plan: Faster Frame Navigation & Time Jump

**Branch**: `002-frame-nav-jumps` | **Date**: 2026-02-15 | **Spec**: /home/rmuraix/ghq/github.com/rmuraix/fmex/specs/002-frame-nav-jumps/spec.md
**Input**: Feature specification from `/specs/002-frame-nav-jumps/spec.md`

## Summary

Add accelerated frame stepping with Shift/Ctrl modifiers and a jump-to-time (seconds)
input. Preserve existing navigation behavior, ensure clear error handling, and meet
interactive performance targets defined in the constitution.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Typer (CLI), Textual + textual-image (TUI), Pillow, PyAV,
 diskcache
**Storage**: Local files (video input/output) and diskcache for frame caching
**Testing**: pytest
**Target Platform**: Desktop terminal (local execution)
**Project Type**: single
**Performance Goals**: p95 interactive actions < 200 ms; initial open to first frame < 3 s
 on baseline media
**Constraints**: No >10% regression on key workflows; bounded memory usage during navigation
**Scale/Scope**: Single-user local workflow on typical desktop-class machine

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Design Gates (from constitution):
- Code Quality and Maintainability: Planned changes localized to navigation handling.
- Testing Standards (Non-Negotiable): Tests will be added for modifier stepping and
  time jump validation.
- User Experience Consistency: New inputs preserve existing key meanings.
- Performance-First Interaction: Actions target <200 ms p95.

Status: PASS (no violations)

Post-Design Re-check:
- Design artifacts align with performance targets and testing requirements.
- No additional gates introduced.

Status: PASS

## Project Structure

### Documentation (this feature)

```text
specs/002-frame-nav-jumps/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── fmex/

tests/
```

**Structure Decision**: Single project with `src/` and `tests/` at repo root.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations.
