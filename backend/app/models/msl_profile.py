from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.models.component import Component


class MSLProfile(Base):
    """Dữ liệu Moisture Sensitivity Level của component."""

    __tablename__ = "msl_profiles"

    __table_args__ = (
        CheckConstraint(
            "floor_life_limit_hours > 0",
            name="ck_msl_floor_life_limit_positive",
        ),
        CheckConstraint(
            "floor_life_used_hours >= 0",
            name="ck_msl_floor_life_used_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    component_id: Mapped[int] = mapped_column(
        ForeignKey(
            "components.id",
            ondelete="CASCADE",
        ),
        unique=True,
        index=True,
        nullable=False,
    )

    msl_level: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    bag_open_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    floor_life_limit_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    floor_life_used_hours: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        server_default="0",
        nullable=False,
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    component: Mapped["Component"] = relationship(
        back_populates="msl_profile",
    )

    def __repr__(self) -> str:
        return (
            "MSLProfile("
            f"id={self.id!r}, "
            f"component_id={self.component_id!r}, "
            f"msl_level={self.msl_level!r}"
            ")"
        )