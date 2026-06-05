from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    """Base class dùng chung cho toàn bộ SQLAlchemy models."""


engine_options: dict[str, Any] = {
    "pool_pre_ping": True,
}

is_sqlite = settings.database_url.startswith("sqlite")

if is_sqlite:
    engine_options["connect_args"] = {
        "check_same_thread": False,
    }


engine: Engine = create_engine(
    settings.database_url,
    **engine_options,
)


if is_sqlite:

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(
        dbapi_connection: Any,
        _connection_record: Any,
    ) -> None:
        """Bật kiểm tra foreign key cho từng SQLite connection."""

        cursor = dbapi_connection.cursor()

        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency cung cấp một database session cho mỗi request."""

    database_session = SessionLocal()

    try:
        yield database_session
    finally:
        database_session.close()


def create_database_tables() -> None:
    """Tạo các bảng đã được đăng ký trong SQLAlchemy metadata."""

    # Import package models để SQLAlchemy đăng ký toàn bộ model.
    # Các model cụ thể sẽ được import trong models/__init__.py ở Bước 4.
    from backend.app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_database_connection() -> None:
    """Kiểm tra engine có thể kết nối database."""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def dispose_database_engine() -> None:
    """Đóng connection pool khi ứng dụng dừng."""

    engine.dispose()