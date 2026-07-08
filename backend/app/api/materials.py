"""
HCP CRM — API routes for Materials.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Material
from app.schemas.schemas import MaterialCreate, MaterialResponse

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("/", response_model=MaterialResponse, status_code=201)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    """Add a new material to the catalog."""
    material = Material(**payload.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/", response_model=List[MaterialResponse])
def list_materials(
    search: Optional[str] = Query(None, description="Search materials by name"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List materials with optional name search."""
    query = db.query(Material)
    if search:
        query = query.filter(Material.name.ilike(f"%{search}%"))
    return query.order_by(Material.name).offset(skip).limit(limit).all()


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: int, db: Session = Depends(get_db)):
    """Get a single material by ID."""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material
