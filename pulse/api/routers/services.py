"""Services API: register, list, get by id."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Service
from ..schemas import ServiceCreate, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceResponse)
def register_service(body: ServiceCreate, db: Session = Depends(get_db)):
    """Register a new service."""
    existing = db.query(Service).filter(Service.name == body.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Service with this name already exists")
    service = Service(name=body.name, description=body.description)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    """List all services."""
    return db.query(Service).all()


@router.get("/{id}", response_model=ServiceResponse)
def get_service(id: UUID, db: Session = Depends(get_db)):
    """Get service by id."""
    service = db.query(Service).filter(Service.id == str(id)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
