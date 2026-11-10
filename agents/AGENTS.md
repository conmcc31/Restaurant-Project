# Agent Instructions

## Project Context

This repository uses spec-driven development.

Before implementing any task:

1. Read project-thesis.md.
2. Read the current task specification.
3. Review relevant existing code and architecture.
4. Identify contradictions or missing requirements.

## Implementation Rules

- Follow the technology decisions in project-thesis.md.
- Implement only what is required by the current task.
- Prefer maintainable, straightforward solutions.
- Avoid introducing unnecessary dependencies.
- Do not expand the scope of a task without approval.
- Do not overwrite unrelated existing work.

## Decision-Making

Agents may independently:

- Choose implementation details within established constraints.
- Organize files and internal helper functions.
- Introduce appropriate tests.
- Make minor implementation adjustments.

Agents must request approval before:

- Changing the established technology stack.
- Introducing substantial architectural changes.
- Altering documented product behavior.
- Implementing features explicitly out of scope.

## Verification

- Run relevant tests and checks.
- Verify all acceptance criteria.
- Report any criteria that could not be verified.
- Never claim a test passed unless it was executed.

## Completion Report

After implementation, provide:

- Summary of changes
- Files created or modified
- Verification performed
- Architectural decisions made
- Unresolved questions or known limitations
