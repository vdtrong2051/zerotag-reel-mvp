from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.enums import EventResult, EventType
from backend.app.models.event import Event
from backend.app.models.scan_transaction import ScanTransaction


def list_events(
    session: Session,
    *,
    transaction_id: str | None = None,
    event_type: EventType | None = None,
    result: EventResult | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[Event]:
    """Trả danh sách event theo thứ tự mới nhất."""

    statement = select(Event)

    if transaction_id is not None:
        statement = (
            statement
            .join(
                ScanTransaction,
                Event.scan_transaction_id
                == ScanTransaction.id,
            )
            .where(
                ScanTransaction.transaction_id
                == transaction_id
            )
        )

    if event_type is not None:
        statement = statement.where(
            Event.event_type == event_type
        )

    if result is not None:
        statement = statement.where(
            Event.result == result
        )

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        statement
        .order_by(
            Event.created_at.desc(),
            Event.id.desc(),
        )
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    event_internal_id: int,
) -> Event | None:
    """Tìm event theo khóa nội bộ."""

    return session.get(Event, event_internal_id)


def get_by_event_id(
    session: Session,
    event_id: str,
) -> Event | None:
    """Tìm event theo mã nghiệp vụ."""

    statement = select(Event).where(
        Event.event_id == event_id
    )

    return session.scalar(statement)


def list_by_transaction(
    session: Session,
    transaction_id: str,
) -> list[Event]:
    """Trả event timeline của một transaction."""

    statement = (
        select(Event)
        .join(
            ScanTransaction,
            Event.scan_transaction_id
            == ScanTransaction.id,
        )
        .where(
            ScanTransaction.transaction_id
            == transaction_id
        )
        .order_by(
            Event.sequence_no,
            Event.id,
        )
    )

    return list(session.scalars(statement))


def create_event(
    session: Session,
    event: Event,
) -> Event:
    """Đưa event mới vào session mà không tự commit."""

    session.add(event)
    session.flush()

    return event


def count_events(
    session: Session,
) -> int:
    """Đếm toàn bộ event."""

    statement = select(func.count(Event.id))

    return session.scalar(statement) or 0