from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.core.enums import (
    EventResult,
    EventType,
    ScanResult,
)
from backend.app.models.bom_item import BomItem
from backend.app.models.component import Component
from backend.app.models.event import Event
from backend.app.models.scan_transaction import ScanTransaction
from backend.app.repositories import event_repo


@dataclass(frozen=True, slots=True)
class EventDefinition:
    """Định nghĩa một Event trước khi ghi vào database."""

    event_type: EventType
    result: EventResult
    message: str
    metadata: dict[str, Any]


def _generate_event_id() -> str:
    """Sinh mã Event duy nhất, không phụ thuộc database ID."""

    return f"EVT-{uuid4().hex.upper()}"


def _build_common_metadata(
    *,
    transaction: ScanTransaction,
    status: ScanResult,
    violations: tuple[ScanResult, ...],
    component: Component | None,
    bom_item: BomItem | None,
) -> dict[str, Any]:
    """Tạo metadata chung cho toàn bộ Event của một lần scan."""

    metadata: dict[str, Any] = {
        "request_id": transaction.request_id,
        "transaction_id": transaction.transaction_id,
        "mode": transaction.mode.value,
        "location": transaction.location,
        "scan_result": status.value,
        "violations": [
            violation.value
            for violation in violations
        ],
    }

    if component is not None:
        metadata["component"] = {
            "zerotag_id": component.zerotag_id,
            "tag_uid": component.tag_uid,
            "part_number": component.part_number,
            "lot_number": component.lot_number,
            "date_code": component.date_code,
            "status": component.status.value,
        }

    if bom_item is not None:
        metadata["bom_item"] = {
            "bom_item_id": bom_item.id,
            "bom_ref": bom_item.bom_ref,
            "required_part_number": (
                bom_item.required_part_number
            ),
            "allowed_lot": bom_item.allowed_lot,
            "allowed_date_code_from": (
                bom_item.allowed_date_code_from
            ),
            "allowed_date_code_to": (
                bom_item.allowed_date_code_to
            ),
            "required_quantity": (
                bom_item.required_quantity
            ),
        }

    return metadata


def _definition(
    *,
    common_metadata: dict[str, Any],
    event_type: EventType,
    result: EventResult,
    message: str,
    details: dict[str, Any] | None = None,
) -> EventDefinition:
    """Tạo EventDefinition với metadata riêng biệt."""

    metadata = dict(common_metadata)
    metadata["event_type"] = event_type.value

    if details:
        metadata.update(details)

    return EventDefinition(
        event_type=event_type,
        result=result,
        message=message,
        metadata=metadata,
    )


def build_event_definitions(
    *,
    transaction: ScanTransaction,
    status: ScanResult,
    violations: tuple[ScanResult, ...] = (),
    component: Component | None = None,
    bom_item: BomItem | None = None,
) -> list[EventDefinition]:
    """Xác định audit trail cần tạo cho một scan result."""

    common_metadata = _build_common_metadata(
        transaction=transaction,
        status=status,
        violations=violations,
        component=component,
        bom_item=bom_item,
    )

    definitions = [
        _definition(
            common_metadata=common_metadata,
            event_type=EventType.REEL_SCANNED,
            result=EventResult.OK,
            message="Scan request was received.",
        )
    ]

    bom_check_results = {
        ScanResult.VALID,
        ScanResult.WRONG_PART,
        ScanResult.LOT_MISMATCH,
        ScanResult.DATECODE_MISMATCH,
    }

    if status in bom_check_results:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.BOM_CHECK_STARTED,
                result=EventResult.OK,
                message="BOM check was started.",
            )
        )

    if status == ScanResult.VALID:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.BOM_MATCH_OK,
                result=EventResult.OK,
                message=(
                    "Component matches the selected BOM item."
                ),
            )
        )

        return definitions

    if status == ScanResult.WRONG_PART:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.BOM_MATCH_FAIL,
                result=EventResult.FAIL,
                message=(
                    "Component part number does not match "
                    "the selected BOM item."
                ),
            )
        )

    elif status == ScanResult.LOT_MISMATCH:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.LOT_MISMATCH,
                result=EventResult.WARNING,
                message=(
                    "Component lot does not match "
                    "the allowed BOM lot."
                ),
            )
        )

        if ScanResult.DATECODE_MISMATCH in violations:
            definitions.append(
                _definition(
                    common_metadata=common_metadata,
                    event_type=EventType.DATECODE_MISMATCH,
                    result=EventResult.WARNING,
                    message=(
                        "Component date-code is outside "
                        "the allowed range."
                    ),
                )
            )

    elif status == ScanResult.DATECODE_MISMATCH:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.DATECODE_MISMATCH,
                result=EventResult.WARNING,
                message=(
                    "Component date-code is outside "
                    "the allowed range."
                ),
            )
        )

    elif status == ScanResult.UNKNOWN_TAG:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.UNKNOWN_TAG,
                result=EventResult.FAIL,
                message=(
                    "Component could not be identified "
                    "from the supplied tag data."
                ),
            )
        )

    elif status == ScanResult.BLOCKED_TAG:
        definitions.append(
            _definition(
                common_metadata=common_metadata,
                event_type=EventType.BLOCKED_TAG,
                result=EventResult.FAIL,
                message="Component is blocked.",
            )
        )

    else:
        raise ValueError(
            f"Unsupported scan result for Day 3: {status.value}"
        )

    definitions.append(
        _definition(
            common_metadata=common_metadata,
            event_type=EventType.WARNING_ISSUED,
            result=EventResult.WARNING,
            message="Manual review is required.",
        )
    )

    return definitions


def create_scan_events(
    session: Session,
    *,
    transaction: ScanTransaction,
    status: ScanResult,
    violations: tuple[ScanResult, ...] = (),
    component: Component | None = None,
    bom_item: BomItem | None = None,
) -> list[Event]:
    """Tạo toàn bộ Event của một ScanTransaction.

    Hàm chỉ add và flush Event thông qua repository.
    Việc commit hoặc rollback thuộc trách nhiệm của Scan Service.
    """

    if transaction.id is None:
        raise ValueError(
            "ScanTransaction must be flushed before creating events."
        )

    definitions = build_event_definitions(
        transaction=transaction,
        status=status,
        violations=violations,
        component=component,
        bom_item=bom_item,
    )

    events: list[Event] = []

    for sequence_no, definition in enumerate(
        definitions,
        start=1,
    ):
        event = Event(
            event_id=_generate_event_id(),
            scan_transaction_id=transaction.id,
            sequence_no=sequence_no,
            event_type=definition.event_type,
            result=definition.result,
            message=definition.message,
            metadata_json=json.dumps(
                definition.metadata,
                ensure_ascii=False,
                sort_keys=True,
            ),
        )

        events.append(
            event_repo.create_event(
                session,
                event,
            )
        )

    return events