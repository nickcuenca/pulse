"""Alert evaluation pipeline: run after metric ingestion."""

from datetime import datetime
from sqlalchemy.orm import Session

from .models import Alert, AlertRule


def evaluate_alert_rules(
    db: Session,
    service_id: str,
    metric_name: str,
    metric_value: float,
) -> None:
    """
    After a metric is ingested, fetch matching rules and create/resolve alerts.
    - If value breaches threshold and no ACTIVE alert for that rule → create Alert (ACTIVE).
    - If value no longer breaches and ACTIVE alert exists → set RESOLVED, resolved_at=now.
    """
    rules = (
        db.query(AlertRule)
        .filter(
            AlertRule.service_id == service_id,
            AlertRule.metric_name == metric_name,
        )
        .all()
    )

    for rule in rules:
        breached = _is_breached(rule.condition, rule.threshold, metric_value)
        active_alert = (
            db.query(Alert)
            .filter(
                Alert.rule_id == rule.id,
                Alert.state == "ACTIVE",
            )
            .first()
        )

        if breached and not active_alert:
            alert = Alert(
                rule_id=rule.id,
                service_id=service_id,
                metric_value=metric_value,
                state="ACTIVE",
            )
            db.add(alert)
        elif not breached and active_alert:
            active_alert.state = "RESOLVED"
            active_alert.resolved_at = datetime.utcnow()
            db.add(active_alert)

    db.commit()


def _is_breached(condition: str, threshold: float, value: float) -> bool:
    if condition == "ABOVE":
        return value > threshold
    if condition == "BELOW":
        return value < threshold
    return False
