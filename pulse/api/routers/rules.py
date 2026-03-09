"""Alert rules API: create and list rules per service."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Service, AlertRule
from ..schemas import AlertRuleCreate, AlertRuleResponse

router = APIRouter(prefix="/services", tags=["rules"])


def _get_service_or_404(db: Session, id: UUID) -> Service:
    service = db.query(Service).filter(Service.id == str(id)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/{id}/rules", response_model=AlertRuleResponse)
def create_rule(
    id: UUID,
    body: AlertRuleCreate,
    db: Session = Depends(get_db),
):
    """Create an alert rule for a service."""
    service = _get_service_or_404(db, id)
    rule = AlertRule(
        service_id=str(service.id),
        metric_name=body.metric_name,
        threshold=body.threshold,
        condition=body.condition,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{id}/rules", response_model=list[AlertRuleResponse])
def list_rules(id: UUID, db: Session = Depends(get_db)):
    """List alert rules for a service."""
    service = _get_service_or_404(db, id)
    return db.query(AlertRule).filter(AlertRule.service_id == str(service.id)).all()
