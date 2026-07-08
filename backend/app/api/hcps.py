"""
HCP CRM — API routes for HCPs.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import HCP
from app.schemas.schemas import HCPCreate, HCPResponse

router = APIRouter(prefix="/hcps", tags=["HCPs"])


@router.post("/", response_model=HCPResponse, status_code=201)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db)):
    """Create a new Healthcare Professional profile."""
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.get("/", response_model=List[HCPResponse])
def list_hcps(
    search: Optional[str] = Query(None, description="Search HCPs by name"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List HCPs with optional name search (for the searchable select)."""
    query = db.query(HCP)
    if search:
        query = query.filter(HCP.name.ilike(f"%{search}%"))
    return query.order_by(HCP.name).offset(skip).limit(limit).all()


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Get a single HCP by ID."""
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp
