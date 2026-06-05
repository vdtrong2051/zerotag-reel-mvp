from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.models.bom import Bom
    from backend.app.models.scan_transaction import ScanTransaction


class BomItem(Base):
    """Một dòng linh kiện yêu cầu trong BOM."""

    __tablename__ = "bom_items"

    __table_args__ = (
        UniqueConstraint(
            "bom_id",
            "bom_ref",
            name="uq_bom_items_bom_id_bom_ref",
        ),
        CheckConstraint(
            "required_quantity > 0",
            name="ck_bom_items_required_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    bom_id: Mapped[int] = mapped_column(
        ForeignKey(
            "boms.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=False,
    )

    bom_ref: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    required_part_number: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )

    allowed_lot: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    allowed_date_code_from: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    allowed_date_code_to: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    required_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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

    bom: Mapped["Bom"] = relationship(
        back_populates="items",
    )

    scan_transactions: Mapped[list["ScanTransaction"]] = relationship(
        back_populates="bom_item",
    )

    def __repr__(self) -> str:
        return (
            "BomItem("
            f"id={self.id!r}, "
            f"bom_id={self.bom_id!r}, "
            f"bom_ref={self.bom_ref!r}"
            ")"
        )