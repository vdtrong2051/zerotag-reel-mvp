from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.core.enums import EventResult, EventType

if TYPE_CHECKING:
    from backend.app.models.scan_transaction import ScanTransaction


class Event(Base):
    """Một bước audit trong một ScanTransaction."""

    __tablename__ = "events"

    __table_args__ = (
        UniqueConstraint(
            "scan_transaction_id",
            "sequence_no",
            name="uq_events_transaction_sequence",
        ),
        CheckConstraint(
            "sequence_no >= 1",
            name="ck_events_sequence_positive",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    event_id: Mapped[str] = mapped_column(
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
        index=True,
        nullable=False,
    )

    sequence_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    event_type: Mapped[EventType] = mapped_column(
        SAEnum(
            EventType,
            name="event_type",
            native_enum=False,
            validate_strings=True,
        ),
        index=True,
        nullable=False,
    )

    result: Mapped[EventResult] = mapped_column(
        SAEnum(
            EventResult,
            name="event_result",
            native_enum=False,
            validate_strings=True,
        ),
        index=True,
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        server_default="{}",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    scan_transaction: Mapped["ScanTransaction"] = relationship(
        back_populates="events",
    )

    def __repr__(self) -> str:
        return (
            "Event("
            f"id={self.id!r}, "
            f"event_id={self.event_id!r}, "
            f"event_type={self.event_type!r}"
            ")"
        )