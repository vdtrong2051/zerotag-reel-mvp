from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.core.enums import BomStatus

if TYPE_CHECKING:
    from backend.app.models.bom_item import BomItem
    from backend.app.models.scan_transaction import ScanTransaction


class Bom(Base):
    """Thông tin tổng quát của một Bill of Materials."""

    __tablename__ = "boms"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    bom_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[BomStatus] = mapped_column(
        SAEnum(
            BomStatus,
            name="bom_status",
            native_enum=False,
            validate_strings=True,
        ),
        default=BomStatus.ACTIVE,
        server_default=BomStatus.ACTIVE.value,
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    items: Mapped[list["BomItem"]] = relationship(
        back_populates="bom",
    )

    scan_transactions: Mapped[list["ScanTransaction"]] = relationship(
        back_populates="bom",
    )

    def __repr__(self) -> str:
        return (
            "Bom("
            f"id={self.id!r}, "
            f"bom_code={self.bom_code!r}, "
            f"product_name={self.product_name!r}"
            ")"
        )