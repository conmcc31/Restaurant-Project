# Food Maps

Local development foundation for the single-user Food Maps demo. This setup includes
a React starter page, FastAPI health endpoint, and PostgreSQL. Product features are
defined in [the project thesis](spec-files/project-thesis.md); none are implemented yet.

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
```

`.env` supplies Compose's database user, password, database name, and host port.
`backend/.env` supplies `DATABASE_URL` and `FRONTEND_ORIGIN`; the backend reads it
relative to its source directory. Existing process environment variables take precedence.
Only example values are tracked. Change the local example password in both files
before using personal credentials. URL-encode special characters in the connection URL.
No frontend environment variables or mapping/search keys are needed for this task.

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

Open <http://localhost:5173>. The frontend is a setup-only starter page.
Vite uses a strict port so a conflict cannot silently change the documented CORS origin.
FastAPI is at <http://127.0.0.1:8000>, with generated API documentation at `/docs`.
The only application route is `GET /health`; it checks the process independently of
database availability. CORS permits only `http://localhost:5173`, with GET requests.
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

`alembic current` needs PostgreSQL running. An empty revision result is expected:
Alembic is configured to read `DATABASE_URL`, but there are no revisions or domain
models. Do not generate/apply a migration until a subsequent task defines the schema.

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
SQLAlchemy/Psycopg for PostgreSQL, Alembic for future migrations, Pydantic Settings
for environment loading, pytest/httpx for API tests, and Ruff for quality checks.

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
