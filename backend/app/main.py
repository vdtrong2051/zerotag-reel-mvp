from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.core.config import get_settings
from backend.app.core.database import (
    create_database_tables,
    dispose_database_engine,
)
from backend.app.core.errors import AppError


logger = logging.getLogger(__name__)
settings = get_settings()


def _error_payload(
    *,
    code: str,
    message: str,
    details: dict[str, Any],
    request_id: str | None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "request_id": request_id,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Khởi tạo và giải phóng tài nguyên theo vòng đời ứng dụng."""

    create_database_tables()

    yield

    dispose_database_engine()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API cho ZeroTag-Reel MVP: quản lý component, "
        "BOM, gateway, transaction và traceability."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.settings = settings


@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exception: AppError,
) -> JSONResponse:
    """Chuyển AppError thành error envelope thống nhất."""

    request_id = request.headers.get("X-Request-ID")

    return JSONResponse(
        status_code=exception.status_code,
        content=_error_payload(
            code=exception.code,
            message=exception.message,
            details=exception.details,
            request_id=request_id,
        ),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Không để lỗi ngoài dự kiến làm lộ stack trace qua API."""

    logger.error(
        "Unhandled error at path %s",
        request.url.path,
        exc_info=(
            type(exception),
            exception,
            exception.__traceback__,
        ),
    )

    request_id = request.headers.get("X-Request-ID")

    return JSONResponse(
        status_code=500,
        content=_error_payload(
            code="INTERNAL_ERROR",
            message="An unexpected server error occurred.",
            details={},
            request_id=request_id,
        ),
    )


@app.get(
    "/health",
    tags=["System"],
    summary="Kiểm tra trạng thái backend",
)
async def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "api_prefix": settings.api_v1_prefix,
        "timestamp": datetime.now(UTC).isoformat(),
    }