# Task 004 — Restaurant recommendation and comment storage

## Goal

Extend saved restaurants with an optional recommendation and store each personal note as a separate dated comment.

## Context and Dependencies

- Read `spec-files/project-thesis.md` and `agents/AGENTS.md`.
- Prior work: 003. Extend `backend/app/models.py` and the Alembic chain headed by `003_restaurants`.

## In Scope

- Add `restaurants.recommend BOOLEAN NULL` with no default. Existing rows and newly saved restaurants begin with NULL. TRUE and FALSE represent explicit choices.
- Create `comments` with a generated primary key `comment_id`, required `restaurant_id` referencing `restaurants.id`, nonblank text `comment`, and required SQL DATE `added_on`. Assign the creation date on the server.
- Use ON DELETE CASCADE so deleting a restaurant also removes its notes.

## Out of Scope

Feedback endpoints, UI, and restaurant visit dates.

## Required Behavior / User Scenarios

- Given an existing restaurant, upgrading the database preserves its saved data and leaves its recommendation unset.
- Given two comments on one restaurant, deleting that restaurant removes both comments and preserves comments on other restaurants.

## Implementation Constraints

Use a versioned migration and matching SQLAlchemy metadata. Ownership follows the parent restaurant. The existing create and duplicate-save contracts continue to work.

## Acceptance Criteria

- [x] Existing and new rows support all three recommendation states. The column has no database default.
- [x] Multiple comments can belong to a restaurant. Missing parents, blank notes and missing required values are rejected.
- [x] Migration and cascade behavior are covered against disposable PostgreSQL.

## Verification

1. With local services running as described in `README.md`, on a disposable database, upgrade to 003, insert a restaurant, upgrade to head and inspect the columns and original row. Exercise constraints and cascade with two restaurants. Downgrade and reapply on that database.
2. From `backend/`, run `RUN_POSTGRES_TESTS=1 .venv/bin/pytest`, `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .`. Record actual results.

## Open Questions / Approval Required

None for this ticket.

## Completion Report (Agent Fills In)

### Summary

Migration `004_feedback` adds a nullable recommendation to saved restaurants and stores each note in its own dated comment row. PostgreSQL deletes a restaurant’s comments when its parent row is deleted.

### Files Changed

- `backend/migrations/versions/004_feedback.py` adds the upgrade and downgrade.
- `backend/app/models.py` maps the recommendation and comment fields.
- `backend/tests/test_restaurants.py` verifies the migration against disposable PostgreSQL databases and updates the existing schema assertions.
- `README.md` identifies the new migration head and clarifies the save response.
- This task file records the acceptance results.

### Verification Results

| Check | Result | Evidence |
| --- | --- | --- |
| Upgrade from 003 | Passed | All original restaurant values survived. Existing and newly inserted rows started with NULL and accepted TRUE, FALSE and NULL. Schema inspection confirmed a nullable boolean with no default. |
| Comment storage and validation | Passed | PostgreSQL generated comment IDs and dates. Inserts rejected an unknown or missing parent, missing text, empty or whitespace-only text, and an explicit NULL date. |
| Cascade and migration reversal | Passed | Deleting one restaurant removed both of its notes and preserved the other restaurant’s note. Downgrading to 003 removed the feedback schema. Reapplying the migration preserved the surviving restaurant. |
| `RUN_POSTGRES_TESTS=1 .venv/bin/pytest` | 35 passed | Includes concurrent and duplicate saves. Starlette emitted one TestClient dependency deprecation warning. |
| `.venv/bin/ruff check .` | Passed | All checks passed. |
| `.venv/bin/ruff format --check .` | Passed | 13 files already formatted. |

### Decisions and Deviations

PostgreSQL assigns the creation date with `CURRENT_DATE`. The restaurant foreign key determines comment ownership and enforces cascading deletion for all database clients.

### Follow-Up

Apply the migration to the development database using the existing README upgrade instructions. Verification used disposable databases.
