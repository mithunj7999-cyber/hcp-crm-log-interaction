"""
HCP CRM — API routes for Interactions.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Interaction
from app.schemas.schemas import InteractionCreate, InteractionUpdate, InteractionResponse

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post("/", response_model=InteractionResponse, status_code=201)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """Create a new interaction record."""
    interaction = Interaction(**payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.get("/", response_model=List[InteractionResponse])
def list_interactions(
    hcp_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List interactions, optionally filtered by hcp_id."""
    query = db.query(Interaction)
    if hcp_id is not None:
        query = query.filter(Interaction.hcp_id == hcp_id)
    return query.order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a single interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.patch("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an interaction (used by the AI edit_interaction tool)."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction
