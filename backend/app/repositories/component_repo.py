from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.enums import ComponentStatus
from backend.app.models.component import Component


def list_components(
    session: Session,
    *,
    part_number: str | None = None,
    lot_number: str | None = None,
    status: ComponentStatus | None = None,
    location: str | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[Component]:
    """Trả danh sách component với các bộ lọc cơ bản."""

    statement = select(Component)

    if part_number is not None:
        statement = statement.where(
            Component.part_number == part_number
        )

    if lot_number is not None:
        statement = statement.where(
            Component.lot_number == lot_number
        )

    if status is not None:
        statement = statement.where(
            Component.status == status
        )

    if location is not None:
        statement = statement.where(
            Component.location == location
        )

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        statement
        .order_by(Component.id)
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    component_id: int,
) -> Component | None:
    """Tìm component theo khóa nội bộ."""

    return session.get(Component, component_id)


def get_by_zerotag_id(
    session: Session,
    zerotag_id: str,
) -> Component | None:
    """Tìm component theo ZeroTag ID."""

    statement = select(Component).where(
        Component.zerotag_id == zerotag_id
    )

    return session.scalar(statement)


def get_by_tag_uid(
    session: Session,
    tag_uid: str,
) -> Component | None:
    """Tìm component theo UID/EPC vật lý."""

    statement = select(Component).where(
        Component.tag_uid == tag_uid
    )

    return session.scalar(statement)


def create_component(
    session: Session,
    component: Component,
) -> Component:
    """Đưa component mới vào session mà không tự commit."""

    session.add(component)
    session.flush()

    return component


def count_components(
    session: Session,
    *,
    status: ComponentStatus | None = None,
) -> int:
    """Đếm component, có thể lọc theo trạng thái."""

    statement = select(func.count(Component.id))

    if status is not None:
        statement = statement.where(
            Component.status == status
        )

    return session.scalar(statement) or 0