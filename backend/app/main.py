"""
HCP CRM Backend — FastAPI Application Entry Point.
"""

import app.compat.patches  # noqa: F401 — patch blocked native deps before langchain loads

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.api import hcps, interactions, materials, chat

settings = get_settings()

app = FastAPI(
    title="HCP CRM — AI-First Healthcare CRM",
    description="Backend API for logging and managing HCP interactions with AI-powered assistance.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)
# ── CORS (allow React dev server) ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ───────────────────────────────────────────────────
app.include_router(hcps.router,         prefix="/api")
app.include_router(interactions.router,  prefix="/api")
app.include_router(materials.router,     prefix="/api")
app.include_router(chat.router,          prefix="/api")


# ── Health Check ────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
def health_check():
    """Quick health check endpoint."""
    return {"status": "ok", "service": "hcp-crm-backend"}
