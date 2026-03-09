"""SQLAlchemy models for Pulse."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


def uuid4_str():
    return str(uuid.uuid4())


class Service(Base):
    __tablename__ = "services"

    id = Column(String(36), primary_key=True, default=uuid4_str)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    metrics = relationship("Metric", back_populates="service", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="service", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="service", cascade="all, delete-orphan")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=uuid4_str)
    service_id = Column(String(36), ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="metrics")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String(36), primary_key=True, default=uuid4_str)
    service_id = Column(String(36), ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String(255), nullable=False, index=True)
    threshold = Column(Float, nullable=False)
    condition = Column(String(32), nullable=False)  # ABOVE | BELOW
    created_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="alert_rules")
    alerts = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=uuid4_str)
    rule_id = Column(String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(String(36), ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    metric_value = Column(Float, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    state = Column(String(32), nullable=False)  # ACTIVE | RESOLVED

    rule = relationship("AlertRule", back_populates="alerts")
    service = relationship("Service", back_populates="alerts")
