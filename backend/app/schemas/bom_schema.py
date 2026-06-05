from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.core.enums import BomStatus


class BomItemRead(BaseModel):
    """Một dòng BOM trả về qua API."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    bom_id: int
    bom_ref: str

    required_part_number: str
    allowed_lot: str | None
    allowed_date_code_from: str | None
    allowed_date_code_to: str | None
    required_quantity: int

    note: str | None

    created_at: datetime
    updated_at: datetime


class BomRead(BaseModel):
    """BOM và danh sách dòng BOM."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    bom_code: str
    product_name: str
    description: str | None
    status: BomStatus

    created_at: datetime
    updated_at: datetime

    items: list[BomItemRead] = Field(
        default_factory=list,
    )