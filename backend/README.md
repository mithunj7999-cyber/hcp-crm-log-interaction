# HCP CRM — Backend

AI-First Healthcare CRM backend built with **FastAPI**, **SQLAlchemy**, **Alembic**, and **LangGraph**.

## Quick Start

### 1. Prerequisites
- Python 3.11+

### 2. Configure environment

```bash
cd backend
cp .env.example .env
# Update `.env` to set your database connection string and Groq API key
```

Note: This project defaults the `DATABASE_URL` to a MySQL DSN placeholder. Edit `.env` and set `DATABASE_URL` to your MySQL connection string. Example MySQL DSN:

```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hcp_crm?charset=utf8mb4
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
