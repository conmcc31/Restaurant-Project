# Task 003 — Database Restaurant Table and Search Selection Persistence

## Goal

Create the restaurant table and let a user save a restaurant by selecting it from the search dropdown built in Task 002. A successful selection persists the restaurant in PostgreSQL with a fixed placeholder user ID, ready for a later user association.

**Definition of done:** The table exists through a versioned migration, and at least one real restaurant selected through the UI (for example, Ruth's Chris Steak House in Boston) has been saved and verified in PostgreSQL.

## Context and Dependencies

- Read `spec-files/project-thesis.md` and `agents/AGENTS.md` before implementation.
- Prior task: [Task 002 — Map Layout and Search](task-002-map-layout.md).
- Existing search flow: `frontend/src/SearchPanel.tsx`, `frontend/src/placeSearch.ts`, `backend/app/search.py`, and `backend/app/main.py`.
- PostgreSQL, SQLAlchemy/Psycopg, and Alembic are already configured. Alembic currently has no domain model metadata or schema revisions.
- Current search results expose only `name` and `display_name`; extend the normalized contract to include the data needed for saving.
- Dependencies: local database and application can start using `README.md` instructions.
- This task intentionally implements only the persistence portion of the thesis. Pins, visit information, and restaurant management remain future tasks.

## In Scope

- SQLAlchemy restaurant model and an Alembic migration creating the `restaurants` table.
- The seven columns below, including validation and database constraints appropriate to their values.
- Extend the existing search response and frontend types to carry restaurant identity, address, and coordinates.
- A backend create endpoint and frontend request to save the selected result.
- Accessible result selection, saving feedback, success confirmation, duplicate feedback, and recoverable failure feedback.
- Prevent duplicate saved restaurants for the same placeholder user, including concurrent requests.
- Relevant tests, local migration instructions, and a real end-to-end saved entry with database evidence.

## Out of Scope

- Map pins, popups, map movement on selection, or other map changes.
- UI or API features for editing or deleting restaurants.
- Saved-restaurant lists, detail sidebars/pages, or a retrieval API solely for displaying saved entries.
- User tables, accounts, login, authentication, authorization, or user switching.
- Visit dates/history, notes, recommendation status, ratings, or additional product fields.
- Search-provider replacement, live autocomplete, broad UI redesign, or production deployment.
- Automatically seeded example restaurants or fabricated provider data as proof of completion.

## Required Behavior / User Scenarios

1. **Search:** Existing explicit-submit search continues to return up to five readable results. Typing or submitting a search alone never writes to the restaurant table.
2. **Select and save:** Clicking a result, or focusing its control and activating it with Enter/Space, saves that result immediately. No separate Save button or confirmation step is required. Show a saving state and prevent repeat activation while the save is pending.
3. **Successful save:** After the backend commits the row, show an accessible confirmation identifying the saved restaurant. Do not report success before persistence completes. The result contains the saved database ID; the map remains unchanged.
4. **Repeat selection:** Selecting an already saved restaurant shows `Already saved` and does not create another row. Identity is the combination of `user_id` and normalized `osm_id`, rather than restaurant name or address.
5. **Save failure:** Invalid data or an unavailable database produces clear feedback without a false success message. Keep the map and search usable, preserve a way to retry, and avoid exposing database details or credentials.
6. **Incomplete provider result:** A result missing a usable name, address, coordinates, or OSM identity must not create an incomplete row. Keep it readable with an explanation that it cannot be saved, or reject it with actionable feedback. Never invent missing values or substitute Nominatim's internal `place_id` for OSM identity.
7. **Persistence:** Saved rows survive browser refreshes and application/database restarts with the existing PostgreSQL volume retained. No saved-entry UI is needed to demonstrate this; verify through SQL.

## Implementation Constraints

- Keep the existing React/Vite/TypeScript, FastAPI, PostgreSQL, SQLAlchemy/Psycopg, and Alembic stack. The frontend calls the backend; it never connects directly to PostgreSQL.
- Use a versioned migration, wired to the SQLAlchemy model metadata. Do not rely on application-startup table creation or recreate the database/volume.
- Use the following schema. All seven columns are required/non-null; `id` is the internal primary key, distinct from the external OSM identity.

| Column | Required meaning / constraint |
| --- | --- |
| `id` | Automatically generated primary key; choose a conventional SQLAlchemy/PostgreSQL ID type and document it. |
| `user_id` | Text, assigned by the backend to exactly `xyz123` for every V1 save; no user foreign key yet. |
| `name` | Nonblank restaurant name from the selected search result. |
| `address` | Nonblank readable location string; use the existing provider `display_name` for this task, even when it includes the restaurant name. Structured address parsing is unnecessary. |
| `latitude` | Finite numeric latitude in the inclusive range -90 to 90. |
| `longitude` | Finite numeric longitude in the inclusive range -180 to 180. |
| `osm_id` | Text combining OSM object type and positive numeric ID, normalized as `node/<id>`, `way/<id>`, or `relation/<id>`. |

- Add a database uniqueness constraint on `(user_id, osm_id)` and handle conflicts transactionally so concurrent saves cannot create duplicates. An already saved selection returns the existing record without overwriting it.
- The backend owns validation, transaction handling, and the placeholder identity. Do not accept a client-selected `user_id` or require an actual user record.
- Normalize provider `lat`/`lon` and `osm_type`/`osm_id` behind the existing search integration. Preserve readable `display_name` and name fields; align frontend types and mocked fixtures with the extended contract. See the [Nominatim output documentation](https://nominatim.org/release-docs/latest/api/Output/) for provider field meanings.
- Use `POST /api/restaurants` for saving. The request carries `name`, `address`, `latitude`, `longitude`, and normalized `osm_id`; the backend supplies `id` and `user_id`. Return the saved record and an unambiguous created/already-saved outcome. Document the exact response shape and HTTP statuses during implementation.
- Permit POST in the existing CORS configuration where needed; retain the configured frontend origin and existing development proxy.
- Save directly from the selected search data without an additional provider lookup. Preserve Task 002's explicit submission, cache, rate limiting, attribution, empty/error states, and stale-search-response protection.
- Selection controls need accessible names, keyboard operation, visible focus, and announced saving/success/error states. A save finishing after the search changes must not mislabel a different result as saved.
- The agent may choose routine internal details such as module organization, numeric storage precision, and primary-key type. Material product or architecture changes require approval.

## Acceptance Criteria

- [x] Applying the Alembic migration to the existing local PostgreSQL database creates `restaurants` with the seven specified columns, primary key, required-value/range constraints, and `(user_id, osm_id)` uniqueness.
- [x] The model metadata is registered with Alembic, and migration setup/usage is documented.
- [x] Search results carry the name, address source, coordinates, and normalized OSM identity required to save them.
- [x] Mouse and keyboard selection of a valid dropdown result sends a save request and commits the matching data, using backend-assigned `user_id = 'xyz123'`.
- [x] The UI reports saving, committed success, already saved, and recoverable failure appropriately.
- [x] Repeated and concurrent saves of the same `(user_id, osm_id)` leave exactly one row and return a usable duplicate outcome. Different OSM object types with the same numeric ID remain distinct.
- [x] Invalid or incomplete payloads cannot create rows; database failures do not produce success feedback or partial writes.
- [x] At least one real UI-selected restaurant is verified in PostgreSQL with all seven values, and remains present after a refresh and restart with the volume retained.
- [x] Relevant backend and frontend tests pass, including PostgreSQL-backed verification of actual persistence and duplicate constraints.
- [x] Existing map/search checks, frontend build/lint, and backend quality checks pass; setup documentation reflects the new migration and save behavior.
- [x] No work from the Out of Scope section was introduced.

## Verification

Run commands from the directories indicated and record actual results in the completion report.

1. **Migration/schema:** With PostgreSQL running, from `backend/` run `.venv/bin/alembic upgrade head` and `.venv/bin/alembic current`. Inspect the actual table's columns, primary key, checks, and unique constraint through SQL. Re-running `upgrade head` must succeed without losing data. Verify migration reversibility only against a disposable test database, never the demonstration database containing saved entries.
2. **Backend:** From `backend/`, run `.venv/bin/pytest`, `.venv/bin/ruff check .`, and `.venv/bin/ruff format --check .`. Cover create success, server-assigned identity, invalid/missing data, coordinate bounds, normalized OSM identity, duplicates/concurrency, and database failure. Exercise migration-backed PostgreSQL persistence/uniqueness in an isolated test database; mocked database calls alone are insufficient evidence. Do not clear the development database for tests.
3. **Frontend:** From `frontend/`, run `npm test`, `npm run lint`, and `npm run build`. Mock HTTP responses to verify pointer/keyboard selection, selected-result payload, pending-request protection, success/already-saved/error feedback, retry, and existing search behavior. Test that search without selection makes no save request and late save responses remain associated with the correct restaurant.
4. **Real save:** Start the database/backend/frontend using the updated README. Search for `Ruth's Chris Steak House`, choose an actual Boston result if available, and verify successful saving feedback without a pin or map movement. If the provider does not return that location, use another real restaurant and document which one; exact live provider coverage is not guaranteed.
5. **Database evidence:** Query `restaurants` for the selected normalized `osm_id` and `user_id = 'xyz123'`. Record its generated ID, name, address, latitude, longitude, and OSM identity; confirm they match the selection. Select the same result again, verify `Already saved`, and confirm the count remains one.
6. **Persistence/regression:** Refresh the browser and restart the application and database while retaining the volume; query the same row again. Check a save failure and subsequent recovery, narrow/mobile selection usability, and unchanged map/search behavior. Update `README.md` so its descriptions of read-only results, GET-only CORS, and the absence of migrations no longer contradict the implementation.

If a check cannot be run, report it as **not verified**, with a reason. Never claim a check passed without executing it. A draft specification or mocked test alone does not satisfy the real saved-entry criterion.

## Open Questions / Approval Required

- **Resolved by the user:** Keep one saved entry per restaurant/user; repeat selection shows `Already saved`.
- **Resolved by the user:** Store OSM object type and numeric ID together in the `osm_id` column.
- **Fixed for this task:** Use backend-assigned placeholder `xyz123`, immediate save on selection, and the existing `display_name` as the address string.
- **None remaining.** Visit history, user accounts, and additional fields are deferred to separate tasks.

## Completion Report

### Summary

Implemented and verified on November 16, 2026. A real Boston restaurant selected
through Safari was committed to PostgreSQL and retained through refresh and
application/database restarts. No implementation questions remained after reading
the task's resolved decisions. No additional product scope was introduced.

### Files Changed

- `backend/app/models.py`: seven-column SQLAlchemy restaurant model and database constraints.
- `backend/app/restaurants.py`: request/response validation and transactional conflict handling.
- `backend/app/main.py`: POST endpoint, engine lifecycle, and POST CORS support.
- `backend/app/search.py`: normalized provider coordinates and typed OSM identity; incomplete labels retained.
- `backend/migrations/env.py`, `backend/migrations/versions/003_restaurants.py`, `backend/migrations/README`: registered metadata, initial migration, and usage.
- `backend/tests/test_restaurants.py`, `backend/tests/test_search.py`: validation, normalization, migration-backed PostgreSQL persistence/concurrency/constraints, and commit-failure rollback coverage.
- `frontend/src/placeSearch.ts`, `frontend/src/SearchPanel.tsx`, `frontend/src/index.css`: extended types, save request, native selection buttons, pending guards, visible focus, live announcements, retry and incomplete-result feedback.
- `frontend/src/App.test.tsx`: selected payload, pending protection, save outcomes, retry, late-response identity, incomplete results, and existing search regressions.
- `README.md`: setup migrations, schema/API contract, test database instructions, and updated search/save behavior.
- This specification: acceptance checklist and completion evidence.

### Verification Results

| Check | Result | Evidence |
| --- | --- | --- |
| Development migration | pass | `.venv/bin/alembic upgrade head` and `current`: `003_restaurants (head)`; repeating upgrade preserved the saved row. |
| Schema and metadata | pass | SQL `\d restaurants`: exactly seven non-null columns, identity primary key, six checks, and `(user_id, osm_id)` uniqueness. `.venv/bin/alembic check`: no new upgrade operations. |
| Backend tests | pass | `RUN_POSTGRES_TESTS=1 .venv/bin/pytest`: 34 passed, including a newly created disposable PostgreSQL database, eight concurrent first saves, unchanged duplicate data, distinct OSM types, boundary coordinates, DB-level invalid-value rejection, commit-failure rollback, and recovery. |
| Migration reversibility | pass | Integration test downgraded only its randomly named disposable database to base, then upgraded it again. The development database was never downgraded or cleared. |
| Backend quality | pass | `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`, and `.venv/bin/python -m pip check` all passed. |
| Frontend tests | pass | `npm test`: 9 passed across App and MapView, including no save on search, exact save payload, pending duplicate protection, failure/retry, incomplete results, stale searches, and late saves identifying the original restaurant. |
| Frontend quality | pass | `npm run lint` and `npm run build` passed. |
| Real provider search | pass | Existing backend returned real Boston and Somerville Ruth's Chris results, normalized from Nominatim without additional lookups. |
| Pointer selection | pass | Safari selected the School Street Boston result; UI announced `Saved Ruth's Chris Steak House.`; server logged POST 201. |
| Duplicate selection | pass | UI announced `Already saved: Ruth's Chris Steak House.`; POST 200 and matching row count remained one. |
| Keyboard and failure recovery | pass | Keyboard focus observed on the Boston result. With PostgreSQL stopped, Space activation produced the recoverable error and POST 503. After PostgreSQL restarted, Enter activation returned `Already saved` and POST 200. |
| Refresh/restart persistence | pass | Browser refreshed; FastAPI and Vite stopped and restarted; PostgreSQL stopped and restarted with the existing volume. Repeated selection returned `Already saved`; final SQL returned the same ID and all original values, count one. |
| Narrow layout | pass | Safari Responsive Design Mode at 375 × 812: readable wrapping/scrollable results, usable search/selection, saving/disabled state followed by `Already saved`. |
| Map/search regression | pass | MapView tests passed; map component/configuration unchanged; no pins or map movement code added. Browser retained zoom controls and attribution. |
| Live map tile imagery | not verified | Safari screenshots showed a gray tile area. The cause was not diagnosed; live tile rendering could not be confirmed. This does not affect the verified search/save flow. |
| Diff whitespace | pass | `git diff --check` passed. |

The backend test run emits an upstream Starlette deprecation warning about its
httpx TestClient integration; tests pass with the pinned dependencies.

### Saved Database Evidence

The real UI selection was verified through SQL before and after refresh/restarts:

| Column | Stored value |
| --- | --- |
| `id` | `1` |
| `user_id` | `xyz123` |
| `name` | `Ruth's Chris Steak House` |
| `address` | `Ruth's Chris Steak House, 45, School Street, Downtown Crossing, Downtown, Boston, Suffolk County, Massachusetts, 02108, United States` |
| `latitude` | `42.3580909` |
| `longitude` | `-71.0595739` |
| `osm_id` | `node/7623094006` |

Final query (after mobile repeat selection and all restarts) returned this row and
`matching_rows = 1`:

```sql
SELECT *, (SELECT count(*) FROM restaurants
           WHERE user_id = 'xyz123' AND osm_id = 'node/7623094006') AS matching_rows
FROM restaurants
WHERE user_id = 'xyz123' AND osm_id = 'node/7623094006';
```

### Decisions and Deviations

- PostgreSQL integer identity primary key; double precision coordinates; no new dependencies.
- Backend-fixed user is also enforced by a database check; a future user-association migration can replace it.
- POST contract: `{name,address,latitude,longitude,osm_id}` only. Responses contain `{outcome,restaurant}` with all seven stored fields. `201/created`, `200/already_saved`, `422` for validation, `503` for database failure. Details and examples are in README and generated API docs.
- `ON CONFLICT DO NOTHING` followed by reading the committed winner preserves the original row under concurrent selection. Success is returned only after commit.
- Incomplete provider results keep their readable labels but have null save identity/coordinates and disabled controls with an explanation. Nominatim `place_id` is never substituted.
- Native browser buttons provide Enter/Space activation. Save status names the originally selected restaurant even when the query changes.
- Browser-host access was initially unavailable. After the user enabled access, Safari native automation completed the real save and keyboard/mobile checks.
- No product/architecture deviations; no fabricated or seeded restaurant was used for demonstration.

### Follow-Up

- Investigate gray live map tiles separately if reproducible; live imagery remains unverified.
- Changes are in the working tree; no commit or PR was created.
- Local frontend/backend and PostgreSQL remain running for review. The real demonstration row is retained.
