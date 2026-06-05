from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.enums import ScanResult
from backend.app.models.scan_transaction import ScanTransaction
from backend.app.models.verification_check import VerificationCheck


def list_checks(
    session: Session,
    *,
    component_id: int | None = None,
    verification_result: ScanResult | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[VerificationCheck]:
    """Trả danh sách verification check."""

    statement = select(VerificationCheck)

    if component_id is not None:
        statement = statement.where(
            VerificationCheck.component_id == component_id
        )

    if verification_result is not None:
        statement = statement.where(
            VerificationCheck.verification_result
            == verification_result
        )

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        statement
        .order_by(
            VerificationCheck.checked_at.desc(),
            VerificationCheck.id.desc(),
        )
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    check_id: int,
) -> VerificationCheck | None:
    """Tìm verification check theo khóa nội bộ."""

    return session.get(
        VerificationCheck,
        check_id,
    )


def get_by_verification_id(
    session: Session,
    verification_id: str,
) -> VerificationCheck | None:
    """Tìm verification check theo mã nghiệp vụ."""

    statement = select(VerificationCheck).where(
        VerificationCheck.verification_id
        == verification_id
    )

    return session.scalar(statement)


def get_by_transaction_id(
    session: Session,
    transaction_id: str,
) -> VerificationCheck | None:
    """Tìm verification check theo transaction ID."""

    statement = (
        select(VerificationCheck)
        .join(
            ScanTransaction,
            VerificationCheck.scan_transaction_id
            == ScanTransaction.id,
        )
        .where(
            ScanTransaction.transaction_id
            == transaction_id
        )
    )

    return session.scalar(statement)


def create_check(
    session: Session,
    check: VerificationCheck,
) -> VerificationCheck:
    """Đưa verification check vào session mà không tự commit."""

    session.add(check)
    session.flush()

    return check


def count_checks(
    session: Session,
) -> int:
    """Đếm toàn bộ verification check."""

    statement = select(
        func.count(VerificationCheck.id)
    )

    return session.scalar(statement) or 0