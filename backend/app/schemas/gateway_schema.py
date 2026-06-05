from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.core.enums import (
    GatewayStatus,
    GatewayType,
)


class GatewayRead(BaseModel):
    """Dữ liệu Gateway trả về qua API."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    gateway_id: str
    gateway_name: str
    gateway_type: GatewayType

    location: str | None
    status: GatewayStatus
    last_seen_at: datetime | None

    created_at: datetime
    updated_at: datetime