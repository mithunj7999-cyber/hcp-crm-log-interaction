# HCP CRM — Project Documentation

Version: 1.0
Repository: https://github.com/mithunj7999-cyber/hcp-crm-log-interaction
Date: 2026-07-09
Author: Generated for mithunj7999-cyber

## 1. Introduction

This project provides a backend service and a frontend UI for logging, viewing, and managing interactions between Healthcare Professionals (HCPs) and a CRM system.

Primary goals:
- Capture HCP—CRM interaction events.
- Provide structured APIs for creating, querying, and updating interactions.
- Offer a simple frontend for users to view and manage recorded data.

## 2. Tech stack — overview and responsibilities

- Python 3.11+ (backend)
  - FastAPI: web framework and automatic OpenAPI docs (ASGI).
  - SQLAlchemy: ORM for database models.
  - Alembic: database migrations.
  - Uvicorn: ASGI server for development and production (via Gunicorn+Uvicorn workers).
  - Additional libs: dependencies listed in backend/requirements.txt.

- Database
  - MySQL (example connection strings use MySQL DSN), but SQLAlchemy allows switching to Postgres/SQLite with config changes.

- JavaScript (frontend)
  - Node.js + npm (or yarn/pnpm).
  - A typical SPA or client app (package.json in frontend/). The frontend consumes the backend API.

- Optional components
  - Docker & docker-compose for containerized local runs.
  - LangGraph (agent folder present) — optional / advanced functionality for agent features (if configured).

## 3. What the project implements

- Persistent storage of HCPs and interactions.
- REST API endpoints for:
  - Health check
  - Create / list / search HCPs
  - Create / list / retrieve / patch interactions
  - Create / list / retrieve materials
- Database migrations and seeding utilities.
- A frontend application to interact with the backend API.

## 4. Architecture (logical)

