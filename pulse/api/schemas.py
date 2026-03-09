"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# --- Service ---
class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime


# --- Metric ---
class MetricCreate(BaseModel):
    name: str
    value: float


class MetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    service_id: UUID
    name: str
    value: float
    timestamp: datetime


# --- Alert Rule ---
class AlertRuleCreate(BaseModel):
    metric_name: str
    threshold: float
    condition: Literal["ABOVE", "BELOW"]


class AlertRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    service_id: UUID
    metric_name: str
    threshold: float
    condition: str
    created_at: datetime


# --- Alert ---
class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    rule_id: UUID
    service_id: UUID
    metric_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    state: str
