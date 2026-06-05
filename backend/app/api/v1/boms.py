from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.enums import BomStatus
from backend.app.repositories import bom_repo
from backend.app.schemas.bom_schema import BomRead


router = APIRouter(
    prefix="/boms",
    tags=["BOMs"],
)


@router.get(
    "",
    response_model=list[BomRead],
    summary="Lấy danh sách BOM",
)
def list_bom_records(
    db: Annotated[Session, Depends(get_db)],
    status: Annotated[
        BomStatus | None,
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
) -> list[BomRead]:
    """Đọc danh sách BOM kèm các dòng BOMItem."""

    boms = bom_repo.list_boms(
        db,
        status=status,
        include_items=True,
        offset=offset,
        limit=limit,
    )

    return [
        BomRead.model_validate(bom)
        for bom in boms
    ]