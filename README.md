# Food Maps

Local development foundation for the single-user Food Maps demo. This setup includes
a Boston-centered Leaflet map, explicitly submitted restaurant-name search through
FastAPI, and PostgreSQL persistence for selected restaurants. Product scope is defined in
[the project thesis](spec-files/project-thesis.md).

## Prerequisites

- Node.js 24 LTS and npm (the frontend also accepts Node 22.12+).
- Python 3.10 or newer, with `venv` and pip. Verification used Python 3.10.2.
- Docker Desktop, or Docker Engine with Docker Compose v2. Start the Docker daemon first.
- Git and curl for the optional repository and HTTP checks.

The frontend versions were verified with Node 25.2.1 / npm 11.6.2 on macOS arm64.
Use Node 24 LTS for ongoing development (`cd frontend && nvm use` if using nvm).

## First-time setup

Run these commands from this repository root. Do not create another project directory.

```sh
cp .env.example .env
cp backend/.env.example backend/.env
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm ci
cd ..
docker compose up -d --wait
docker compose ps
docker compose exec -T db pg_isready -U food_maps -d food_maps
cd backend
.venv/bin/alembic upgrade head
cd ..
```

`.env` supplies Compose's database user, password, database name, and host port.
`backend/.env` supplies `DATABASE_URL` and `FRONTEND_ORIGIN`; the backend reads it
relative to its source directory. Existing process environment variables take precedence.
Only example values are tracked. Change the local example password in both files
before using personal credentials. URL-encode special characters in the connection URL.
No frontend environment variables or mapping/search keys are needed. Search configuration
is described below.

PostgreSQL is exposed on **127.0.0.1:5433**, with its container listening on 5432.
If 5433 is occupied, change `POSTGRES_PORT` in the root `.env`, update the port in
`DATABASE_URL` in `backend/.env`, then run `docker compose up -d --wait` again.
Changing database user/password/name after the volume has been initialized does
not update existing PostgreSQL roles; keep those values consistent with the volume.

## Run locally

In one terminal, from the repository root:

```sh
cd backend
source .venv/bin/activate
uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

In another terminal, from the repository root:

```sh
cd frontend
npm run dev
```

Open <http://localhost:5173>. The main page shows a Boston map and restaurant search.
Vite uses a strict port so a conflict cannot silently change the documented CORS origin.
FastAPI is at <http://127.0.0.1:8000>, with generated API documentation at `/docs`.
`GET /health` checks the process independently of database availability.
`GET /api/places/search?q=...` returns up to five places with readable labels and normalized save data.
The Vite development server proxies `/api` to the existing backend on port 8000;
serve `/api` from the same origin when serving a production frontend build. CORS permits only `http://localhost:5173`, with GET and POST requests.
If changing the frontend URL, also change `FRONTEND_ORIGIN` in `backend/.env` and restart FastAPI.

Check health and database connectivity:

```sh
curl --fail http://127.0.0.1:8000/health
cd backend
.venv/bin/python -m app.check_db
```

Expected output: `{"status":"ok"}` and `Database connection successful (SELECT 1).`
The database command exits nonzero when the check fails and does not print credentials.
It uses SQLAlchemy with Psycopg 3 and creates no tables.

## Tests, lint, and build

From `backend/`:

```sh
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pip check
.venv/bin/alembic heads
.venv/bin/alembic current
```

`alembic current` needs PostgreSQL running and should show `004_feedback (head)`.
After pulling new migrations, run `.venv/bin/alembic upgrade head` before starting
FastAPI. Repeating this command preserves existing data. Alembic uses the registered
SQLAlchemy metadata in `app/models.py`; the app never creates tables at startup.
Do not downgrade the development database containing saved entries.

For migration-backed PostgreSQL tests, also run from `backend/`:

```sh
RUN_POSTGRES_TESTS=1 .venv/bin/pytest
```

These tests use the configured database role to create a randomly named
`food_maps_test_*` database, migrate it, test commits/concurrent duplicates/constraints,
downgrade and upgrade it, then drop only that disposable database. The role needs
CREATEDB permission (the local Compose role has it). Without the opt-in, the integration
test is explicitly skipped; unit tests still run. No development rows are cleared.

From `frontend/`:

```sh
npm run lint
npm test
npm run build
```

Vitest uses jsdom and React Testing Library. `npm run test:watch` starts watch mode.
The production build includes TypeScript checking; its output is in ignored `frontend/dist/`.
Tailwind uses its official Vite plugin and the CSS import in `src/index.css`.

## Dependencies

Frontend direct dependencies are pinned in `frontend/package.json`, with transitive
versions in `frontend/package-lock.json`. Install with `npm ci`.
Backend runtime and development dependencies are fully pinned in `backend/requirements.txt`.
`requirements.in` records their direct purposes: FastAPI/Uvicorn for the API,
SQLAlchemy/Psycopg for PostgreSQL, Alembic for versioned migrations, Pydantic Settings
for environment loading, pytest for API tests, httpx for provider calls and tests, and Ruff for quality checks.

For an intentional backend dependency refresh, resolve `requirements.in` in a fresh
Python 3.10 virtual environment, run all checks, then regenerate the lock:

```sh
backend/.venv/bin/python -m pip install -r backend/requirements.in
backend/.venv/bin/python -m pip freeze > backend/requirements.txt
```

