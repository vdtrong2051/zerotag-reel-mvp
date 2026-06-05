from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.core.enums import (
    ComponentStatus,
    LabelType,
    TamperStatus,
)


class ComponentRead(BaseModel):
    """Dữ liệu component trả về qua API."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    zerotag_id: str
    tag_uid: str | None

    part_number: str
    component_name: str
    manufacturer: str | None
    supplier: str | None

    lot_number: str
    date_code: str

    quantity_initial: int
    quantity_current: int

    status: ComponentStatus
    location: str | None

    label_type: LabelType
    tamper_status: TamperStatus

    created_at: datetime
    updated_at: datetime