from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Final

from dotenv import load_dotenv


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env",
    override=False,
)


def _read_string(name: str, default: str) -> str:
    """Đọc biến môi trường dạng chuỗi và dùng giá trị mặc định nếu rỗng."""
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    return value.strip()


def _read_integer(name: str, default: int) -> int:
    """Đọc biến môi trường dạng số nguyên."""
    raw_value = os.getenv(name)

    if raw_value is None or not raw_value.strip():
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable {name} must be an integer."
        ) from exc


@dataclass(frozen=True, slots=True)
class Settings:
    """Cấu hình dùng chung của ứng dụng."""

    app_name: str
    app_env: str
    api_v1_prefix: str

    database_url: str

    backend_host: str
    backend_port: int

    dashboard_host: str
    dashboard_port: int

    default_gateway_id: str
    default_location: str
    default_bom_code: str

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Tạo và cache Settings để toàn ứng dụng dùng cùng cấu hình."""

    api_prefix = _read_string("API_V1_PREFIX", "/api/v1")

    if not api_prefix.startswith("/"):
        api_prefix = f"/{api_prefix}"

    api_prefix = api_prefix.rstrip("/") or "/"

    settings = Settings(
        app_name=_read_string(
            "APP_NAME",
            "ZeroTag Reel MVP",
        ),
        app_env=_read_string(
            "APP_ENV",
            "development",
        ),
        api_v1_prefix=api_prefix,
        database_url=_read_string(
            "DATABASE_URL",
            "sqlite:///./zerotag_mvp.db",
        ),
        backend_host=_read_string(
            "BACKEND_HOST",
            "127.0.0.1",
        ),
        backend_port=_read_integer(
            "BACKEND_PORT",
            8000,
        ),
        dashboard_host=_read_string(
            "DASHBOARD_HOST",
            "127.0.0.1",
        ),
        dashboard_port=_read_integer(
            "DASHBOARD_PORT",
            8501,
        ),
        default_gateway_id=_read_string(
            "DEFAULT_GATEWAY_ID",
            "ZG-001",
        ),
        default_location=_read_string(
            "DEFAULT_LOCATION",
            "SMT Issue Station 01",
        ),
        default_bom_code=_read_string(
            "DEFAULT_BOM_CODE",
            "PCB-DEMO-01",
        ),
    )

    for port_name, port_value in (
        ("BACKEND_PORT", settings.backend_port),
        ("DASHBOARD_PORT", settings.dashboard_port),
    ):
        if not 1 <= port_value <= 65535:
            raise ValueError(
                f"{port_name} must be between 1 and 65535."
            )

    return settings