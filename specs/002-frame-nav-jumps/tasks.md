---

description: "Task list for Faster Frame Navigation & Time Jump"
---

# Tasks: Faster Frame Navigation & Time Jump

**Input**: Design documents from `/specs/002-frame-nav-jumps/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested in spec; no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Update keyboard controls documentation in /home/rmuraix/ghq/github.com/rmuraix/fmex/README.md to include modifier stepping and time jump input

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Add public FPS accessor and time-to-frame helper in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/video_decoder.py
- [x] T003 Add navigation helper methods for step sizing and time jump validation in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/session_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Accelerated Frame Stepping (Priority: P1) 🎯 MVP

**Goal**: Allow Shift and Ctrl modifiers to advance by 10 or 100 frames while preserving existing 1-frame stepping

**Independent Test**: Use step controls with and without modifiers and verify frame index changes by 1, 10, or 100, clamped to bounds

### Implementation for User Story 1

- [x] T004 [P] [US1] Add modifier-aware bindings and action routing in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py
- [x] T005 [US1] Implement step-by-N navigation with boundary clamping in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/session_service.py
- [x] T006 [P] [US1] Update controls legend to show modifier steps in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/keymap.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Jump to Specific Time (Priority: P2)

**Goal**: Allow users to jump to an absolute time in seconds with validation and clear feedback

**Independent Test**: Enter a valid time and confirm the frame updates to the nearest frame; enter invalid/out-of-range time and confirm messaging with no unwanted frame changes

### Implementation for User Story 2

- [x] T007 [P] [US2] Add a time-jump input widget to the footer in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/frame_view.py
- [x] T008 [US2] Handle time-jump input submission and status messaging in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py
- [x] T009 [US2] Implement jump-to-time behavior using FPS mapping in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/services/session_service.py
- [x] T010 [P] [US2] Update controls legend text for time jump usage in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/keymap.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T011 [P] Validate status messaging for boundary conditions and invalid inputs in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py
- [x] T012 [P] Ensure quickstart navigation instructions match new behavior in /home/rmuraix/ghq/github.com/rmuraix/fmex/specs/002-frame-nav-jumps/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Can be done after US1 but is independently testable

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- T004 and T006 can run in parallel (different files)
- T007 and T010 can run in parallel (different files)
- T011 and T012 can run in parallel (different files)

---

## Parallel Example: User Story 1

```text
Task: "Add modifier-aware bindings and action routing in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/app.py"
Task: "Update controls legend to show modifier steps in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/keymap.py"
```

---

## Parallel Example: User Story 2

```text
Task: "Add a time-jump input widget to the footer in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/frame_view.py"
Task: "Update controls legend text for time jump usage in /home/rmuraix/ghq/github.com/rmuraix/fmex/src/fmex/ui/keymap.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
