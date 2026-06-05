from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.core.enums import (
    ComponentStatus,
    ScanMode,
    ScanResult,
)

if TYPE_CHECKING:
    from backend.app.models.bom import Bom
    from backend.app.models.bom_item import BomItem
    from backend.app.models.component import Component
    from backend.app.models.event import Event
    from backend.app.models.gateway import Gateway
    from backend.app.models.verification_check import VerificationCheck


class ScanTransaction(Base):
    """Kết quả tổng thể của một lần scan."""

    __tablename__ = "scan_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    transaction_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    request_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    component_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "components.id",
            ondelete="SET NULL",
        ),
        index=True,
        nullable=True,
    )

    gateway_ref_id: Mapped[int] = mapped_column(
        ForeignKey(
            "gateways.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=False,
    )

    bom_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "boms.id",
            ondelete="SET NULL",
        ),
        index=True,
        nullable=True,
    )

    bom_item_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "bom_items.id",
            ondelete="SET NULL",
        ),
        index=True,
        nullable=True,
    )

    mode: Mapped[ScanMode] = mapped_column(
        SAEnum(
            ScanMode,
            name="scan_mode",
            native_enum=False,
            validate_strings=True,
        ),
        index=True,
        nullable=False,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    input_zerotag_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )

    input_tag_uid: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
    )

    input_qr_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    input_rfid_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    final_result: Mapped[ScanResult] = mapped_column(
        SAEnum(
            ScanResult,
            name="scan_result",
            native_enum=False,
            validate_strings=True,
        ),
        index=True,
        nullable=False,
    )

    violations_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
        server_default="[]",
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    component_status_before: Mapped[ComponentStatus | None] = mapped_column(
        SAEnum(
            ComponentStatus,
            name="component_status",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=True,
    )

    component_status_after: Mapped[ComponentStatus | None] = mapped_column(
        SAEnum(
            ComponentStatus,
            name="component_status",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=True,
    )

    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    component: Mapped["Component | None"] = relationship(
        back_populates="scan_transactions",
    )

    gateway: Mapped["Gateway"] = relationship(
        back_populates="scan_transactions",
    )

    bom: Mapped["Bom | None"] = relationship(
        back_populates="scan_transactions",
    )

    bom_item: Mapped["BomItem | None"] = relationship(
        back_populates="scan_transactions",
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="scan_transaction",
        order_by="Event.sequence_no",
    )

    verification_check: Mapped["VerificationCheck | None"] = relationship(
        back_populates="scan_transaction",
        uselist=False,
    )

    def __repr__(self) -> str:
        return (
            "ScanTransaction("
            f"id={self.id!r}, "
            f"transaction_id={self.transaction_id!r}, "
            f"final_result={self.final_result!r}"
            ")"
        )