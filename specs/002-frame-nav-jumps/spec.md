# Feature Specification: Faster Frame Navigation & Time Jump

**Feature Branch**: `002-frame-nav-jumps`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: User description: "For improved convenience, we will enhance the frame navigation method. When using Shift or Ctrl, it will now advance by 10 or 100 frames. Additionally, we will add functionality to jump to any specified number of seconds."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accelerated Frame Stepping (Priority: P1)

As a user reviewing a video, I can step forward or backward faster by holding modifier keys so I can reach nearby frames quickly without repeated inputs.

**Why this priority**: Fast stepping reduces friction in the most common navigation task.

**Independent Test**: Can be fully tested by using the existing frame step controls with and without modifiers and observing the frame index change.

**Acceptance Scenarios**:

1. **Given** a video is loaded and the current frame is 100, **When** I step forward without modifiers, **Then** the current frame becomes 101.
2. **Given** a video is loaded and the current frame is 100, **When** I step forward while holding Shift, **Then** the current frame becomes 110.
3. **Given** a video is loaded and the current frame is 100, **When** I step backward while holding Ctrl, **Then** the current frame becomes 0 or the first frame if fewer than 100 frames are available behind.

---

### User Story 2 - Jump to Specific Time (Priority: P2)

As a user, I can jump directly to a specific time in seconds so I can reach a precise moment without manual stepping.

**Why this priority**: Time-based navigation is a common mental model when reviewing videos.

**Independent Test**: Can be fully tested by entering a target time in seconds and verifying the current frame corresponds to that time.

**Acceptance Scenarios**:

1. **Given** a 120-second video is loaded, **When** I enter a jump time of 60 seconds, **Then** the current frame updates to the frame nearest 60 seconds from the start.
2. **Given** a video is loaded, **When** I enter a jump time greater than the video duration, **Then** the current frame moves to the last frame and I am informed the time was out of range.

### Edge Cases

- Jump time is negative or non-numeric.
- Jump time falls between frames and requires rounding to the nearest available frame.
- Modifier stepping would move beyond the first or last frame.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support single-frame step forward and backward without modifiers.
- **FR-002**: System MUST advance by 10 frames when stepping with Shift held.
- **FR-003**: System MUST advance by 100 frames when stepping with Ctrl held.
- **FR-004**: System MUST apply modifier stepping consistently for both forward and backward step actions.
- **FR-005**: Users MUST be able to enter a target time in seconds to jump to that point in the video.
- **FR-006**: System MUST interpret the jump time as an absolute offset from the start of the video.
- **FR-007**: System MUST move to the nearest available frame for a given jump time.
- **FR-008**: If a jump time is outside the video duration, system MUST move to the nearest valid boundary (first or last frame) and inform the user.
- **FR-009**: If a jump time input is invalid, system MUST reject it and present a clear error message without changing the current frame.

### Key Entities *(include if feature involves data)*

- **Video Time**: A position in the video expressed in seconds from the start.
- **Current Frame**: The active frame index the user is viewing or selecting.
- **Step Size**: The number of frames advanced per step action (1, 10, or 100).

### Assumptions

- Modifier keys are used with existing step controls; default step size is 1 frame.
- Jump time input accepts whole or fractional seconds.
- User-facing messages are shown when input is invalid or out of range.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can move 100 frames forward or backward in a single action using a modifier key.
- **SC-002**: Users can reach a specified time in the video within one jump action, with the resulting frame within one frame of the target time.
- **SC-003**: 95% of attempted jumps with valid numeric input land on the expected frame without additional adjustments.
- **SC-004**: User-reported navigation time to reach a target moment is reduced by at least 50% compared to single-frame stepping.
