from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.core.enums import (
    EventResult,
    EventType,
)


class EventRead(BaseModel):
    """Một bản ghi audit event trả về qua API."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    event_id: str
    scan_transaction_id: int
    sequence_no: int

    event_type: EventType
    result: EventResult

    message: str | None
    metadata_json: str

    created_at: datetime