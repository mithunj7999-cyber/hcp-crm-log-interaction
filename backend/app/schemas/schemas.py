"""
HCP CRM — Pydantic Schemas for API request / response validation.
"""

from datetime import date, time, datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


# ── Enums (mirror DB enums for API layer) ───────────────────────────────

class InteractionTypeEnum(str, Enum):
    MEETING = "Meeting"
    CALL = "Call"
    EMAIL = "Email"
    VIDEO_CALL = "Video Call"
    CONFERENCE = "Conference"
    OTHER = "Other"


class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class MaterialTypeEnum(str, Enum):
    BROCHURE = "Brochure"
    SAMPLE = "Sample"
    CLINICAL_DATA = "Clinical Data"
    PRESENTATION = "Presentation"
    VIDEO = "Video"
    OTHER = "Other"


# ── HCP Schemas ─────────────────────────────────────────────────────────

class HCPBase(BaseModel):
    name: str = Field(..., max_length=255)
    specialty: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPResponse(HCPBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Interaction Schemas ─────────────────────────────────────────────────

class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: InteractionTypeEnum = InteractionTypeEnum.MEETING
    date: date
    time: Optional[time] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[SentimentEnum] = SentimentEnum.NEUTRAL
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    """Partial update — every field is optional."""
    hcp_id: Optional[int] = None
    interaction_type: Optional[InteractionTypeEnum] = None
    date: Optional[date] = None
    time: Optional[time] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[SentimentEnum] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Material Schemas ────────────────────────────────────────────────────

class MaterialBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: MaterialTypeEnum = MaterialTypeEnum.BROCHURE
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chat / AI Schemas ──────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """Incoming message from the AI chat panel."""
    message: str = Field(..., min_length=1, description="Natural-language summary of the interaction")


class ChatResponse(BaseModel):
    """Response from the AI agent after processing a chat message."""
    reply: str
    extracted_data: Optional[dict] = None
    suggestions: Optional[List[str]] = None
