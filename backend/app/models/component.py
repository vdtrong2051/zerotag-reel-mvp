from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.core.enums import (
    ComponentStatus,
    LabelType,
    TamperStatus,
)

if TYPE_CHECKING:
    from backend.app.models.msl_profile import MSLProfile
    from backend.app.models.scan_transaction import ScanTransaction
    from backend.app.models.verification_check import VerificationCheck


class Component(Base):
    """Hồ sơ số của một reel, tray hoặc carton linh kiện."""

    __tablename__ = "components"

    __table_args__ = (
        CheckConstraint(
            "quantity_initial >= 0",
            name="ck_components_quantity_initial_nonnegative",
        ),
        CheckConstraint(
            "quantity_current >= 0",
            name="ck_components_quantity_current_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    zerotag_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    tag_uid: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=True,
    )

    part_number: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )

    component_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    supplier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    lot_number: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )

    date_code: Mapped[str] = mapped_column(
        String(16),
        index=True,
        nullable=False,
    )

    quantity_initial: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quantity_current: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[ComponentStatus] = mapped_column(
        SAEnum(
            ComponentStatus,
            name="component_status",
            native_enum=False,
            validate_strings=True,
        ),
        default=ComponentStatus.REGISTERED,
        server_default=ComponentStatus.REGISTERED.value,
        index=True,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    label_type: Mapped[LabelType] = mapped_column(
        SAEnum(
            LabelType,
            name="label_type",
            native_enum=False,
            validate_strings=True,
        ),
        default=LabelType.STANDARD,
        server_default=LabelType.STANDARD.value,
        nullable=False,
    )

    tamper_status: Mapped[TamperStatus] = mapped_column(
        SAEnum(
            TamperStatus,
            name="tamper_status",
            native_enum=False,
            validate_strings=True,
        ),
        default=TamperStatus.NORMAL,
        server_default=TamperStatus.NORMAL.value,
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

    scan_transactions: Mapped[list["ScanTransaction"]] = relationship(
        back_populates="component",
    )

    msl_profile: Mapped["MSLProfile | None"] = relationship(
        back_populates="component",
        uselist=False,
    )

    verification_checks: Mapped[list["VerificationCheck"]] = relationship(
        back_populates="component",
    )

    def __repr__(self) -> str:
        return (
            "Component("
            f"id={self.id!r}, "
            f"zerotag_id={self.zerotag_id!r}, "
            f"part_number={self.part_number!r}"
            ")"
        )