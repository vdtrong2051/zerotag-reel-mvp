from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.enums import BomStatus
from backend.app.models.bom import Bom
from backend.app.models.bom_item import BomItem


def list_boms(
    session: Session,
    *,
    status: BomStatus | None = None,
    include_items: bool = True,
    offset: int = 0,
    limit: int = 100,
) -> list[Bom]:
    """Trả danh sách BOM."""

    statement = select(Bom)

    if include_items:
        statement = statement.options(
            selectinload(Bom.items)
        )

    if status is not None:
        statement = statement.where(
            Bom.status == status
        )

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        statement
        .order_by(Bom.id)
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    bom_id: int,
) -> Bom | None:
    """Tìm BOM theo khóa nội bộ."""

    statement = (
        select(Bom)
        .options(selectinload(Bom.items))
        .where(Bom.id == bom_id)
    )

    return session.scalar(statement)


def get_by_bom_code(
    session: Session,
    bom_code: str,
    *,
    include_items: bool = True,
) -> Bom | None:
    """Tìm BOM theo mã nghiệp vụ."""

    statement = select(Bom).where(
        Bom.bom_code == bom_code
    )

    if include_items:
        statement = statement.options(
            selectinload(Bom.items)
        )

    return session.scalar(statement)


def get_item_by_id(
    session: Session,
    bom_item_id: int,
) -> BomItem | None:
    """Tìm BOMItem theo khóa nội bộ."""

    return session.get(BomItem, bom_item_id)


def get_item_by_ref(
    session: Session,
    *,
    bom_code: str,
    bom_ref: str,
) -> BomItem | None:
    """Tìm dòng BOM bằng bom_code và bom_ref."""

    statement = (
        select(BomItem)
        .join(Bom, BomItem.bom_id == Bom.id)
        .where(
            Bom.bom_code == bom_code,
            BomItem.bom_ref == bom_ref,
        )
    )

    return session.scalar(statement)


def create_bom(
    session: Session,
    bom: Bom,
) -> Bom:
    """Đưa BOM mới vào session mà không tự commit."""

    session.add(bom)
    session.flush()

    return bom


def create_bom_item(
    session: Session,
    bom_item: BomItem,
) -> BomItem:
    """Đưa BOMItem mới vào session mà không tự commit."""

    session.add(bom_item)
    session.flush()

    return bom_item


def count_boms(
    session: Session,
    *,
    status: BomStatus | None = None,
) -> int:
    """Đếm BOM, có thể lọc theo trạng thái."""

    statement = select(func.count(Bom.id))

    if status is not None:
        statement = statement.where(
            Bom.status == status
        )

    return session.scalar(statement) or 0