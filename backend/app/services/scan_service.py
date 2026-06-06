from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.enums import (
    BuzzerAction,
    EventType,
    LedAction,
    ScanMode,
    ScanResult,
)
from backend.app.core.errors import (
    AppError,
    ConflictError,
    DatabaseOperationError,
    InvalidRequestError,
    ResourceNotFoundError,
)
from backend.app.models.bom import Bom
from backend.app.models.bom_item import BomItem
from backend.app.models.component import Component
from backend.app.models.scan_transaction import ScanTransaction
from backend.app.repositories import (
    bom_repo,
    component_repo,
    gateway_repo,
    scan_repo,
)
from backend.app.schemas.scan_schema import (
    BomCheckSnapshot,
    ComponentSnapshot,
    GatewayAction,
    ScanRequest,
    ScanResponse,
)
from backend.app.services.bom_matching_service import (
    BomMatchResult,
    match_component_to_bom_item,
)
from backend.app.services.event_service import create_scan_events


_EVENT_TYPE_BY_STATUS: dict[ScanResult, EventType] = {
    ScanResult.VALID: EventType.BOM_MATCH_OK,
    ScanResult.WRONG_PART: EventType.BOM_MATCH_FAIL,
    ScanResult.LOT_MISMATCH: EventType.LOT_MISMATCH,
    ScanResult.DATECODE_MISMATCH: EventType.DATECODE_MISMATCH,
    ScanResult.UNKNOWN_TAG: EventType.UNKNOWN_TAG,
    ScanResult.BLOCKED_TAG: EventType.BLOCKED_TAG,
}


_GATEWAY_ACTION_BY_STATUS: dict[
    ScanResult,
    tuple[LedAction, BuzzerAction],
] = {
    ScanResult.VALID: (
        LedAction.GREEN,
        BuzzerAction.SHORT_BEEP,
    ),
    ScanResult.WRONG_PART: (
        LedAction.RED,
        BuzzerAction.LONG_BEEP,
    ),
    ScanResult.LOT_MISMATCH: (
        LedAction.YELLOW,
        BuzzerAction.DOUBLE_BEEP,
    ),
    ScanResult.DATECODE_MISMATCH: (
        LedAction.YELLOW,
        BuzzerAction.DOUBLE_BEEP,
    ),
    ScanResult.UNKNOWN_TAG: (
        LedAction.RED,
        BuzzerAction.LONG_BEEP,
    ),
    ScanResult.BLOCKED_TAG: (
        LedAction.RED,
        BuzzerAction.LONG_BEEP,
    ),
}


_UNKNOWN_TAG_MESSAGE = (
    "Component could not be identified from the supplied tag data."
)


def _generate_transaction_id() -> str:
    """Sinh mã transaction độc lập với khóa số trong database."""

    return f"TX-{uuid4().hex.upper()}"


def _datetime_key(value: datetime) -> str:
    """Chuẩn hóa datetime để so sánh request replay.

    SQLite có thể trả DateTime mà không giữ timezone offset.
    Vì vậy, replay so sánh phần thời gian cục bộ đã gửi.
    """

    return value.replace(
        tzinfo=None,
    ).isoformat(
        timespec="microseconds",
    )


def _ensure_timezone(value: datetime) -> datetime:
    """Đảm bảo datetime trả qua response luôn có timezone."""

    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)

    return value


def _request_signature(
    request: ScanRequest,
) -> dict[str, Any]:
    """Biểu diễn các field nghiệp vụ của request."""

    return {
        "gateway_id": request.gateway_id,
        "mode": request.mode.value,
        "location": request.location,
        "zerotag_id": request.zerotag_id,
        "tag_uid": request.tag_uid,
        "qr_id": request.qr_id,
        "rfid_id": request.rfid_id,
        "bom_code": request.bom_code,
        "bom_ref": request.bom_ref,
        "read_at": _datetime_key(request.read_at),
    }


def _transaction_signature(
    transaction: ScanTransaction,
) -> dict[str, Any]:
    """Dựng lại signature từ transaction đã lưu."""

    gateway_id = (
        transaction.gateway.gateway_id
        if transaction.gateway is not None
        else None
    )

    bom_code = (
        transaction.bom.bom_code
        if transaction.bom is not None
        else None
    )

    bom_ref = (
        transaction.bom_item.bom_ref
        if transaction.bom_item is not None
        else None
    )

    return {
        "gateway_id": gateway_id,
        "mode": transaction.mode.value,
        "location": transaction.location,
        "zerotag_id": transaction.input_zerotag_id,
        "tag_uid": transaction.input_tag_uid,
        "qr_id": transaction.input_qr_id,
        "rfid_id": transaction.input_rfid_id,
        "bom_code": bom_code,
        "bom_ref": bom_ref,
        "read_at": _datetime_key(transaction.read_at),
    }


