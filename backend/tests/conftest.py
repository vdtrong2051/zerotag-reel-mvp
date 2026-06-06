from __future__ import annotations

import json
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.models  # noqa: F401
from backend.app.api.v1 import api_router
from backend.app.core.database import Base, get_db
from backend.app.core.errors import AppError
from backend.app.main import app_error_handler
from backend.app.seed.seed_boms import seed_boms
from backend.app.seed.seed_components import seed_components
from backend.app.seed.seed_gateways import seed_gateways


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_PAYLOAD_DIR = (
    PROJECT_ROOT
    / "gateway"
    / "simulator"
    / "sample_payloads"
)


@pytest.fixture()
def sqlite_test_engine() -> Generator[Engine, None, None]:
    """Tạo SQLite in-memory riêng cho từng test."""

    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def _enable_foreign_keys(
        dbapi_connection: Any,
        _connection_record: Any,
    ) -> None:
        cursor = dbapi_connection.cursor()

        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    Base.metadata.create_all(
        bind=test_engine,
    )

    try:
        yield test_engine
    finally:
        Base.metadata.drop_all(
            bind=test_engine,
        )

        test_engine.dispose()


@pytest.fixture()
def session_factory(
    sqlite_test_engine: Engine,
) -> sessionmaker[Session]:
    """Tạo Session factory gắn với database test."""

    return sessionmaker(
        bind=sqlite_test_engine,
        class_=Session,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture()
def seeded_session_factory(
    session_factory: sessionmaker[Session],
) -> sessionmaker[Session]:
    """Nạp dữ liệu demo vào database test."""

    with session_factory() as session:
        try:
            seed_components(session)
            seed_boms(session)
            seed_gateways(session)

            session.commit()
        except Exception:
            session.rollback()
            raise

    return session_factory


@pytest.fixture()
def test_app(
    seeded_session_factory: sessionmaker[Session],
) -> Generator[FastAPI, None, None]:
    """Tạo FastAPI app riêng và override database dependency."""

    application = FastAPI(
        title="ZeroTag Reel MVP Test App",
    )

    application.include_router(
        api_router,
        prefix="/api/v1",
    )

    application.add_exception_handler(
        AppError,
        app_error_handler,
    )

    def override_get_db() -> Generator[Session, None, None]:
        database_session = seeded_session_factory()

        try:
            yield database_session
        finally:
            database_session.close()

    application.dependency_overrides[get_db] = (
        override_get_db
    )

    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture()
def client(
    test_app: FastAPI,
) -> Generator[TestClient, None, None]:
    """HTTP client dùng để gọi API trong integration test."""

    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture()
def load_sample_payload() -> Callable[
    [str],
    dict[str, Any],
]:
    """Đọc một sample payload JSON theo tên file."""

    def _load(filename: str) -> dict[str, Any]:
        payload_path = SAMPLE_PAYLOAD_DIR / filename

        if not payload_path.exists():
            raise FileNotFoundError(
                f"Sample payload was not found: {payload_path}"
            )

        payload = json.loads(
            payload_path.read_text(
                encoding="utf-8-sig",
            )
        )

        if not isinstance(payload, dict):
            raise ValueError(
                f"Payload must be a JSON object: {filename}"
            )

        return payload

    return _load