- backend/
  - app/main.py (FastAPI app entrypoint)
  - app/api/* (route handlers: hcps.py, interactions.py, materials.py)
  - app/core/* (config/database setup)
  - app/models (SQLAlchemy models)
  - alembic/ (migrations)
  - seed.py (sample data seeder)

- frontend/
  - package.json, source files (UI that calls backend APIs)

Runtime:
- API served by FastAPI (uvicorn/gunicorn).
- Frontend served by a development server (npm run dev) or as built static assets served by backend or CDN.
- Database connected via DATABASE_URL environment variable.

## 5. Installation (development) — condensed

Prerequisites:
- Git
- Python 3.11
- Node.js 16+ and npm/yarn/pnpm
- (Optional) Docker & Docker Compose

Steps (local, no Docker)

1. Clone:

```bash
git clone https://github.com/mithunj7999-cyber/hcp-crm-log-interaction.git
cd hcp-crm-log-interaction
```

2. Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .\.venv\Scripts\Activate.ps1 on Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# Edit backend/.env with your database and API keys

# Run migrations
alembic upgrade head

# Optional seed
python -m app.seed

# Run server (dev)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Frontend:

```bash
cd ../frontend
npm install
npm run dev     # or npm start
```

Open API docs: http://localhost:8000/docs

## 6. Environment variables (example)

backend/.env (example)

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hcp_crm?charset=utf8mb4
SECRET_KEY=change-me
PORT=8000
CRM_API_KEY=your_crm_api_key
CRM_API_URL=https://api.crm.example
```

Never commit secrets. Add `.env` to .gitignore.

## 7. API — main endpoints and examples

Base URL (dev): http://localhost:8000

Health check:
- GET /api/health
  Example:
  curl http://localhost:8000/api/health

Create HCP:
- POST /api/hcps/
  Body (JSON):
  {
    "name": "Dr. Jane Doe",
    "email": "jane@example.org",
    "organization": "Example Hospital"
  }
  Example:
  curl -X POST http://localhost:8000/api/hcps/ -H "Content-Type: application/json" -d '{"name":"Dr. Jane","email":"jane@example.org","organization":"EH"}'

List/search HCPs:
- GET /api/hcps/?search=Jane
  Example:
  curl "http://localhost:8000/api/hcps/?search=Jane"

Create Interaction:
- POST /api/interactions/
  Body (JSON):
  {
    "hcp_id": 1,
    "type": "call",
    "notes": "Discussed product X",
    "timestamp": "2026-07-09T10:00:00Z"
  }
  Example:
  curl -X POST http://localhost:8000/api/interactions/ -H "Content-Type: application/json" -d '{"hcp_id":1,"type":"call","notes":"Discussed product X","timestamp":"2026-07-09T10:00:00Z"}'

List interactions:
- GET /api/interactions/?hcp_id=1
  Example:
  curl "http://localhost:8000/api/interactions/?hcp_id=1"

Get interaction:
- GET /api/interactions/{id}

PATCH interaction:
- PATCH /api/interactions/{id}
  Body: JSON with partial updates.

Materials:
- POST /api/materials/
- GET /api/materials/?search=

## 8. Example workflow (end-to-end)

1) Start backend and frontend.
2) Create an HCP:
   curl -X POST http://localhost:8000/api/hcps/ -H "Content-Type: application/json" -d '{"name":"Dr. John","email":"john@hosp.org"}'
3) Record an interaction:
   curl -X POST http://localhost:8000/api/interactions/ -H "Content-Type: application/json" -d '{"hcp_id":1,"type":"email","notes":"Sent follow-up materials","timestamp":"2026-07-09T12:00:00Z"}'
4) Verify:
   curl "http://localhost:8000/api/interactions/?hcp_id=1"

## 9. Testing, linting, formatting

- Backend tests:
  cd backend
  pytest

- Frontend tests:
  cd frontend
  npm test

- Linting:
  Backend: black, flake8, isort
  Frontend: eslint, prettier

## 10. Docker (optional)

Create Dockerfiles for backend and frontend and a docker-compose.yml with services:
- backend (build, env vars, ports)
- frontend (build or dev server)
- db (mysql/postgres)

Quick command (after writing compose file):

docker-compose up --build

## 11. Deployment notes

- Use production ASGI servers (Gunicorn + Uvicorn workers) and a reverse proxy (Nginx).
- Configure secrets via the hosting platform secret manager.
- Serve built frontend assets from a CDN or backend static server for best performance.

## 12. Troubleshooting

- “Cannot connect to DB”: verify DATABASE_URL, DB reachable, credentials correct.
- “Migrations failed”: check Alembic versions and model changes; inspect error output.
- “Missing environment variables”: ensure .env exists and variables loaded.

## 13. Future improvements / roadmap

- Add authentication/authorization (OAuth2/JWT).
- Add pagination, filtering, and rate-limiting to API endpoints.
- Add CI (GitHub Actions) for tests and lint checks.
- Add e2e tests for frontend + backend.
- Add more robust seeder and sample data.

## 14. License

This repository currently does not include a LICENSE file. Add one (e.g., MIT) if you want to make the project open-source.

---

### Appendix A — Convert to PDF (quick methods)

Method A — Pandoc (recommended)
1) Install pandoc and a PDF engine (e.g., LaTeX distribution or wkhtmltopdf).
2) Save this file as `docs/HCP-CRM-Documentation.md` (already added to repo).
3) Run:

```bash
pandoc docs/HCP-CRM-Documentation.md -o HCP-CRM-Documentation.pdf --metadata title="HCP CRM — Project Documentation"
```

Method B — Browser Print to PDF (fast)
1) Open the rendered Markdown on GitHub:
   https://github.com/mithunj7999-cyber/hcp-crm-log-interaction/blob/main/docs/HCP-CRM-Documentation.md
2) Use your browser: File → Print → Save as PDF.

Method C — GitHub Actions (automate)
- I can add a GitHub Action that converts docs/*.md to PDF on push and commits the generated PDF to `docs/`.
- Tell me if you want me to add that workflow — it will create `docs/HCP-CRM-Documentation.pdf` automatically on the next push or workflow run.

---

If you'd like, I can now:
- Add the GitHub Action to auto-build and commit the PDF (so you get a direct download link automatically), or
- Produce the PDF here and attach it (if attachments are allowed).