from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class AppError(Exception):
    """Base exception cho các lỗi nghiệp vụ và lỗi ứng dụng."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = dict(details or {})


class InvalidRequestError(AppError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "INVALID_REQUEST",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details,
        )


class ResourceNotFoundError(AppError):
    def __init__(
        self,
        resource: str,
        identifier: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        error_details = {
            "resource": resource,
            "identifier": identifier,
        }

        if details:
            error_details.update(details)

        super().__init__(
            code=f"UNKNOWN_{resource.upper()}",
            message=f"{resource} '{identifier}' was not found.",
            status_code=404,
            details=error_details,
        )


class ConflictError(AppError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "CONFLICT",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=409,
            details=details,
        )


class InvalidStateError(AppError):
    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="INVALID_STATE",
            message=message,
            status_code=409,
            details=details,
        )


class DatabaseOperationError(AppError):
    def __init__(
        self,
        message: str = "Database operation failed.",
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=500,
            details=details,
        )