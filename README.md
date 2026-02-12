# Mental Wellness — Full Stack App

AI-powered mental wellness web app with **User**, **Professional**, and **Admin** roles. Built from Stitch ZIP exports, merged into a single Next.js + FastAPI stack.

## Architecture Overview

- **Frontend**: Next.js (App Router) + Tailwind. Role-based routes: `/user`, `/professional`, `/admin`.
- **Backend**: FastAPI. REST APIs for auth, assessment, chat, triage, admin (no animations/motion).
- **Database**: SQLite by default (dev); PostgreSQL for production. Separate identity and clinical data; encryption-ready fields.
- **AI**: Pluggable chatbot adapter; sentiment + risk scoring; mock model first.
- **Voice**: WebRTC-ready UI; call lifecycle in professional session page.
- **Notifications**: Email service (mock in dev); in-app notifications.

## Setup

### Prerequisites

- Node 18+, Python 3.11+
- (Optional) PostgreSQL for production

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env: SECRET_KEY, DATABASE_URL (postgresql for prod)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: **http://localhost:8000** — Docs: **http://localhost:8000/docs**

### 2. Frontend

```bash
cd web
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Frontend: **http://localhost:3000**

### 3. Seed data

From backend directory:

```bash
cd backend
python scripts/seed.py
```

Dummy accounts:

| Role         | Email              | Password |
|-------------|--------------------|----------|
| Admin       | admin@wellness.local | admin123 |
| User        | user@wellness.local  | user123  |
| Professional (approved) | pro2@wellness.local | pro123  |
| Professional (pending)   | pro@wellness.local  | pro123  |

## API Documentation

- **Health**: `GET /health`
- **Auth**:  
  - `POST /auth/signup` — body: `{ "email?", "phone?", "password?", "role": "user"|"professional", "is_anonymous?": false }`  
  - `POST /auth/login` — body: `{ "email?", "password?" }` (empty for anonymous)  
  - `GET /auth/me` — header: `Authorization: Bearer <token>`
- **Assessment**: `POST /assessment/submit` — body: `{ "answers": { "sleep": "...", "mood": "...", "support": "..." } }` → returns `{ "redirect": "/user"|"/user/support", "triage_label?" }`
- **Chat**: `POST /chat/message` — body: `{ "message": "..." }` → `{ "reply": "..." }`

Triage is internal (Green/Yellow/Red). Users are redirected by severity; labels are not exposed in UI.

## Minimal end-to-end flow

1. **User signup** → `/role` → choose “Seeking support” → `/login` → Continue Anonymously or Sign up with Email.
2. **Assessment** → `/user` → “Start quick check” → `/user/assessment` → submit answers → backend triage → redirect to `/user` or `/user/support`.
3. **Chat** → `/user/chat` → send message → backend mock chatbot reply.
4. **Admin queue** → `/admin` (live queue, assign users to professionals; real-time via WebSockets when implemented).

## Project layout

```
PRTAB/
├── web/                 # Next.js
│   ├── app/
│   │   ├── user/         # User pages (home, chat, wellness, support, assessment)
│   │   ├── professional/  # Dashboard, verify, session/[id], cases, schedule)
│   │   ├── admin/        # Triage dashboard, analytics
│   │   ├── role/         # Role selection
│   │   └── login/        # Signup / login
│   └── lib/              # api, types
├── backend/              # FastAPI
│   ├── app/
│   │   ├── routers/      # auth, assessment, chat
│   │   ├── ai/          # chatbot, risk (triage)
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   └── database.py
│   └── main.py
├── scripts/
│   ├── dev.bat          # Start backend + frontend (Windows)
│   └── seed.py          # Dummy users, professionals
├── STITCH_ZIP_MAPPING.md
└── .env.example
```

## Non-functional

- Data privacy first; anonymization by default.
- Encryption-ready fields; rate limiting and audit logging to be extended.
- No animations or motion elements added.

## Production

- Set `DATABASE_URL` to PostgreSQL.
- Set `SECRET_KEY` to a long random value.
- Set `CORS_ORIGINS` to your frontend origin(s).
- Configure `OPENAI_API_KEY` and/or email provider as needed.