PostgreSQL uses the explicit `17.7-bookworm` image tag and a named `postgres_data`
volume. The Compose service is the only containerized component.
See [the setup verification report](spec-files/task-001-completion.md) for actual
versions, executed checks, and known tooling limitations.
The Vite and Tailwind configuration follows their official guides:
[Vite](https://vite.dev/guide/) and
[Tailwind CSS](https://tailwindcss.com/docs/installation/using-vite).

## Shutdown and data

Press Ctrl+C in the frontend and backend terminals. Deactivate the Python environment
with `deactivate` if active. From the repository root:

```sh
docker compose down
```

The named database volume survives `down` and app restarts. `docker compose up -d --wait`
starts it again. Do not add `--volumes` to shutdown unless you intend to delete all local
database data. Environments, `.env` files, dependency directories, caches, and build
outputs are excluded by `.gitignore`.

## Map and search (Task 002)

The map starts at Boston (42.3601, -71.0589), zoom 13. Submit a restaurant name
with Enter or Search; typing never sends a request. Selecting a complete result immediately saves it and announces saving, committed
success, or `Already saved`; results do not move the map or add pins. Failed saves
can be retried by selecting the result again. Incomplete results remain readable
with a disabled selection control and an explanation. Nominatim is a geocoder, so restaurant coverage varies.
Queries are sent to the configured external provider; avoid confidential information.

**Public Nominatim usage:** follow the [usage policy](https://operations.osmfoundation.org/policies/nominatim/).
It permits moderate, user-triggered searches, prohibits autocomplete and systematic
scraping, and requires application identification, attribution, caching, and at most
one upstream request per second across the application. FastAPI serializes misses
with at least 1.1 seconds between request starts (including failed requests), caches
up to 256 queries for 24 hours in memory, and backs off for at least 60 seconds after
HTTP 429. No automatic retries are made. The visible search credit and map credit
link to OpenStreetMap attribution/licensing. Cache contents reset on backend restart.

Run **one backend process with one worker/replica**, as in the local command above.
All browser sessions share that process's limiter/cache. Do not deploy multiple
workers or concurrent backend instances against the public provider: the in-memory
limiter cannot coordinate those instances. A shared limiter/cache or a different
provider must be chosen before scaling; neither is part of this local demo task.

Optional backend environment variables (restart FastAPI after changing):

- `NOMINATIM_SEARCH_URL`: complete search endpoint; defaults to
  `https://nominatim.openstreetmap.org/search`. Replace it with a compatible endpoint
  without changing frontend code.
- `NOMINATIM_USER_AGENT`: defaults to `FoodMapsLocalDemo/0.1`; use an application
  identifier with your real contact URL/email before public deployment.

Tiles load directly from `https://tile.openstreetmap.org/{z}/{x}/{y}.png` using
normal browser caching and Referer behavior. Do not disable caching, strip the
Referer, or bulk download tiles. See the [tile policy](https://operations.osmfoundation.org/policies/tiles/).
Search works without a database connection, though the existing backend settings
still require `DATABASE_URL` to be configured.

## Restaurant persistence (Task 003)

`restaurants` has exactly seven required columns: an `INTEGER GENERATED BY DEFAULT
AS IDENTITY` primary key `id`, text `user_id`, `name`, `address`, `osm_id`, and double
precision `latitude`/`longitude`. The backend always assigns `user_id = xyz123`.
Coordinates must be finite and within ±90/±180; names/addresses must be nonblank.
OSM identity is `node/<positive ID>`, `way/<positive ID>`, or `relation/<positive ID>`.
The database enforces these rules and uniqueness of `(user_id, osm_id)`.
Double precision preserves provider coordinates without rounding to a fixed scale.
The fixed-user check can be replaced by a later user-association migration.

Search normalizes Nominatim `lat`/`lon` and `osm_type`/`osm_id`; `display_name` is
used verbatim as the address source (outer whitespace is trimmed on save).
Missing/invalid save fields produce null coordinates/identity in the normalized
result, keeping its readable label. `place_id` is never used as OSM identity.
See [Nominatim output fields](https://nominatim.org/release-docs/latest/api/Output/).

`POST /api/restaurants` accepts only these JSON fields:

```json
{"name":"Restaurant name","address":"Provider display_name","latitude":42.36,"longitude":-71.05,"osm_id":"node/123"}
```

This is an illustrative contract, not seeded data. Responses are:

- **201**: `{"outcome":"created","restaurant":{"id":1,"user_id":"xyz123",...}}`
- **200**: same record shape with `"outcome":"already_saved"`.
- **422**: FastAPI validation feedback for invalid/missing/extra fields, including client `user_id`.
- **503**: `{"detail":"Restaurant could not be saved. Please try again."}` for database failures.

`restaurant` includes the seven required restaurant fields. PostgreSQL `ON CONFLICT DO NOTHING`
resolves concurrent saves without overwriting the original data; responses wait
for commit. Searching and typing alone never write rows. No retrieval API is added.
Verify entries through SQL, for example:

```sh
docker compose exec -T db psql -U food_maps -d food_maps -c 'SELECT * FROM restaurants;'
docker compose exec -T db psql -U food_maps -d food_maps -c '\d restaurants'
```

Use your configured role/database if they differ. Refresh the browser, restart the
app, and run `docker compose restart db` to check retained data; do not remove the volume.
