"""Alerts API: list alerts per service or globally."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Service, Alert
from ..schemas import AlertResponse

router = APIRouter(tags=["alerts"])


def _get_service_or_404(db: Session, id: UUID) -> Service:
    service = db.query(Service).filter(Service.id == str(id)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.get("/services/{id}/alerts", response_model=list[AlertResponse])
def list_service_alerts(
    id: UUID,
    db: Session = Depends(get_db),
    state: str | None = Query(None, pattern="^(ACTIVE|RESOLVED)$"),
):
    """List alerts for a service. Optional filter: state=ACTIVE|RESOLVED."""
    service = _get_service_or_404(db, id)
    q = db.query(Alert).filter(Alert.service_id == str(service.id))
    if state is not None:
        q = q.filter(Alert.state == state)
    q = q.order_by(Alert.triggered_at.desc())
    return q.all()


@router.get("/alerts", response_model=list[AlertResponse])
def list_all_alerts(
    db: Session = Depends(get_db),
    state: str | None = Query(None, pattern="^(ACTIVE|RESOLVED)$"),
):
    """List all alerts across all services. Optional filter: state=ACTIVE|RESOLVED."""
    q = db.query(Alert)
    if state is not None:
        q = q.filter(Alert.state == state)
    q = q.order_by(Alert.triggered_at.desc())
    return q.all()