def _validate_replay_request(
    *,
    request: ScanRequest,
    transaction: ScanTransaction,
) -> None:
    """Từ chối request_id cũ nếu payload đã bị thay đổi."""

    request_signature = _request_signature(request)
    stored_signature = _transaction_signature(transaction)

    if request_signature != stored_signature:
        changed_fields = sorted(
            field_name
            for field_name in request_signature
            if request_signature[field_name]
            != stored_signature[field_name]
        )

        raise ConflictError(
            (
                f"request_id '{request.request_id}' "
                "was already used with a different payload."
            ),
            code="REQUEST_ID_CONFLICT",
            details={
                "request_id": request.request_id,
                "changed_fields": changed_fields,
            },
        )


def _find_component(
    session: Session,
    request: ScanRequest,
) -> Component | None:
    """Tìm Component theo ZeroTag ID, sau đó fallback sang tag UID."""

    component: Component | None = None

    if request.zerotag_id is not None:
        component = component_repo.get_by_zerotag_id(
            session,
            request.zerotag_id,
        )

    if component is None and request.tag_uid is not None:
        component = component_repo.get_by_tag_uid(
            session,
            request.tag_uid,
        )

    return component


def _parse_violations(
    violations_json: str,
) -> tuple[ScanResult, ...]:
    """Đọc violations đã lưu trong ScanTransaction."""

    try:
        raw_values = json.loads(violations_json)
    except json.JSONDecodeError:
        return ()

    if not isinstance(raw_values, list):
        return ()

    violations: list[ScanResult] = []

    for raw_value in raw_values:
        try:
            violations.append(
                ScanResult(raw_value)
            )
        except ValueError:
            continue

    return tuple(violations)


def _gateway_action_for_status(
    status: ScanResult,
) -> GatewayAction:
    """Dựng gateway action từ kết quả scan."""

    try:
        led, buzzer = _GATEWAY_ACTION_BY_STATUS[status]
    except KeyError as error:
        raise ValueError(
            f"Unsupported Day 3 scan result: {status.value}"
        ) from error

    return GatewayAction(
        led=led,
        buzzer=buzzer,
    )


def _event_type_for_status(
    status: ScanResult,
) -> EventType:
    """Lấy Event đại diện cho kết quả cuối."""

    try:
        return _EVENT_TYPE_BY_STATUS[status]
    except KeyError as error:
        raise ValueError(
            f"Unsupported Day 3 scan result: {status.value}"
        ) from error


def _build_component_snapshot(
    *,
    transaction: ScanTransaction,
    component: Component | None,
) -> ComponentSnapshot | None:
    if component is None:
        return None

    status_before = (
        transaction.component_status_before
        or component.status
    )

    status_after = (
        transaction.component_status_after
        or component.status
    )

    return ComponentSnapshot(
        zerotag_id=component.zerotag_id,
        part_number=component.part_number,
        lot_number=component.lot_number,
        date_code=component.date_code,
        quantity_current=component.quantity_current,
        status_before=status_before,
        status_after=status_after,
        location=component.location,
    )


def _build_bom_snapshot(
    *,
    bom: Bom | None,
    bom_item: BomItem | None,
    quantity_sufficient: bool,
) -> BomCheckSnapshot | None:
    if bom is None or bom_item is None:
        return None

    return BomCheckSnapshot(
        bom_code=bom.bom_code,
        bom_ref=bom_item.bom_ref,
        required_part_number=(
            bom_item.required_part_number
        ),
        required_lot=bom_item.allowed_lot,
        allowed_date_code_from=(
            bom_item.allowed_date_code_from
        ),
        allowed_date_code_to=(
            bom_item.allowed_date_code_to
        ),
        required_quantity=bom_item.required_quantity,
        quantity_sufficient=quantity_sufficient,
    )


def _build_scan_response(
    *,
    transaction: ScanTransaction,
    component: Component | None,
    bom: Bom | None,
    bom_item: BomItem | None,
    event_type: EventType,
    gateway_action: GatewayAction,
    violations: tuple[ScanResult, ...],
    quantity_sufficient: bool,
    replayed: bool,
) -> ScanResponse:
    """Chuyển kết quả xử lý thành response contract."""

    processed_at = (
        transaction.completed_at
        or transaction.started_at
        or datetime.now(UTC)
    )

    return ScanResponse(
        request_id=transaction.request_id,
        transaction_id=transaction.transaction_id,
        mode=transaction.mode,
        status=transaction.final_result,
        message=transaction.message or "",
        event_type=event_type,
        violations=list(violations),
        component=_build_component_snapshot(
            transaction=transaction,
            component=component,
        ),
        bom_check=_build_bom_snapshot(
            bom=bom,
            bom_item=bom_item,
            quantity_sufficient=quantity_sufficient,
        ),
        gateway_action=gateway_action,
        replayed=replayed,
        processed_at=_ensure_timezone(processed_at),
    )


def _build_replay_response(
    transaction: ScanTransaction,
) -> ScanResponse:
    """Dựng lại response mà không tạo transaction hoặc event mới."""

    component = transaction.component
    bom = transaction.bom
    bom_item = transaction.bom_item

    quantity_sufficient = (
        component is not None
        and bom_item is not None
        and component.quantity_current
        >= bom_item.required_quantity
    )

    violations = _parse_violations(
        transaction.violations_json
    )

    return _build_scan_response(
        transaction=transaction,
        component=component,
        bom=bom,
        bom_item=bom_item,
        event_type=_event_type_for_status(
            transaction.final_result
        ),
        gateway_action=_gateway_action_for_status(
            transaction.final_result
        ),
        violations=violations,
        quantity_sufficient=quantity_sufficient,
        replayed=True,
    )


