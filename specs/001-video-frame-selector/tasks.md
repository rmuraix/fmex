# Tasks: Video Frame Selector

**Input**: Design documents from `/home/rmuraix/ghq/github.com/rmuraix/fmex/specs/001-video-frame-selector/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Comprehensive automated testing is required for this feature (unit, integration, contract, performance).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/`, `tests/` at repository root
- Feature docs: `specs/001-video-frame-selector/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline tooling for implementation/testing.

- [X] T001 Add runtime dependencies (`av`) and ensure CLI entrypoint in `/home/rmuraix/ghq/github.com/rmuraix/fmex/pyproject.toml`
- [X] T002 Create package module skeleton and exports in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/cli.py`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/models/__init__.py`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/__init__.py`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/__init__.py`
- [X] T003 [P] Create test directory structure and package markers in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/.gitkeep`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/integration/.gitkeep`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/contract/.gitkeep`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/performance/.gitkeep`
- [X] T004 [P] Add deterministic sample media fixture loader in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core primitives required before implementing user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Implement core domain models (`VideoSession`, `FrameSnapshot`, `SaveOperation`, `UserCommand`) in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/models/session.py` and `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/models/commands.py`
- [X] T006 [P] Implement keyboard mapping and command translation in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/keymap.py`
- [X] T007 [P] Implement bounded frame cache service with diskcache backend in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/frame_cache.py`
- [X] T008 Implement video decode/index service abstraction with PyAV hooks in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/video_decoder.py`
- [X] T009 [P] Implement PNG save service with unique naming and outdir creation helpers in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/frame_saver.py`
- [X] T010 [P] Add foundational unit tests for models, keymaps, and cache semantics in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/test_session_models.py`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/test_keymap.py`, `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/test_frame_cache.py`

**Checkpoint**: Foundation ready. User stories can now proceed.

---

## Phase 3: User Story 1 - Select and Save a Frame (Priority: P1) 🎯 MVP

**Goal**: Open a video, preview selected frame, and save exact selected frame as PNG to cwd or `--outdir`.

**Independent Test**: Run `uv run fmex samples/video.mp4 --outdir ./exports`, press save key on selected frame, and verify PNG exists under `./exports` and matches preview frame.

### Tests for User Story 1

- [X] T011 [P] [US1] Add contract conformance tests for open-session/get-frame/save-frame behavior in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/contract/test_contract_conformance.py`
- [X] T012 [P] [US1] Add integration test for CLI open + save flow with `--outdir` auto-create in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/integration/test_outdir_and_save_flow.py`
- [X] T013 [P] [US1] Add unit tests for outdir validation, unique PNG naming, and save failures in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/test_frame_saver.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement Typer CLI argument parsing (`video_file`, `--outdir`) and startup validation in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/cli.py`
- [X] T015 [US1] Implement Textual app shell and session lifecycle orchestration in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py`
- [X] T016 [P] [US1] Implement frame preview widget using textual-image in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/frame_view.py`
- [X] T017 [US1] Integrate current-frame decode/load pipeline into app startup and save action in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py`
- [X] T018 [US1] Implement actionable launch/decode/save error surfacing in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py` and `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/cli.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Navigate Frames with Keyboard (Priority: P2)

**Goal**: Navigate forward/backward by frame using keyboard with boundary-safe behavior.

**Independent Test**: Run `uv run fmex samples/video.mp4`, press next/previous keys repeatedly, and verify preview updates correctly and boundary feedback appears at first/last frame.

### Tests for User Story 2

- [X] T019 [P] [US2] Add contract conformance tests for next/previous frame operations and boundary conflicts in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/contract/test_contract_conformance.py`
- [X] T020 [P] [US2] Add integration test for keyboard navigation across frame boundaries in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/integration/test_cli_to_tui_flow.py`
- [X] T021 [P] [US2] Add unit tests for frame index transitions and boundary guards in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/test_video_decoder.py`

### Implementation for User Story 2

- [X] T022 [US2] Implement next/previous frame commands and boundary enforcement in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/video_decoder.py`
- [X] T023 [US2] Wire keyboard events to navigation commands and status feedback in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py`
- [X] T024 [US2] Integrate cache-aware navigation (reuse and prefetch adjacent frames) in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/video_decoder.py` and `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/frame_cache.py`

