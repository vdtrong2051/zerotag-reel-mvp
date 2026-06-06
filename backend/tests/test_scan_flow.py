from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from backend.app.models.event import Event
from backend.app.models.scan_transaction import ScanTransaction


PayloadLoader = Callable[[str], dict[str, Any]]


def _database_counts(
    session_factory: sessionmaker[Session],
) -> tuple[int, int]:
    """Đếm ScanTransaction và Event trong database test."""

    with session_factory() as session:
        transaction_count = session.scalar(
            select(func.count(ScanTransaction.id))
        ) or 0

        event_count = session.scalar(
            select(func.count(Event.id))
        ) or 0

    return transaction_count, event_count


def _load_transaction_snapshot(
    session_factory: sessionmaker[Session],
    request_id: str,
) -> dict[str, Any]:
    """Đọc transaction và event timeline theo request ID."""

    with session_factory() as session:
        statement = (
            select(ScanTransaction)
            .options(
                selectinload(ScanTransaction.events),
            )
            .where(
                ScanTransaction.request_id == request_id
            )
        )

        transaction = session.scalar(statement)

        assert transaction is not None

        return {
            "transaction_id": transaction.transaction_id,
            "final_result": transaction.final_result.value,
            "component_id": transaction.component_id,
            "violations_json": transaction.violations_json,
            "event_types": [
                event.event_type.value
                for event in transaction.events
            ],
            "sequence_numbers": [
                event.sequence_no
                for event in transaction.events
            ],
        }


