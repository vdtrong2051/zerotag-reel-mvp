from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.enums import EventResult, EventType
from backend.app.repositories import event_repo
from backend.app.schemas.event_schema import EventRead


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get(
    "",
    response_model=list[EventRead],
    summary="Lấy danh sách event",
)
def list_event_records(
    db: Annotated[Session, Depends(get_db)],
    transaction_id: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
    event_type: Annotated[
        EventType | None,
        Query(),
    ] = None,
    result: Annotated[
        EventResult | None,
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
) -> list[EventRead]:
    """Đọc Event Log theo thứ tự mới nhất."""

    events = event_repo.list_events(
        db,
        transaction_id=transaction_id,
        event_type=event_type,
        result=result,
        offset=offset,
        limit=limit,
    )

    return [
        EventRead.model_validate(event)
        for event in events
    ]