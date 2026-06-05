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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.core.enums import ScanResult

if TYPE_CHECKING:
    from backend.app.models.component import Component
    from backend.app.models.scan_transaction import ScanTransaction


class VerificationCheck(Base):
    """Kết quả kiểm tra QR, RFID và anti-tamper."""

    __tablename__ = "verification_checks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    verification_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    scan_transaction_id: Mapped[int] = mapped_column(
        ForeignKey(
            "scan_transactions.id",
            ondelete="RESTRICT",
        ),
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

    qr_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    rfid_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    tag_uid_read: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    verification_result: Mapped[ScanResult] = mapped_column(
        SAEnum(
            ScanResult,
            name="scan_result",
            native_enum=False,
            validate_strings=True,
        ),
        index=True,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )

    scan_transaction: Mapped["ScanTransaction"] = relationship(
        back_populates="verification_check",
    )

    component: Mapped["Component | None"] = relationship(
        back_populates="verification_checks",
    )

    def __repr__(self) -> str:
        return (
            "VerificationCheck("
            f"id={self.id!r}, "
            f"verification_id={self.verification_id!r}, "
            f"verification_result={self.verification_result!r}"
            ")"
        )