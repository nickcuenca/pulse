"""Metrics API: ingest and query metrics. Triggers alert evaluation on POST."""

from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Service, Metric
from ..schemas import MetricCreate, MetricResponse
from ..evaluation import evaluate_alert_rules

router = APIRouter(prefix="/services", tags=["metrics"])


def _get_service_or_404(db: Session, id: UUID) -> Service:
    service = db.query(Service).filter(Service.id == str(id)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/{id}/metrics", response_model=MetricResponse)
def ingest_metric(
    id: UUID,
    body: MetricCreate,
    db: Session = Depends(get_db),
):
    """Ingest a metric datapoint. Runs alert evaluation for matching rules."""
    service = _get_service_or_404(db, id)
    metric = Metric(
        service_id=str(service.id),
        name=body.name,
        value=body.value,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)

    evaluate_alert_rules(db, str(service.id), body.name, body.value)

    return metric


@router.get("/{id}/metrics", response_model=list[MetricResponse])
def get_metrics(
    id: UUID,
    db: Session = Depends(get_db),
    metric_name: str | None = Query(None),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get metrics for a service. Optional filters: metric_name, start, end, limit."""
    service = _get_service_or_404(db, id)
    q = db.query(Metric).filter(Metric.service_id == str(service.id))
    if metric_name is not None:
        q = q.filter(Metric.name == metric_name)
    if start is not None:
        q = q.filter(Metric.timestamp >= start)
    if end is not None:
        q = q.filter(Metric.timestamp <= end)
    q = q.order_by(Metric.timestamp.desc()).limit(limit)
    return q.all()
