# Data Model: Faster Frame Navigation & Time Jump

## Entities

### Video Time
- **Description**: Absolute position in the video expressed in seconds from start.
- **Fields**:
  - `seconds` (float): Non-negative, may include fractional seconds.
- **Validation**:
  - Must be numeric.
  - Negative values are invalid.

### Current Frame
- **Description**: Active frame index being displayed/selected.
- **Fields**:
  - `index` (int): Zero-based frame index.
- **Validation**:
  - Must be within `[0, last_frame_index]`.
- **State Transitions**:
  - Can move by `step_size` forward/backward with clamping to bounds.

### Step Size
- **Description**: Number of frames advanced per step action.
- **Fields**:
  - `frames` (int): One of `{1, 10, 100}` based on modifier state.
- **Validation**:
  - Must be a supported value derived from input modifiers.

## Relationships

- **Video Time → Current Frame**: A time input maps to the nearest frame index.
- **Step Size → Current Frame**: Step size drives the delta applied to the current
  frame index.