**Checkpoint**: User Stories 1 and 2 are independently functional and testable.

---

## Phase 5: User Story 3 - Understand Controls and Status (Priority: P3)

**Goal**: Show users key controls and current frame position clearly in the TUI.

**Independent Test**: Start app as first-time user and complete navigate/save/quit using on-screen instructions only.

### Tests for User Story 3

- [X] T025 [P] [US3] Add integration test verifying control legend visibility and frame-position updates in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/integration/test_cli_to_tui_flow.py`
- [X] T026 [P] [US3] Add unit tests for status line formatting and command hint rendering in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/unit/test_app_status.py`

### Implementation for User Story 3

- [X] T027 [US3] Implement control legend component and key-help text in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/frame_view.py`
- [X] T028 [US3] Implement frame position/status updates on state transitions in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py`
- [X] T029 [US3] Ensure quit command and close-session messaging are consistent in `/home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Performance hardening, end-to-end quality checks, and documentation.

- [X] T030 [P] Add performance regression tests for frame-step latency target in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/performance/test_navigation_latency.py`
- [X] T031 [P] Add memory budget test for sustained navigation sessions in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/performance/test_memory_budget.py`
- [X] T032 Add CLI smoke test for invalid/corrupt input errors in `/home/rmuraix/ghq/github.com/rmuraix/fmex/tests/integration/test_error_paths.py`
- [X] T033 [P] Update and validate quickstart commands and keyboard docs in `/home/rmuraix/ghq/github.com/rmuraix/fmex/specs/001-video-frame-selector/quickstart.md` and `/home/rmuraix/ghq/github.com/rmuraix/fmex/README.md`
- [X] T034 Run full test suite with coverage threshold report and capture results in `/home/rmuraix/ghq/github.com/rmuraix/fmex/specs/001-video-frame-selector/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user stories.
- **User Stories (Phases 3-5)**: Depend on Phase 2 completion; can proceed in priority order or parallel if staffed.
- **Polish (Phase 6)**: Depends on completion of target user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on other user stories.
- **US2 (P2)**: Starts after Phase 2; depends functionally on foundational decoder/cache but not on US1 completion.
- **US3 (P3)**: Starts after Phase 2; integrates app state from US1/US2 but remains independently testable.

### Within Each User Story

- Tests are written before implementation and must fail before feature code changes.
- Models/services before app wiring.
- App wiring before integration assertions.

### Parallel Opportunities

- Phase 1: T003, T004 parallel.
- Phase 2: T006, T007, T009, T010 parallel after T005 baseline model contracts.
- US1: T011, T012, T013, T016 parallel.
- US2: T019, T020, T021 parallel.
- US3: T025, T026 parallel.
- Polish: T030, T031, T033 parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T011 [US1] Contract conformance tests in tests/contract/test_contract_conformance.py"
Task: "T012 [US1] Integration save flow test in tests/integration/test_outdir_and_save_flow.py"
Task: "T013 [US1] Frame saver unit tests in tests/unit/test_frame_saver.py"
Task: "T016 [US1] Frame preview widget in src/fmex/ui/frame_view.py"
```

## Parallel Example: User Story 2

```bash
Task: "T019 [US2] Contract navigation tests in tests/contract/test_contract_conformance.py"
Task: "T020 [US2] Keyboard navigation integration test in tests/integration/test_cli_to_tui_flow.py"
Task: "T021 [US2] Decoder transition unit tests in tests/unit/test_video_decoder.py"
```

## Parallel Example: User Story 3

```bash
Task: "T025 [US3] Integration test for control legend/status in tests/integration/test_cli_to_tui_flow.py"
Task: "T026 [US3] Unit tests for status and hints in tests/unit/test_app_status.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independent test and contract/save behavior.
4. Demo or ship MVP.

### Incremental Delivery

1. Deliver US1 (frame selection and save).
2. Deliver US2 (precise navigation and boundaries).
3. Deliver US3 (controls and status clarity).
4. Finish with Phase 6 performance and coverage hardening.

### Parallel Team Strategy

1. Team aligns on Phase 1 and Phase 2.
2. After foundation:
   - Engineer A: US1
   - Engineer B: US2
   - Engineer C: US3
3. Re-converge on Phase 6 for performance/coverage gates.
