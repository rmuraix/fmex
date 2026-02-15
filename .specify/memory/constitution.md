<!--
Sync Impact Report
Version change: N/A -> 1.0.0
Modified principles: N/A (new document)
Added sections: Core Principles; Performance Standards; Development Workflow & Quality Gates; Governance
Removed sections: None
Templates requiring updates:
- ✅ /home/rmuraix/ghq/github.com/rmuraix/fmex/.specify/templates/plan-template.md (no changes needed)
- ✅ /home/rmuraix/ghq/github.com/rmuraix/fmex/.specify/templates/spec-template.md (no changes needed)
- ✅ /home/rmuraix/ghq/github.com/rmuraix/fmex/.specify/templates/tasks-template.md (no changes needed)
- ✅ No command templates present under `/home/rmuraix/ghq/github.com/rmuraix/fmex/.specify/templates/commands/`
- ✅ /home/rmuraix/ghq/github.com/rmuraix/fmex/README.md (no changes needed)
Follow-up TODOs:
- TODO(RATIFICATION_DATE): Original adoption date unknown; confirm once available.
-->
# fmex Constitution

## Core Principles

### I. Code Quality and Maintainability
All changes MUST preserve or improve clarity, readability, and simplicity. Code MUST be
structured to be easily understood and modified by others. Avoid hidden side effects,
excessive coupling, and duplication. Public behaviors and assumptions MUST be documented
where they affect user workflows or future maintenance.

### II. Testing Standards (Non-Negotiable)
Every new behavior MUST be covered by tests that verify the intended user outcome. Every
bug fix MUST include a regression test. Tests MUST be deterministic, fast enough to run
routinely, and focused on primary user workflows. Changes that alter navigation behavior
MUST include tests that validate expected frame and time positioning.

### III. User Experience Consistency
User interactions MUST be predictable and consistent across the application. Keybindings
and commands MUST not change meaning across contexts. Errors and invalid inputs MUST
produce clear, actionable messages without losing user progress. UX changes that affect
existing workflows MUST include a clear rationale and, when needed, migration guidance.

### IV. Performance-First Interaction
Interactive operations (frame step, time jump, save actions) MUST feel instantaneous for
typical inputs, with p95 response time under 200 ms on representative media. Long-running
operations MUST provide progress feedback and remain cancelable where feasible. Performance
regressions beyond 10% on key workflows require explicit justification and remediation.

## Performance Standards

- Typical input baseline: 1080p, 30 fps, 10-minute video on a development-class machine.
- Initial open to first actionable frame MUST complete within 3 seconds for the baseline.
- Interactive navigation actions MUST meet the p95 target defined in Core Principles.
- Memory usage MUST remain bounded and free of unbounded growth during navigation.

## Development Workflow & Quality Gates

- All changes MUST undergo review against the Core Principles and Performance Standards.
- Tests relevant to the change MUST pass before merging.
- Performance impact MUST be assessed in the feature plan; performance-sensitive changes
  MUST document expected cost and mitigation.
- User-facing changes MUST update user documentation or on-screen help where applicable.

## Governance

This constitution supersedes local practices when conflicts arise. Amendments require a
documented proposal, rationale, and version bump. Compliance MUST be reviewed during PR
review and before release.

Versioning policy:
- MAJOR: Backward-incompatible governance changes or principle removals.
- MINOR: New principles or material expansions of guidance.
- PATCH: Clarifications or minor wording changes.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date unknown.
| **Last Amended**: 2026-02-15