def _validate_supported_mode(
    request: ScanRequest,
) -> None:
    """Day 3 chỉ thực thi nghiệp vụ BOM_CHECK."""

    if request.mode != ScanMode.BOM_CHECK:
        raise InvalidRequestError(
            (
                f"Scan mode '{request.mode.value}' "
                "is not implemented in Day 3."
            ),
            code="UNSUPPORTED_SCAN_MODE",
            details={
                "mode": request.mode.value,
                "supported_modes": [
                    ScanMode.BOM_CHECK.value,
                ],
            },
        )


def process_scan(
    session: Session,
    request: ScanRequest,
) -> ScanResponse:
    """Điều phối toàn bộ BOM_CHECK scan flow.

    Transaction database gồm ScanTransaction và toàn bộ Events.
    Chỉ commit đúng một lần sau khi response đã dựng thành công.
    """

    try:
        existing_transaction = scan_repo.get_by_request_id(
            session,
            request.request_id,
            include_details=True,
        )

        if existing_transaction is not None:
            _validate_replay_request(
                request=request,
                transaction=existing_transaction,
            )

            return _build_replay_response(
                existing_transaction
            )

        _validate_supported_mode(request)

        gateway = gateway_repo.get_by_gateway_id(
            session,
            request.gateway_id,
        )

        if gateway is None:
            raise ResourceNotFoundError(
                "gateway",
                request.gateway_id,
            )

        assert request.bom_code is not None
        assert request.bom_ref is not None

        bom = bom_repo.get_by_bom_code(
            session,
            request.bom_code,
            include_items=False,
        )

        if bom is None:
            raise ResourceNotFoundError(
                "bom",
                request.bom_code,
            )

        bom_item = bom_repo.get_item_by_ref(
            session,
            bom_code=request.bom_code,
            bom_ref=request.bom_ref,
        )

        if bom_item is None:
            raise ResourceNotFoundError(
                "bom_item",
                f"{request.bom_code}:{request.bom_ref}",
                details={
                    "bom_code": request.bom_code,
                    "bom_ref": request.bom_ref,
                },
            )

        component = _find_component(
            session,
            request,
        )

        match_result: BomMatchResult | None = None

        if component is None:
            status = ScanResult.UNKNOWN_TAG
            message = _UNKNOWN_TAG_MESSAGE
            event_type = EventType.UNKNOWN_TAG
            violations = (
                ScanResult.UNKNOWN_TAG,
            )
            gateway_action = GatewayAction(
                led=LedAction.RED,
                buzzer=BuzzerAction.LONG_BEEP,
            )
            quantity_sufficient = False
        else:
            match_result = match_component_to_bom_item(
                component,
                bom_item,
            )

            status = match_result.status
            message = match_result.message
            event_type = match_result.event_type
            violations = match_result.violations
            gateway_action = GatewayAction(
                led=match_result.gateway_action.led,
                buzzer=match_result.gateway_action.buzzer,
            )
            quantity_sufficient = (
                match_result.quantity_sufficient
            )

        processed_at = datetime.now(UTC)

        transaction = ScanTransaction(
            transaction_id=_generate_transaction_id(),
            request_id=request.request_id,
            component_id=(
                component.id
                if component is not None
                else None
            ),
            gateway_ref_id=gateway.id,
            bom_id=bom.id,
            bom_item_id=bom_item.id,
            mode=request.mode,
            location=request.location,
            input_zerotag_id=request.zerotag_id,
            input_tag_uid=request.tag_uid,
            input_qr_id=request.qr_id,
            input_rfid_id=request.rfid_id,
            final_result=status,
            violations_json=json.dumps(
                [
                    violation.value
                    for violation in violations
                ],
                ensure_ascii=False,
            ),
            message=message,
            component_status_before=(
                component.status
                if component is not None
                else None
            ),
            component_status_after=(
                component.status
                if component is not None
                else None
            ),
            read_at=request.read_at,
            completed_at=processed_at,
        )

        scan_repo.create_transaction(
            session,
            transaction,
        )

        create_scan_events(
            session,
            transaction=transaction,
            status=status,
            violations=violations,
            component=component,
            bom_item=bom_item,
        )

        response = _build_scan_response(
            transaction=transaction,
            component=component,
            bom=bom,
            bom_item=bom_item,
            event_type=event_type,
            gateway_action=gateway_action,
            violations=violations,
            quantity_sufficient=quantity_sufficient,
            replayed=False,
        )

        session.commit()

        return response

    except AppError:
        session.rollback()
        raise

    except SQLAlchemyError as error:
        session.rollback()

        raise DatabaseOperationError(
            details={
                "operation": "process_scan",
                "request_id": request.request_id,
                "reason": str(error),
            }
        ) from error

    except Exception:
        session.rollback()
        raise