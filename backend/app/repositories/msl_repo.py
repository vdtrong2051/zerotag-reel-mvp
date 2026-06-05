from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.component import Component
from backend.app.models.msl_profile import MSLProfile


def list_profiles(
    session: Session,
    *,
    offset: int = 0,
    limit: int = 100,
) -> list[MSLProfile]:
    """Trả danh sách MSL profile."""

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        select(MSLProfile)
        .order_by(MSLProfile.id)
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    profile_id: int,
) -> MSLProfile | None:
    """Tìm MSL profile theo khóa nội bộ."""

    return session.get(MSLProfile, profile_id)


def get_by_component_id(
    session: Session,
    component_id: int,
) -> MSLProfile | None:
    """Tìm MSL profile theo component ID."""

    statement = select(MSLProfile).where(
        MSLProfile.component_id == component_id
    )

    return session.scalar(statement)


def get_by_zerotag_id(
    session: Session,
    zerotag_id: str,
) -> MSLProfile | None:
    """Tìm MSL profile theo ZeroTag ID."""

    statement = (
        select(MSLProfile)
        .join(
            Component,
            MSLProfile.component_id == Component.id,
        )
        .where(
            Component.zerotag_id == zerotag_id
        )
    )

    return session.scalar(statement)


def create_profile(
    session: Session,
    profile: MSLProfile,
) -> MSLProfile:
    """Đưa MSL profile mới vào session mà không tự commit."""

    session.add(profile)
    session.flush()

    return profile


def count_profiles(
    session: Session,
) -> int:
    """Đếm toàn bộ MSL profile."""

    statement = select(func.count(MSLProfile.id))

    return session.scalar(statement) or 0