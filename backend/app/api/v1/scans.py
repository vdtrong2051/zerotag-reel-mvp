from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.scan_schema import (
    ScanRequest,
    ScanResponse,
)
from backend.app.services import scan_service


router = APIRouter(
    prefix="/scans",
    tags=["Scans"],
)


@router.post(
    "",
    response_model=ScanResponse,
    status_code=status.HTTP_200_OK,
    summary="Xử lý một lần scan",
    response_description=(
        "Kết quả nghiệp vụ và hành động dành cho Gateway."
    ),
)
def process_scan_request(
    request: ScanRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ScanResponse:
    """Nhận payload từ Dashboard hoặc Gateway Simulator."""

    return scan_service.process_scan(
        db,
        request,
    )