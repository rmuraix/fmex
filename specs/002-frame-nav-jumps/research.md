# Research: Faster Frame Navigation & Time Jump

## Decisions

### 1) Use existing frame index and caching for navigation
- **Decision**: Reuse the current frame index and cache mechanisms for modifier
  stepping and time jumps.
- **Rationale**: This minimizes additional overhead and keeps interactive actions
  within p95 < 200 ms.
- **Alternatives considered**: Recompute frame positions on each action; rejected
  due to added latency and redundant work.

### 2) Time-to-frame mapping based on existing video timing metadata
- **Decision**: Convert seconds to the nearest available frame using existing
  timing metadata already used for playback/navigation.
- **Rationale**: Ensures consistent behavior with current frame display and avoids
  drift between time and frame positions.
- **Alternatives considered**: Maintain a separate time-to-frame table; rejected
  for extra memory and initialization cost.

### 3) Input validation with bounded navigation
- **Decision**: Reject invalid time inputs without changing the current frame and
  clamp out-of-range values to first/last frame with clear messaging.
- **Rationale**: Preserves user context and prevents unnecessary work.
- **Alternatives considered**: Silent clamping for all invalid inputs; rejected
  for lack of user feedback and possible confusion.

### 4) Performance safeguards in navigation actions
- **Decision**: Keep navigation operations O(1) with constant-time index updates
  and avoid any full-seek or re-decode per step.
- **Rationale**: Protects interactive responsiveness and aligns with
  performance-first constitution principle.
- **Alternatives considered**: Triggering decode on every step; rejected due to
  latency risk and cache churn.
