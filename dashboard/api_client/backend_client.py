from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class BackendClientError(RuntimeError):
    """Lỗi nền của Dashboard Backend Client."""


class BackendConnectionError(BackendClientError):
    """Không thể kết nối tới FastAPI backend."""

    def __init__(
        self,
        *,
        url: str,
        reason: str,
    ) -> None:
        self.url = url
        self.reason = reason

        super().__init__(
            f"Cannot connect to backend at {url}: {reason}"
        )


class BackendAPIError(BackendClientError):
    """Backend trả HTTP 4xx hoặc 5xx."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Mapping[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = dict(details or {})
        self.request_id = request_id

        super().__init__(
            f"{message} [{code}, HTTP {status_code}]"
        )


class BackendResponseError(BackendClientError):
    """Backend trả dữ liệu không đúng JSON contract."""

    def __init__(
        self,
        *,
        endpoint: str,
        reason: str,
    ) -> None:
        self.endpoint = endpoint
        self.reason = reason

        super().__init__(
            f"Invalid response from {endpoint}: {reason}"
        )


def _normalize_api_prefix(value: str) -> str:
    cleaned = value.strip().strip("/")

    if not cleaned:
        return ""

    return f"/{cleaned}"


def _clean_query_params(
    params: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if params is None:
        return None

    cleaned = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }

    return cleaned or None


class BackendClient:
    """HTTP client duy nhất của Streamlit Dashboard."""

    def __init__(
        self,
        *,
        base_url: str,
        api_prefix: str = "/api/v1",
        timeout_seconds: float = 5.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_prefix = _normalize_api_prefix(
            api_prefix
        )
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    @classmethod
    def from_env(cls) -> BackendClient:
        """Tạo client từ file .env của project."""

        load_dotenv(PROJECT_ROOT / ".env")

        explicit_base_url = os.getenv(
            "BACKEND_BASE_URL"
        )

        if explicit_base_url:
            base_url = explicit_base_url
        else:
            backend_host = os.getenv(
                "BACKEND_HOST",
                "127.0.0.1",
            )

            backend_port = os.getenv(
                "BACKEND_PORT",
                "8000",
            )

            base_url = (
                f"http://{backend_host}:{backend_port}"
            )

        api_prefix = os.getenv(
            "API_V1_PREFIX",
            "/api/v1",
        )

        return cls(
            base_url=base_url,
            api_prefix=api_prefix,
        )

    def _build_url(
        self,
        path: str,
        *,
        use_api_prefix: bool = True,
    ) -> str:
        normalized_path = path.lstrip("/")

        prefix = (
            self.api_prefix
            if use_api_prefix
            else ""
        )

        return (
            f"{self.base_url}"
            f"{prefix}"
            f"/{normalized_path}"
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        use_api_prefix: bool = True,
        params: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        request_id: str | None = None,
    ) -> Any:
        url = self._build_url(
            path,
            use_api_prefix=use_api_prefix,
        )

        headers = {
            "Accept": "application/json",
            "User-Agent": "ZeroTag-Dashboard/0.1",
        }

        if request_id:
            headers["X-Request-ID"] = request_id

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                transport=self._transport,
                headers=headers,
            ) as client:
                response = client.request(
                    method,
                    url,
                    params=_clean_query_params(params),
                    json=json_body,
                )

        except httpx.TimeoutException as error:
            raise BackendConnectionError(
                url=url,
                reason="request timed out",
            ) from error

        except httpx.RequestError as error:
            raise BackendConnectionError(
                url=url,
                reason=str(error),
            ) from error

        try:
            response_payload = response.json()
        except ValueError as error:
            if response.is_error:
                message = (
                    response.text.strip()
                    or response.reason_phrase
                    or "Backend request failed."
                )

                raise BackendAPIError(
                    status_code=response.status_code,
                    code=f"HTTP_{response.status_code}",
                    message=message,
                    details={
                        "url": url,
                    },
                ) from error

            raise BackendResponseError(
                endpoint=url,
                reason="response is not valid JSON",
            ) from error

        if response.is_error:
            self._raise_api_error(
                response=response,
                payload=response_payload,
            )

        return response_payload

    @staticmethod
    def _raise_api_error(
        *,
        response: httpx.Response,
        payload: Any,
    ) -> None:
        error_code = (
            f"HTTP_{response.status_code}"
        )

        error_message = (
            response.reason_phrase
            or "Backend request failed."
        )

        error_details: dict[str, Any] = {}
        request_id: str | None = None

        if isinstance(payload, dict):
            request_id_value = payload.get(
                "request_id"
            )

            if isinstance(request_id_value, str):
                request_id = request_id_value

            error_payload = payload.get("error")

            if isinstance(error_payload, dict):
                code_value = error_payload.get(
                    "code"
                )

                message_value = error_payload.get(
                    "message"
                )

                details_value = error_payload.get(
                    "details"
                )

                if isinstance(code_value, str):
                    error_code = code_value

                if isinstance(message_value, str):
                    error_message = message_value

                if isinstance(details_value, dict):
                    error_details = details_value

        raise BackendAPIError(
            status_code=response.status_code,
            code=error_code,
            message=error_message,
            details=error_details,
            request_id=request_id,
        )

    @staticmethod
    def _expect_object(
        payload: Any,
        *,
        endpoint: str,
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise BackendResponseError(
                endpoint=endpoint,
                reason="expected a JSON object",
            )

        return payload

    @staticmethod
    def _expect_object_list(
        payload: Any,
        *,
        endpoint: str,
    ) -> list[dict[str, Any]]:
        if not isinstance(payload, list):
            raise BackendResponseError(
                endpoint=endpoint,
                reason="expected a JSON array",
            )

        if not all(
            isinstance(item, dict)
            for item in payload
        ):
            raise BackendResponseError(
                endpoint=endpoint,
                reason=(
                    "every array item must be "
                    "a JSON object"
                ),
            )

        return [
            dict(item)
            for item in payload
        ]

    def health_check(self) -> dict[str, Any]:
        endpoint = "/health"

        payload = self._request(
            "GET",
            endpoint,
            use_api_prefix=False,
        )

        return self._expect_object(
            payload,
            endpoint=endpoint,
        )

    def get_components(
        self,
        *,
        part_number: str | None = None,
        lot_number: str | None = None,
        status: str | None = None,
        location: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        endpoint = "/components"

        payload = self._request(
            "GET",
            endpoint,
            params={
                "part_number": part_number,
                "lot_number": lot_number,
                "status": status,
                "location": location,
                "offset": offset,
                "limit": limit,
            },
        )

        return self._expect_object_list(
            payload,
            endpoint=endpoint,
        )

    def get_component(
        self,
        zerotag_id: str,
    ) -> dict[str, Any]:
        cleaned_id = zerotag_id.strip()

        if not cleaned_id:
            raise ValueError(
                "zerotag_id cannot be empty."
            )

        endpoint = (
            "/components/"
            f"{quote(cleaned_id, safe='')}"
        )

        payload = self._request(
            "GET",
            endpoint,
        )

        return self._expect_object(
            payload,
            endpoint=endpoint,
        )

    def get_boms(
        self,
    ) -> list[dict[str, Any]]:
        endpoint = "/boms"

        payload = self._request(
            "GET",
            endpoint,
        )

        return self._expect_object_list(
            payload,
            endpoint=endpoint,
        )

    def get_events(
        self,
        *,
        transaction_id: str | None = None,
        event_type: str | None = None,
        result: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        endpoint = "/events"

        payload = self._request(
            "GET",
            endpoint,
            params={
                "transaction_id": transaction_id,
                "event_type": event_type,
                "result": result,
                "offset": offset,
                "limit": limit,
            },
        )

        return self._expect_object_list(
            payload,
            endpoint=endpoint,
        )

    def get_gateways(
        self,
    ) -> list[dict[str, Any]]:
        endpoint = "/gateways"

        payload = self._request(
            "GET",
            endpoint,
        )

        return self._expect_object_list(
            payload,
            endpoint=endpoint,
        )

    def submit_scan(
        self,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        endpoint = "/scans"

        request_id_value = payload.get(
            "request_id"
        )

        request_id = (
            request_id_value
            if isinstance(request_id_value, str)
            else None
        )

        response_payload = self._request(
            "POST",
            endpoint,
            json_body=dict(payload),
            request_id=request_id,
        )

        return self._expect_object(
            response_payload,
            endpoint=endpoint,
        )