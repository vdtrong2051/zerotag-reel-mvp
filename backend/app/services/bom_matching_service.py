from __future__ import annotations

from dataclasses import dataclass

from backend.app.core.enums import (
    BuzzerAction,
    ComponentStatus,
    EventType,
    LedAction,
    ScanResult,
)
from backend.app.models.bom_item import BomItem
from backend.app.models.component import Component


@dataclass(frozen=True, slots=True)
class GatewayActionDecision:
    """Hành động vật lý Gateway cần thực hiện."""

    led: LedAction
    buzzer: BuzzerAction


@dataclass(frozen=True, slots=True)
class BomMatchResult:
    """Kết quả nội bộ của quá trình đối chiếu Component với BOMItem."""

    status: ScanResult
    message: str
    event_type: EventType
    violations: tuple[ScanResult, ...]
    gateway_action: GatewayActionDecision
    quantity_sufficient: bool

    @property
    def is_valid(self) -> bool:
        return self.status == ScanResult.VALID


_GATEWAY_ACTIONS: dict[ScanResult, GatewayActionDecision] = {
    ScanResult.VALID: GatewayActionDecision(
        led=LedAction.GREEN,
        buzzer=BuzzerAction.SHORT_BEEP,
    ),
    ScanResult.WRONG_PART: GatewayActionDecision(
        led=LedAction.RED,
        buzzer=BuzzerAction.LONG_BEEP,
    ),
    ScanResult.LOT_MISMATCH: GatewayActionDecision(
        led=LedAction.YELLOW,
        buzzer=BuzzerAction.DOUBLE_BEEP,
    ),
    ScanResult.DATECODE_MISMATCH: GatewayActionDecision(
        led=LedAction.YELLOW,
        buzzer=BuzzerAction.DOUBLE_BEEP,
    ),
    ScanResult.BLOCKED_TAG: GatewayActionDecision(
        led=LedAction.RED,
        buzzer=BuzzerAction.LONG_BEEP,
    ),
}


_EVENT_TYPES: dict[ScanResult, EventType] = {
    ScanResult.VALID: EventType.BOM_MATCH_OK,
    ScanResult.WRONG_PART: EventType.BOM_MATCH_FAIL,
    ScanResult.LOT_MISMATCH: EventType.LOT_MISMATCH,
    ScanResult.DATECODE_MISMATCH: EventType.DATECODE_MISMATCH,
    ScanResult.BLOCKED_TAG: EventType.BLOCKED_TAG,
}


_MESSAGES: dict[ScanResult, str] = {
    ScanResult.VALID: (
        "Correct part number, lot and date-code."
    ),
    ScanResult.WRONG_PART: (
        "Scanned component does not match the selected BOM item."
    ),
    ScanResult.LOT_MISMATCH: (
        "Component part number is correct but lot does not match."
    ),
    ScanResult.DATECODE_MISMATCH: (
        "Component date-code is outside the allowed range."
    ),
    ScanResult.BLOCKED_TAG: (
        "Component is blocked and cannot be used."
    ),
}


_RESULT_PRIORITY: tuple[ScanResult, ...] = (
    ScanResult.BLOCKED_TAG,
    ScanResult.WRONG_PART,
    ScanResult.LOT_MISMATCH,
    ScanResult.DATECODE_MISMATCH,
)


def _is_lot_allowed(
    component_lot: str,
    allowed_lot: str | None,
) -> bool:
    """Lot rỗng trong BOM nghĩa là không giới hạn lot."""

    if allowed_lot is None or not allowed_lot.strip():
        return True

    return component_lot == allowed_lot


def _compare_date_code(
    left: str,
    right: str,
) -> int:
    """So sánh date-code số hoặc chuỗi có cùng định dạng."""

    if left.isdigit() and right.isdigit():
        left_value = int(left)
        right_value = int(right)

        return (left_value > right_value) - (
            left_value < right_value
        )

    return (left > right) - (left < right)


def _is_date_code_allowed(
    date_code: str,
    allowed_from: str | None,
    allowed_to: str | None,
) -> bool:
    """Kiểm tra date-code theo hai biên tùy chọn."""

    if (
        allowed_from is not None
        and allowed_from.strip()
        and _compare_date_code(date_code, allowed_from) < 0
    ):
        return False

    if (
        allowed_to is not None
        and allowed_to.strip()
        and _compare_date_code(date_code, allowed_to) > 0
    ):
        return False

    return True


def _select_primary_status(
    violations: list[ScanResult],
) -> ScanResult:
    """Chọn status chính theo thứ tự ưu tiên nghiệp vụ."""

    for status in _RESULT_PRIORITY:
        if status in violations:
            return status

    return ScanResult.VALID


def match_component_to_bom_item(
    component: Component,
    bom_item: BomItem,
) -> BomMatchResult:
    """Đối chiếu một Component với một dòng BOM cụ thể."""

    violations: list[ScanResult] = []

    if component.status == ComponentStatus.BLOCKED:
        violations.append(ScanResult.BLOCKED_TAG)

    if component.part_number != bom_item.required_part_number:
        violations.append(ScanResult.WRONG_PART)

    if not _is_lot_allowed(
        component.lot_number,
        bom_item.allowed_lot,
    ):
        violations.append(ScanResult.LOT_MISMATCH)

    if not _is_date_code_allowed(
        component.date_code,
        bom_item.allowed_date_code_from,
        bom_item.allowed_date_code_to,
    ):
        violations.append(ScanResult.DATECODE_MISMATCH)

    quantity_sufficient = (
        component.quantity_current
        >= bom_item.required_quantity
    )

    status = _select_primary_status(violations)

    return BomMatchResult(
        status=status,
        message=_MESSAGES[status],
        event_type=_EVENT_TYPES[status],
        violations=tuple(violations),
        gateway_action=_GATEWAY_ACTIONS[status],
        quantity_sufficient=quantity_sufficient,
    )