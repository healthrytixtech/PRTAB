# PRISMA (PRTAB) — Mental Wellness Web App

Production-oriented full-stack prototype for a privacy-first mental wellness experience.

- **Frontend**: Next.js (`web/`)
- **Backend API**: FastAPI (`backend/`)
- **Local orchestration**: Docker Compose (`docker-compose.yml`)
- **CI/CD**: GitHub Actions builds + tests + pushes images to GHCR (`.github/workflows/ci-cd.yml`)

## Quick start (recommended)

Run the whole stack with Docker:

```bash
docker compose up --build
```

- **Frontend**: `http://localhost:3000`
- **Backend**: `http://localhost:8000`
- **Backend docs**: `http://localhost:8000/docs`

## Local dev (without Docker)

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend reads environment variables from `backend/.env` (see `backend/app/config.py`).

### Frontend (Next.js)

```bash
cd web
npm ci
npm run dev
```

The frontend is built to use `NEXT_PUBLIC_API_URL` (see `docker-compose.yml` for the default local value).

## Core API endpoints

- **Health**: `GET /health`
- **Auth**:
  - `POST /auth/signup`
  - `POST /auth/login`
  - `GET /auth/me` (requires `Authorization: Bearer <token>`)
- **Assessment**: `POST /assessment/submit`
- **Chat**: `POST /chat/message`
- **Admin**:
  - `GET /admin/queue` (admin only)
  - `GET /admin/analytics` (admin only)
- **Professional requests**:
  - `POST /chat-requests` (authenticated user)
  - `GET /chat-requests/mine` (authenticated user)
  - `GET /chat-requests` (admin only)
  - `PUT /chat-requests/{id}/assign` (admin only)
  - `PUT /chat-requests/{id}/schedule` (professional only)

## Running tests

Backend tests (pytest):

```bash
cd backend
.venv\Scripts\python.exe -m pytest -q
```

## Environment variables (high level)

Backend (`backend/.env`):
- **`DATABASE_URL`**: defaults to SQLite; use Postgres in production (e.g. `postgresql+psycopg2://...`)
- **`SECRET_KEY`**: required for legacy JWT signing (use a long random value)
- **`CORS_ORIGINS`**: comma-separated origins (set to your deployed frontend URL(s))
- **`CLERK_JWKS_URL`**: if using Clerk JWT verification on backend

Frontend (`web/` build/runtime):
- **`NEXT_PUBLIC_API_URL`**: backend base URL reachable from the browser
- **Clerk**: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` (if enabled)

## CI/CD (GitHub Actions)

Workflow: `./.github/workflows/ci-cd.yml`

- Runs **frontend typecheck + lint**
- Runs **backend pytest**
- Builds and pushes Docker images to **GitHub Container Registry (GHCR)**
- Deploy step is scaffolded (SSH-based) and can be enabled when a server is ready

## Repo layout

```text
PRTAB/
├── backend/                 # FastAPI service
├── web/                     # Next.js app
├── docker-compose.yml        # Local orchestration
├── .github/workflows/ci-cd.yml
└── STITCH_ZIP_MAPPING.md     # Mapping from Stitch export → app structure
```
