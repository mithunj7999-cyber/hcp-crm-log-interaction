# hcp-crm-log-interaction

Clear, step-by-step setup and installation instructions for running the HCP <-> CRM interaction logging project locally and in containers.

This repo contains a Python backend (FastAPI + SQLAlchemy + Alembic) and a JavaScript frontend. The README below focuses on practical, reproducible steps to get the project running.

---

## Summary

- Backend: FastAPI (app entrypoint: `app.main:app`), uses SQLAlchemy and Alembic for migrations.
- Frontend: standard Node.js project (assumes `frontend/` with a `package.json`).
- Database: the project uses an external SQL database (default examples use MySQL DSN style).

---

## Prerequisites

- Git
- Python 3.11 (recommended)
- Node.js 16+ and npm (or yarn/pnpm)
- (Optional) Docker & Docker Compose if you prefer containers

---

## Quick setup (development)

Clone the repository and change into it:

```bash
git clone https://github.com/mithunj7999-cyber/hcp-crm-log-interaction.git
cd hcp-crm-log-interaction
```

The instructions assume two top-level folders: `backend/` and `frontend/`. If your repository differs, adapt accordingly.

### Backend (detailed)

1) Create and activate a Python virtual environment

macOS / Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Configure environment variables

- Copy the `.env.example` that exists in `backend/` to `.env` and edit values to match your environment.

```bash
cp .env.example .env
# then edit backend/.env with a text editor
```

Example environment variables (edit for your setup):

```
# backend/.env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hcp_crm?charset=utf8mb4
SECRET_KEY=change-me
FLASK_ENV=development  # not used for FastAPI; keep only if present in your app
PORT=8000
CRM_API_KEY=your_crm_api_key
CRM_API_URL=https://api.crm.example
```

Important: do not commit `.env` to git. Ensure `.gitignore` contains the `.env` entry.

4) Database migrations

If you are starting fresh or the schema changed, run Alembic migrations from the `backend/` directory.

```bash
# from backend/
# generate a migration only if you changed models (optional)
alembic revision --autogenerate -m "some message"
# apply migrations
alembic upgrade head
```

If your project uses a different flow (Django, custom migrate script), use those commands instead.

5) Seed sample data (optional)

If a seeder is provided, run it to create sample data:

```bash
python -m app.seed
```

6) Run the backend server

The backend exposes an ASGI app. The default entrypoint in this repo is `app.main:app`. Start with uvicorn in development:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open API docs at: http://localhost:8000/docs

If your project uses Gunicorn (production) or a different entrypoint, use the appropriate command (for example `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`).


### Frontend (detailed)

If a `frontend/` folder exists with `package.json`:

1) Install dependencies

```bash
cd ../frontend
npm install
# or: yarn install
# or: pnpm install
```

2) Start development server

```bash
npm run dev
# or
npm start
```

3) Build for production

```bash
npm run build
```

If the built assets should be served by the backend, follow the repo-specific copy/serve instructions.

---

## Running tests

Backend (Python):

```bash
cd backend
pytest
```

Frontend (JS):

```bash
cd frontend
npm test
```

Adjust test commands if your repo uses a different test runner.

---

## Linting & Formatting

Recommended tools:

- Python: black, isort, flake8
- JavaScript: eslint, prettier

Example commands:

```bash
# Python
cd backend
black .
flake8

# JavaScript
cd ../frontend
npm run lint
```

---

## Docker (optional)

If you prefer to run the project in containers, add or update `Dockerfile` and `docker-compose.yml` at the repo root. A typical quick command to run (after writing compose files) is:

```bash
docker-compose up --build
```

The compose file should create three services at minimum: `backend`, `frontend` (if needed), and a database (MySQL/Postgres). Configure environment variables for each service via an `.env` file or `docker-compose.override.yml`.

---

## Deployment notes

- Use a production ASGI server (Gunicorn with Uvicorn workers or Uvicorn + process manager) behind a reverse proxy.
- Store secrets with your hosting provider's secret manager and **never** commit them to source control.
- Build frontend assets and upload to a CDN or serve them from the backend/static server.

---

## Troubleshooting

- Dependency install failures: confirm Python and Node versions and that you activated the virtual environment.
- Database connection issues: confirm `DATABASE_URL` is correct and the DB server accepts connections from your host.
- Migrations fail: inspect the Alembic versions directory and error output; if in doubt, share the error logs.

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make changes and add tests where appropriate
4. Commit and push: `git push origin feature/my-change`
5. Open a Pull Request and describe the change

Please follow the project's code style and keep README up to date with any changes to start commands.

---

## License

This repository currently does not include a LICENSE file. If you want to make this project open-source, add a LICENSE (for example, the MIT License) and mention it here.

---

If you want, I can:
- Update the README to include exact commands discovered in the repository (for example, confirm the frontend start script and backend entrypoint) — I inspected `backend/README.md` and used its details above. If you want the README to reflect exact, live file contents for scripts and package.json commands, I can scan the repo and update the README accordingly.