@pytest.mark.parametrize(
    (
        "filename",
        "expected_status",
        "expected_event_type",
        "expected_led",
        "expected_buzzer",
        "expected_events",
        "component_expected",
    ),
    [
        (
            "valid_scan.json",
            "VALID",
            "BOM_MATCH_OK",
            "GREEN",
            "SHORT_BEEP",
            [
                "REEL_SCANNED",
                "BOM_CHECK_STARTED",
                "BOM_MATCH_OK",
            ],
            True,
        ),
        (
            "wrong_part.json",
            "WRONG_PART",
            "BOM_MATCH_FAIL",
            "RED",
            "LONG_BEEP",
            [
                "REEL_SCANNED",
                "BOM_CHECK_STARTED",
                "BOM_MATCH_FAIL",
                "WARNING_ISSUED",
            ],
            True,
        ),
        (
            "wrong_lot.json",
            "LOT_MISMATCH",
            "LOT_MISMATCH",
            "YELLOW",
            "DOUBLE_BEEP",
            [
                "REEL_SCANNED",
                "BOM_CHECK_STARTED",
                "LOT_MISMATCH",
                "WARNING_ISSUED",
            ],
            True,
        ),
        (
            "unknown_tag.json",
            "UNKNOWN_TAG",
            "UNKNOWN_TAG",
            "RED",
            "LONG_BEEP",
            [
                "REEL_SCANNED",
                "UNKNOWN_TAG",
                "WARNING_ISSUED",
            ],
            False,
        ),
    ],
)
def test_main_scan_cases(
    client: TestClient,
    seeded_session_factory: sessionmaker[Session],
    load_sample_payload: PayloadLoader,
    filename: str,
    expected_status: str,
    expected_event_type: str,
    expected_led: str,
    expected_buzzer: str,
    expected_events: list[str],
    component_expected: bool,
) -> None:
    """Bốn case chính phải đúng từ HTTP đến database."""

    payload = load_sample_payload(filename)

    response = client.post(
        "/api/v1/scans",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["request_id"] == payload["request_id"]
    assert data["transaction_id"].startswith("TX-")
    assert data["mode"] == "BOM_CHECK"

    assert data["status"] == expected_status
    assert data["event_type"] == expected_event_type

    assert data["gateway_action"] == {
        "led": expected_led,
        "buzzer": expected_buzzer,
    }

    assert data["replayed"] is False
    assert data["processed_at"] is not None

    assert data["bom_check"] is not None
    assert data["bom_check"]["bom_code"] == "PCB-DEMO-01"
    assert data["bom_check"]["bom_ref"] == "R12"

    if component_expected:
        assert data["component"] is not None
        assert (
            data["component"]["zerotag_id"]
            == payload["zerotag_id"]
        )
    else:
        assert data["component"] is None

    if expected_status == "VALID":
        assert data["violations"] == []
    else:
        assert expected_status in data["violations"]

    transaction_count, event_count = _database_counts(
        seeded_session_factory
    )

    assert transaction_count == 1
    assert event_count == len(expected_events)

    snapshot = _load_transaction_snapshot(
        seeded_session_factory,
        payload["request_id"],
    )

    assert (
        snapshot["transaction_id"]
        == data["transaction_id"]
    )

    assert snapshot["final_result"] == expected_status
    assert snapshot["event_types"] == expected_events

    assert snapshot["sequence_numbers"] == list(
        range(1, len(expected_events) + 1)
    )

    if component_expected:
        assert snapshot["component_id"] is not None
    else:
        assert snapshot["component_id"] is None


def test_event_log_endpoint_returns_generated_events(
    client: TestClient,
    load_sample_payload: PayloadLoader,
) -> None:
    """Event Log API phải đọc được event vừa tạo."""

    payload = load_sample_payload(
        "wrong_part.json"
    )

    scan_response = client.post(
        "/api/v1/scans",
        json=payload,
    )

    assert scan_response.status_code == 200

    transaction_id = scan_response.json()[
        "transaction_id"
    ]

    event_response = client.get(
        "/api/v1/events",
        params={
            "transaction_id": transaction_id,
        },
    )

    assert event_response.status_code == 200

    events = sorted(
        event_response.json(),
        key=lambda item: item["sequence_no"],
    )

    assert [
        event["event_type"]
        for event in events
    ] == [
        "REEL_SCANNED",
        "BOM_CHECK_STARTED",
        "BOM_MATCH_FAIL",
        "WARNING_ISSUED",
    ]

    assert [
        event["sequence_no"]
        for event in events
    ] == [1, 2, 3, 4]


def test_same_request_is_replayed_without_duplicates(
    client: TestClient,
    seeded_session_factory: sessionmaker[Session],
    load_sample_payload: PayloadLoader,
) -> None:
    """Gửi lại cùng payload không được nhân đôi audit log."""

    payload = load_sample_payload(
        "valid_scan.json"
    )

    first_response = client.post(
        "/api/v1/scans",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/scans",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["replayed"] is False
    assert second_data["replayed"] is True

    assert (
        first_data["transaction_id"]
        == second_data["transaction_id"]
    )

    assert first_data["status"] == "VALID"
    assert second_data["status"] == "VALID"

    transaction_count, event_count = _database_counts(
        seeded_session_factory
    )

    assert transaction_count == 1
    assert event_count == 3


def test_request_id_conflict_returns_409(
    client: TestClient,
    seeded_session_factory: sessionmaker[Session],
    load_sample_payload: PayloadLoader,
) -> None:
    """Cùng request_id nhưng payload khác phải bị từ chối."""

    original_payload = load_sample_payload(
        "valid_scan.json"
    )

    first_response = client.post(
        "/api/v1/scans",
        json=original_payload,
    )

    assert first_response.status_code == 200

    conflicting_payload = dict(original_payload)

    conflicting_payload["zerotag_id"] = "ZT-R1005"
    conflicting_payload["tag_uid"] = "UID-R1005"

    conflict_response = client.post(
        "/api/v1/scans",
        json=conflicting_payload,
    )

    assert conflict_response.status_code == 409

    error_data = conflict_response.json()

    assert (
        error_data["error"]["code"]
        == "REQUEST_ID_CONFLICT"
    )

    assert (
        error_data["error"]["details"]["request_id"]
        == original_payload["request_id"]
    )

    changed_fields = error_data["error"]["details"][
        "changed_fields"
    ]

    assert "zerotag_id" in changed_fields
    assert "tag_uid" in changed_fields

    transaction_count, event_count = _database_counts(
        seeded_session_factory
    )

    assert transaction_count == 1
    assert event_count == 3


def test_invalid_scan_payload_returns_422_without_writes(
    client: TestClient,
    seeded_session_factory: sessionmaker[Session],
    load_sample_payload: PayloadLoader,
) -> None:
    """Payload sai schema không được gọi business flow."""

    payload = load_sample_payload(
        "valid_scan.json"
    )

    payload.pop("bom_ref")

    response = client.post(
        "/api/v1/scans",
        json=payload,
    )

    assert response.status_code == 422

    transaction_count, event_count = _database_counts(
        seeded_session_factory
    )

    assert transaction_count == 0
    assert event_count == 0