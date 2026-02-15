# Feature Specification: Video Frame Selector

**Feature Branch**: `001-video-frame-selector`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: User description: "Create an application that allows users to select any frame from a video and save it. Launch it like 'fmex video.mp4'. The TUI displays a preview of the selected frame, and users can navigate between frames using keyboard controls."

## Clarifications

### Session 2026-02-15

- Q: How should save destination be chosen during interactive use? → A: Use the `--outdir` CLI option.
- Q: What output image format should be used for saved frames? → A: PNG.
- Q: How should the app handle a missing `--outdir` directory? → A: Create it automatically.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select and Save a Frame (Priority: P1)

A user opens a video from the command line, navigates to a desired frame, and saves that exact frame as an image file.

**Why this priority**: This is the core user value of the feature: extracting a specific frame from a video.

**Independent Test**: Run `fmex <video-file>`, move to a known frame, save it, and confirm an image file is created that matches the displayed frame.

**Acceptance Scenarios**:

1. **Given** a valid local video file path, **When** the user runs `fmex <video-file>`, **Then** the application opens the video and displays an initial frame preview.
2. **Given** the frame preview is visible, **When** the user triggers the save action, **Then** the currently selected frame is written to an image file and the user sees a success confirmation including the save location.

---

### User Story 2 - Navigate Frames with Keyboard (Priority: P2)

A user navigates forward and backward through frames using keyboard controls to locate the precise frame they want.

**Why this priority**: Precise frame navigation is required to make frame selection practical.

**Independent Test**: Open a video and use only keyboard input to move between frames; verify frame position updates consistently and predictably.

**Acceptance Scenarios**:

1. **Given** a loaded video, **When** the user presses the control for next frame, **Then** the preview updates to the next frame.
2. **Given** a loaded video, **When** the user presses the control for previous frame, **Then** the preview updates to the previous frame.
3. **Given** the first frame is selected, **When** the user requests previous frame, **Then** the selection remains at the first frame and the user receives boundary feedback.

---

### User Story 3 - Understand Controls and Status (Priority: P3)

A user can see key controls and current frame position so they can operate the interface without guesswork.

**Why this priority**: Clear controls and status reduce mistakes and speed up completion.

**Independent Test**: Start the app as a first-time user and verify you can navigate, save, and exit using on-screen instructions only.

**Acceptance Scenarios**:

1. **Given** the TUI is displayed, **When** the user views the interface, **Then** it shows the available keyboard controls for navigation, saving, and quitting.
2. **Given** the user navigates frames, **When** the selection changes, **Then** the interface updates the current frame position indicator.

### Edge Cases

- Invalid or missing video path at launch returns a clear error and does not enter the interactive interface.
- Unsupported or corrupted video files return a clear error and do not crash the application.
- Very short videos (single frame or very few frames) still allow preview and save behavior.
- Saving fails due to permission or disk-space issues returns a clear error message and keeps the session active.
- If `--outdir` points to a directory that does not exist, the system creates it before saving; if creation fails, it returns a clear error and keeps the session active.
- Repeated saves from the same frame create distinct output files without silently overwriting unless the user explicitly requests overwrite behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a local video file path as a required launch argument in the format `fmex <video-file>`.
- **FR-001a**: System MUST accept an optional `--outdir <directory>` CLI argument that sets the directory used for saved frame output.
- **FR-001b**: System MUST create the `--outdir` directory automatically when it does not exist, and MUST show an actionable error if directory creation fails.
- **FR-002**: System MUST validate that the provided path exists and points to a readable video file before starting the interactive session.
- **FR-003**: System MUST display a TUI containing a preview of the currently selected frame.
- **FR-004**: System MUST allow users to navigate at least one frame forward and one frame backward using keyboard controls.
- **FR-005**: System MUST prevent navigation beyond the first and last frame and provide boundary feedback.
- **FR-006**: System MUST allow users to save the currently selected frame as an image file through a keyboard control.
- **FR-006a**: System MUST save extracted frames in PNG format.
- **FR-007**: System MUST confirm successful saves with the output file path.
- **FR-007a**: System MUST save extracted frames to the directory specified by `--outdir` when provided; otherwise it MUST save to the current working directory.
- **FR-008**: System MUST display actionable error messages for launch, decoding, and save failures.
- **FR-009**: System MUST display available keyboard controls for navigation, save, and quit within the TUI.
- **FR-010**: System MUST display current frame position information during navigation.
- **FR-011**: System MUST allow the user to quit the application from the keyboard without forcing termination.

### Key Entities *(include if feature involves data)*

- **Video Session**: Represents a loaded video file in an interactive session; includes source path, total frame count, and current frame index.
- **Frame Selection**: Represents the currently active frame; includes frame index and displayable frame preview state.
- **Saved Frame Output**: Represents a frame export event; includes source frame index, output path, save timestamp, and save result status.
- **Keyboard Command**: Represents a recognized user input action; includes command type (next, previous, save, quit) and resulting state change.

## Assumptions

- The application is intended for single-user local CLI use with local video files.
- The default save location is the current working directory when `--outdir` is not provided.
- Saved frame files are image files and are named uniquely by default to avoid accidental overwrite.
- Frame navigation is frame-by-frame; jump navigation and playback controls are out of scope for this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of users can open a valid video, navigate to a target frame, and save it in under 2 minutes on first attempt.
- **SC-002**: 100% of save actions produce an image matching the frame shown in preview at the time of save in acceptance testing.
- **SC-003**: 100% of invalid launch inputs (missing file, unreadable file, unsupported/corrupt file) return a clear user-facing error without application crash.
- **SC-004**: At least 90% of first-time users can correctly identify navigation, save, and quit controls from the TUI without external documentation.
