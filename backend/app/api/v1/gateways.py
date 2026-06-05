from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.enums import GatewayStatus
from backend.app.repositories import gateway_repo
from backend.app.schemas.gateway_schema import GatewayRead


router = APIRouter(
    prefix="/gateways",
    tags=["Gateways"],
)


@router.get(
    "",
    response_model=list[GatewayRead],
    summary="Lấy danh sách gateway",
)
def list_gateway_records(
    db: Annotated[Session, Depends(get_db)],
    status: Annotated[
        GatewayStatus | None,
        Query(),
    ] = None,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 100,
) -> list[GatewayRead]:
    """Đọc danh sách gateway."""

    gateways = gateway_repo.list_gateways(
        db,
        status=status,
        offset=offset,
        limit=limit,
    )

    return [
        GatewayRead.model_validate(gateway)
        for gateway in gateways
    ]