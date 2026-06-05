from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.enums import ComponentStatus
from backend.app.core.errors import ResourceNotFoundError
from backend.app.repositories import component_repo
from backend.app.schemas.component_schema import ComponentRead


router = APIRouter(
    prefix="/components",
    tags=["Components"],
)


@router.get(
    "",
    response_model=list[ComponentRead],
    summary="Lấy danh sách component",
)
def list_component_records(
    db: Annotated[Session, Depends(get_db)],
    part_number: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
    lot_number: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
    status: Annotated[
        ComponentStatus | None,
        Query(),
    ] = None,
    location: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 100,
) -> list[ComponentRead]:
    """Đọc component với các bộ lọc cơ bản."""

    components = component_repo.list_components(
        db,
        part_number=part_number,
        lot_number=lot_number,
        status=status,
        location=location,
        offset=offset,
        limit=limit,
    )

    return [
        ComponentRead.model_validate(component)
        for component in components
    ]


@router.get(
    "/{zerotag_id}",
    response_model=ComponentRead,
    summary="Lấy component theo ZeroTag ID",
)
def read_component(
    zerotag_id: Annotated[
        str,
        Path(min_length=1, max_length=64),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> ComponentRead:
    """Tìm một component cụ thể theo ZeroTag ID."""

    component = component_repo.get_by_zerotag_id(
        db,
        zerotag_id,
    )

    if component is None:
        raise ResourceNotFoundError(
            "component",
            zerotag_id,
        )

    return ComponentRead.model_validate(component)