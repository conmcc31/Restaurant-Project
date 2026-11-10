# Task 001 — Project Setup

## Goal

Establish a reproducible local development foundation for Food Maps with a React/Vite frontend, Python/FastAPI backend, and PostgreSQL database. This task is infrastructure scaffolding only; do not implement restaurant features.

## Context and Dependencies

- Read `project-thesis.md` for the product vision, stack, and architectural principles.
- Read `AGENTS.md` for agent workflow and reporting requirements.
- Assume this is the first implementation task; preserve any existing repository files rather than overwriting them without review.
- Use the current repository as the monorepo root; **do not create an extra nested repository directory**.

## In Scope

- Create `frontend/` and `backend/` with conventional, simple project layouts.
- Scaffold a **React + Vite + TypeScript** frontend and configure **Tailwind CSS**.
- Scaffold a **Python + FastAPI** backend with a minimal application entry point and a health endpoint (`GET /health`) solely for setup verification.
- Configure a PostgreSQL service using **Docker Compose** and a persistent named volume.
- Add SQLAlchemy and a PostgreSQL driver, and a minimal, verifiable database connectivity mechanism (for example, a startup check or a simple script). Do **not** create domain tables.
- Prepare backend dependencies for later migrations with Alembic, without creating restaurant migrations or models.
- Add basic development-quality tools: pytest + Ruff for the backend, and ESLint plus Vitest/React Testing Library for the frontend. Install/configure tooling; extensive feature tests are not required here.
- Add environment variable examples (`.env.example` or equivalent), a safe `.gitignore`, and reproducible local setup instructions in `README.md`.
- Provide commands to run frontend and backend in development mode and to start/stop PostgreSQL.

## Out of Scope

- Restaurant, visit, or user database models and tables
- Domain migrations or seed data
- Restaurant-related backend API routes, CRUD behavior, or business logic
- Map integration, restaurant search, sidebar, or finished frontend design
- Authentication, authorization, friend connections, and social functionality
- Production deployment, containerization of the entire app, or CI/CD

**Exception:** `GET /health` is allowed as a setup-only endpoint; do not interpret that exception as permission to build other API routes.

## Implementation Constraints

- Use the technologies established in `project-thesis.md`.
- Prefer minimal conventional scaffolding; do not introduce Redux, a service mesh, complex repository tooling, or additional infrastructure without a documented need.
- Use a local Python virtual environment and documented backend install commands; keep generated environments and dependencies out of Git.
- Use package manifests and lockfiles where supported; avoid unpinned ad hoc install instructions.
- Place database credentials and connection strings in environment variables, and commit examples rather than real secrets.
- Set an explicit local database port and document how to change it if it conflicts with an existing PostgreSQL installation.
- Configure cross-origin access only as necessary for the documented local frontend URL; avoid unrestricted CORS by default.
- Do not require a geolocation, mapping, or search API key at setup time.
- If choosing a nontrivial alternative to an established stack element, stop and request approval before implementing the change.

## Acceptance Criteria

- [ ] The repository contains separate `frontend/` and `backend/` directories, with no unintended nested project root.
- [ ] Frontend dependencies install successfully, and the Vite app starts and renders its starter page.
- [ ] Backend dependencies install successfully, and FastAPI starts locally.
- [ ] `GET /health` returns a successful response (for example, HTTP 200 with a small JSON payload).
- [ ] `docker compose up -d` starts PostgreSQL, and its health/readiness status can be checked.
- [ ] The backend can establish a connection to the running PostgreSQL database.
- [ ] Environment configuration is documented and secrets are excluded from version control.
- [ ] `README.md` documents prerequisites, install/setup, run, test/lint commands, and shutdown.
- [ ] The basic configured frontend/backend lint and test commands run successfully, or any unmet check is explicitly reported with the reason.
- [ ] No restaurant models, domain APIs, or completed product UI have been added.

## Verification

Perform and report the results of these checks, adapting commands to the actual manifests created:

1. Start the database with Docker Compose and confirm its health/readiness.
2. Start the backend and request `GET /health`.
3. Run the database connectivity mechanism and confirm a successful connection.
4. Start the frontend and verify it loads in a browser (if browser access is unavailable, report that limitation and at least confirm startup/build output).
5. Run the configured lint/test commands and a frontend production build.
6. Check repository status for accidentally committed secrets, local virtual environments, `node_modules`, or generated files.

Do not claim visual/manual checks were completed if the environment did not permit them. Do not mark a criterion complete solely because a command was written into the README.

## Completion Report

At the end of the task, provide:

- **Summary:** What was created and configured.
- **Files:** Key new or modified files.
- **Commands:** Exact startup and verification commands that were run.
- **Acceptance criteria:** Passed, failed, or not verified for each item.
- **Decisions:** Framework versions and any non-obvious choices.
- **Deviations/limitations:** Scope changes, blockers, unverified behavior, and remaining manual steps.
- **Next task:** Recommended follow-up, without implementing it as part of this task.
