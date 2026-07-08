"""
HCP CRM — SQLAlchemy ORM Models.

Tables:
  • hcps          — Healthcare Professional profiles
  • interactions  — Logged interactions with HCPs
  • materials     — Pharma materials / samples catalog
"""

import enum
from datetime import datetime, date, time

from sqlalchemy import (
    Column, Integer, String, Text, Date, Time, DateTime,
    Enum as SAEnum, ForeignKey, ARRAY,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ── Enums ───────────────────────────────────────────────────────────────

class InteractionType(str, enum.Enum):
    """Allowed interaction types."""
    MEETING = "Meeting"
    CALL = "Call"
    EMAIL = "Email"
    VIDEO_CALL = "Video Call"
    CONFERENCE = "Conference"
    OTHER = "Other"


class Sentiment(str, enum.Enum):
    """Observed / inferred HCP sentiment."""
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class MaterialType(str, enum.Enum):
    """Material category."""
    BROCHURE = "Brochure"
    SAMPLE = "Sample"
    CLINICAL_DATA = "Clinical Data"
    PRESENTATION = "Presentation"
    VIDEO = "Video"
    OTHER = "Other"


# ── Models ──────────────────────────────────────────────────────────────

class HCP(Base):
    """Healthcare Professional profile."""

    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialty = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<HCP id={self.id} name={self.name!r}>"


class Interaction(Base):
    """A logged interaction between a field rep and an HCP."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)

    interaction_type = Column(
        SAEnum(InteractionType, name="interaction_type_enum", create_constraint=True),
        nullable=False,
        default=InteractionType.MEETING,
    )
    date = Column(Date, nullable=False, default=date.today)
    time = Column(Time, nullable=True, default=None)
    attendees = Column(Text, nullable=True)          # comma-separated or JSON string
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True)    # comma-separated material names
    samples_distributed = Column(Text, nullable=True) # comma-separated sample names
    sentiment = Column(
        SAEnum(Sentiment, name="sentiment_enum", create_constraint=True),
        nullable=True,
        default=Sentiment.NEUTRAL,
    )
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<Interaction id={self.id} hcp_id={self.hcp_id} type={self.interaction_type}>"


class Material(Base):
    """Pharma materials & samples catalog."""

    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(
        SAEnum(MaterialType, name="material_type_enum", create_constraint=True),
        nullable=False,
        default=MaterialType.BROCHURE,
    )
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Material id={self.id} name={self.name!r}>"
