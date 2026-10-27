from __future__ import annotations

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    intersection_id: str
    horizon_minutes: int = Field(default=15, ge=15, le=60)
    weather: str | None = None
    event: bool | None = None


class TicketRequest(BaseModel):
    name: str
    subject: str
    message: str
    priority: str = "Medium"


class TicketUpdate(BaseModel):
    status: str | None = None
    reply: str | None = None


class SettingsRequest(BaseModel):
    city_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    congestion_alert_threshold: str | None = None
    green_time_base_seconds: int | None = None
