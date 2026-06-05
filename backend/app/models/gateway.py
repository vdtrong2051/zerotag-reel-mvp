from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.core.enums import GatewayStatus, GatewayType

if TYPE_CHECKING:
    from backend.app.models.scan_transaction import ScanTransaction


class Gateway(Base):
    """Gateway Simulator hoặc gateway phần cứng của hệ thống."""

    __tablename__ = "gateways"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    gateway_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    gateway_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    gateway_type: Mapped[GatewayType] = mapped_column(
        SAEnum(
            GatewayType,
            name="gateway_type",
            native_enum=False,
            validate_strings=True,
        ),
        default=GatewayType.SIMULATOR,
        server_default=GatewayType.SIMULATOR.value,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[GatewayStatus] = mapped_column(
        SAEnum(
            GatewayStatus,
            name="gateway_status",
            native_enum=False,
            validate_strings=True,
        ),
        default=GatewayStatus.OFFLINE,
        server_default=GatewayStatus.OFFLINE.value,
        index=True,
        nullable=False,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
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

    scan_transactions: Mapped[list["ScanTransaction"]] = relationship(
        back_populates="gateway",
    )

    def __repr__(self) -> str:
        return (
            "Gateway("
            f"id={self.id!r}, "
            f"gateway_id={self.gateway_id!r}, "
            f"status={self.status!r}"
            ")"
        )