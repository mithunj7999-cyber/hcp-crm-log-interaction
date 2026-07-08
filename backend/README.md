# HCP CRM — Backend

AI-First Healthcare CRM backend built with **FastAPI**, **SQLAlchemy**, **Alembic**, and **LangGraph**.

## Quick Start

### 1. Prerequisites
- Python 3.11+
- PostgreSQL running locally

### 2. Create the database

```sql
CREATE DATABASE hcp_crm;
```

### 3. Configure environment

```bash
cd backend
cp .env.example .env
# Edit .env with your actual Postgres credentials & Groq API key
```

### 4. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 5. Run migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "initial schema"

# Apply migration
alembic upgrade head
```

### 6. Seed sample data

```bash
python -m app.seed
```

### 7. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
backend/
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── api/                 # FastAPI route handlers
│   │   ├── hcps.py
│   │   ├── interactions.py
│   │   └── materials.py
│   ├── agent/               # LangGraph agent (Step 2+)
│   ├── core/                # Config & database setup
│   │   ├── config.py
│   │   └── database.py
│   ├── models/              # SQLAlchemy ORM models
│   │   └── models.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   └── schemas.py
│   ├── main.py              # FastAPI app entry point
│   └── seed.py              # Database seeder
├── .env                     # Environment variables (git-ignored)
├── .env.example             # Template for .env
├── alembic.ini              # Alembic configuration
└── requirements.txt         # Python dependencies
```

## API Endpoints

| Method  | Endpoint                       | Description                     |
|---------|--------------------------------|---------------------------------|
| GET     | `/api/health`                  | Health check                    |
| POST    | `/api/hcps/`                   | Create HCP                      |
| GET     | `/api/hcps/?search=`           | List/search HCPs                |
| GET     | `/api/hcps/{id}`               | Get HCP by ID                   |
| POST    | `/api/interactions/`           | Create interaction               |
| GET     | `/api/interactions/?hcp_id=`   | List interactions (filter by HCP)|
| GET     | `/api/interactions/{id}`       | Get interaction by ID            |
| PATCH   | `/api/interactions/{id}`       | Partial update interaction       |
| POST    | `/api/materials/`              | Create material                  |
| GET     | `/api/materials/?search=`      | List/search materials            |
| GET     | `/api/materials/{id}`          | Get material by ID               |
