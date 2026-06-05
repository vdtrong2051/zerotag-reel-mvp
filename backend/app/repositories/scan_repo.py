from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.enums import ScanMode, ScanResult
from backend.app.models.scan_transaction import ScanTransaction


def list_transactions(
    session: Session,
    *,
    component_id: int | None = None,
    gateway_ref_id: int | None = None,
    mode: ScanMode | None = None,
    final_result: ScanResult | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[ScanTransaction]:
    """Trả danh sách scan transaction."""

    statement = select(ScanTransaction)

    if component_id is not None:
        statement = statement.where(
            ScanTransaction.component_id == component_id
        )

    if gateway_ref_id is not None:
        statement = statement.where(
            ScanTransaction.gateway_ref_id == gateway_ref_id
        )

    if mode is not None:
        statement = statement.where(
            ScanTransaction.mode == mode
        )

    if final_result is not None:
        statement = statement.where(
            ScanTransaction.final_result == final_result
        )

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        statement
        .order_by(
            ScanTransaction.started_at.desc(),
            ScanTransaction.id.desc(),
        )
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    scan_transaction_id: int,
) -> ScanTransaction | None:
    """Tìm transaction theo khóa nội bộ."""

    return session.get(
        ScanTransaction,
        scan_transaction_id,
    )


def get_by_transaction_id(
    session: Session,
    transaction_id: str,
) -> ScanTransaction | None:
    """Tìm transaction theo mã nghiệp vụ."""

    statement = select(ScanTransaction).where(
        ScanTransaction.transaction_id == transaction_id
    )

    return session.scalar(statement)


def get_by_request_id(
    session: Session,
    request_id: str,
) -> ScanTransaction | None:
    """Tìm transaction bằng request ID chống gửi trùng."""

    statement = select(ScanTransaction).where(
        ScanTransaction.request_id == request_id
    )

    return session.scalar(statement)


def create_transaction(
    session: Session,
    transaction: ScanTransaction,
) -> ScanTransaction:
    """Đưa transaction mới vào session mà không tự commit."""

    session.add(transaction)
    session.flush()

    return transaction


def count_transactions(
    session: Session,
) -> int:
    """Đếm toàn bộ scan transaction."""

    statement = select(
        func.count(ScanTransaction.id)
    )

    return session.scalar(statement) or 0