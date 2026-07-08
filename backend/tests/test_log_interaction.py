import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent import tools
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
