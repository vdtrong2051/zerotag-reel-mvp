from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.enums import GatewayStatus
from backend.app.models.gateway import Gateway


def list_gateways(
    session: Session,
    *,
    status: GatewayStatus | None = None,
    offset: int = 0,
    limit: int = 100,
) -> list[Gateway]:
    """Trả danh sách gateway."""

    statement = select(Gateway)

    if status is not None:
        statement = statement.where(
            Gateway.status == status
        )

    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), 100)

    statement = (
        statement
        .order_by(Gateway.id)
        .offset(safe_offset)
        .limit(safe_limit)
    )

    return list(session.scalars(statement))


def get_by_id(
    session: Session,
    gateway_ref_id: int,
) -> Gateway | None:
    """Tìm gateway theo khóa nội bộ."""

    return session.get(Gateway, gateway_ref_id)


def get_by_gateway_id(
    session: Session,
    gateway_id: str,
) -> Gateway | None:
    """Tìm gateway theo mã nghiệp vụ."""

    statement = select(Gateway).where(
        Gateway.gateway_id == gateway_id
    )

    return session.scalar(statement)


def create_gateway(
    session: Session,
    gateway: Gateway,
) -> Gateway:
    """Đưa gateway mới vào session mà không tự commit."""

    session.add(gateway)
    session.flush()

    return gateway


def count_gateways(
    session: Session,
    *,
    status: GatewayStatus | None = None,
) -> int:
    """Đếm gateway."""

    statement = select(func.count(Gateway.id))

    if status is not None:
        statement = statement.where(
            Gateway.status == status
        )

    return session.scalar(statement) or 0