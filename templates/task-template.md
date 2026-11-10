# Task [NNN] — [Short Descriptive Title]

> Copy this file for each new, bounded task. Replace bracketed placeholders, remove unused prompts, and keep the specification proportionate to the work.

## Goal

[One to three sentences describing the outcome and why it matters. State the result rather than a detailed sequence of code edits.]

## Context and Dependencies

- Read `project-thesis.md` and `AGENTS.md` before starting.
- Relevant existing modules/features: [paths or concise description]
- Prior tasks or decisions: [links/IDs, or None]
- Dependencies/blockers: [what must already exist]

## In Scope

- [Specific deliverable 1]
- [Specific deliverable 2]

## Out of Scope

- [Related capability that must **not** be implemented]
- [Other deliberate exclusions]

## Required Behavior / User Scenarios

[Include only when this task changes user-visible behavior or an external API.]

- **Given** [initial state], **when** [action], **then** [observable outcome].
- **Given** [edge case or failure], **when** [action], **then** [expected response].

## Implementation Constraints

- Use the stack and principles in `project-thesis.md`.
- [Relevant API contract, migration expectations, file/module boundaries, security/privacy or provider rules]
- [Compatibility or performance constraints, if materially relevant]
- The agent may choose routine internal implementation details; do not make material architectural/product changes without approval.

## Acceptance Criteria

- [ ] [Observable behavior or deliverable with a clear pass/fail result]
- [ ] [Key edge case handled]
- [ ] [Appropriate automated tests included or updated]
- [ ] [Documentation/configuration updated where relevant]
- [ ] [No work from the Out of Scope section was introduced]

## Verification

Describe exactly how the result will be checked. Prefer checks that can actually be run locally.

1. [Command or automated test + expected result]
2. [Manual test with steps + expected result, if necessary]
3. [Regression check or other check]

If a test cannot be run, report it as **not verified**, with a reason; never claim it passed without executing it.

## Open Questions / Approval Required

- [Decision that affects product behavior or architecture, or `None`]
- [Any assumption the agent must confirm rather than silently choose]

## Completion Report (Agent Fills In)

### Summary

[What changed]

### Files Changed

- [Path: purpose]

### Verification Results

| Check | Result (pass/fail/not verified) | Evidence |
| --- | --- | --- |
| [Acceptance criterion or command] | [Result] | [Actual output/observation] |

### Decisions and Deviations

- [Implementation choice and why]
- [Any deviation from the task or unresolved limitation]

### Follow-Up

- [Suggested next task, not implemented here]
- PR/commit: [Link or ID, if available]
