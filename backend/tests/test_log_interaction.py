import json
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent import graph, tools
from app.core.database import Base
from app.models.models import HCP


def test_log_interaction_creates_hcp_when_missing(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(tools, "SessionLocal", TestingSessionLocal)

    result = json.loads(
        tools.log_interaction.func(
            hcp_name="Dr. Smith",
            topics_discussed="OncoBoost efficacy",
            sentiment="Positive",
        )
    )

    assert result["success"] is True

    with TestingSessionLocal() as session:
        hcp = session.query(HCP).filter(HCP.name == "Dr. Smith").one()
        assert hcp.name == "Dr. Smith"


def test_build_llm_uses_groq_model_name(monkeypatch):
    captured = {}

    class DummyChatGroq:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def bind_tools(self, tools):
            return self

        def invoke(self, messages):
            return "ok"

    monkeypatch.setattr(graph, "ChatGroq", DummyChatGroq)
    monkeypatch.setattr(graph.settings, "GROQ_API_KEY", "test-key")
    monkeypatch.setattr(graph.settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
    monkeypatch.setattr(graph.settings, "GROQ_FALLBACK_MODEL", "llama-3.3-70b-versatile")

    graph._build_llm()

    assert captured["model"] == "llama-3.3-70b-versatile"
