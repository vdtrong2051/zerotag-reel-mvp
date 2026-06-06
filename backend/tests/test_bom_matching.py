from __future__ import annotations

from backend.app.core.enums import (
    BuzzerAction,
    ComponentStatus,
    EventType,
    LabelType,
    LedAction,
    ScanResult,
    TamperStatus,
)
from backend.app.models.bom_item import BomItem
from backend.app.models.component import Component
from backend.app.services.bom_matching_service import (
    match_component_to_bom_item,
)


def make_component(
    *,
    part_number: str = "RES-10K-0603",
    lot_number: str = "L2026A01",
    date_code: str = "2520",
    quantity_current: int = 5000,
    status: ComponentStatus = ComponentStatus.IN_STOCK,
) -> Component:
    return Component(
        zerotag_id="ZT-TEST",
        tag_uid="UID-TEST",
        part_number=part_number,
        component_name="Test Component",
        manufacturer="Test Manufacturer",
        supplier="Test Supplier",
        lot_number=lot_number,
        date_code=date_code,
        quantity_initial=5000,
        quantity_current=quantity_current,
        status=status,
        location="Test Warehouse",
        label_type=LabelType.STANDARD,
        tamper_status=TamperStatus.NORMAL,
    )


def make_bom_item(
    *,
    required_part_number: str = "RES-10K-0603",
    allowed_lot: str | None = "L2026A01",
    allowed_date_code_from: str | None = "2520",
    allowed_date_code_to: str | None = "2540",
    required_quantity: int = 100,
) -> BomItem:
    return BomItem(
        bom_id=1,
        bom_ref="R12",
        required_part_number=required_part_number,
        allowed_lot=allowed_lot,
        allowed_date_code_from=allowed_date_code_from,
        allowed_date_code_to=allowed_date_code_to,
        required_quantity=required_quantity,
        note="Test BOM item",
    )


def test_valid_bom_match() -> None:
    result = match_component_to_bom_item(
        make_component(),
        make_bom_item(),
    )

    assert result.status == ScanResult.VALID
    assert result.violations == ()
    assert result.event_type == EventType.BOM_MATCH_OK
    assert result.gateway_action.led == LedAction.GREEN
    assert (
        result.gateway_action.buzzer
        == BuzzerAction.SHORT_BEEP
    )
    assert result.quantity_sufficient is True
    assert result.is_valid is True


def test_wrong_part_has_high_priority() -> None:
    result = match_component_to_bom_item(
        make_component(
            part_number="CAP-10UF-0805",
        ),
        make_bom_item(),
    )

    assert result.status == ScanResult.WRONG_PART
    assert result.violations == (
        ScanResult.WRONG_PART,
    )
    assert result.event_type == EventType.BOM_MATCH_FAIL
    assert result.gateway_action.led == LedAction.RED
    assert (
        result.gateway_action.buzzer
        == BuzzerAction.LONG_BEEP
    )


def test_lot_mismatch_returns_warning_action() -> None:
    result = match_component_to_bom_item(
        make_component(
            lot_number="L2025X09",
        ),
        make_bom_item(),
    )

    assert result.status == ScanResult.LOT_MISMATCH
    assert result.violations == (
        ScanResult.LOT_MISMATCH,
    )
    assert result.event_type == EventType.LOT_MISMATCH
    assert result.gateway_action.led == LedAction.YELLOW
    assert (
        result.gateway_action.buzzer
        == BuzzerAction.DOUBLE_BEEP
    )


def test_date_code_mismatch() -> None:
    result = match_component_to_bom_item(
        make_component(
            date_code="2519",
        ),
        make_bom_item(),
    )

    assert result.status == ScanResult.DATECODE_MISMATCH
    assert result.violations == (
        ScanResult.DATECODE_MISMATCH,
    )
    assert result.event_type == EventType.DATECODE_MISMATCH
    assert result.gateway_action.led == LedAction.YELLOW
    assert (
        result.gateway_action.buzzer
        == BuzzerAction.DOUBLE_BEEP
    )


def test_multiple_violations_keep_primary_priority() -> None:
    result = match_component_to_bom_item(
        make_component(
            lot_number="L2025X09",
            date_code="2519",
        ),
        make_bom_item(),
    )

    assert result.status == ScanResult.LOT_MISMATCH
    assert result.violations == (
        ScanResult.LOT_MISMATCH,
        ScanResult.DATECODE_MISMATCH,
    )


def test_wrong_part_remains_primary_with_other_errors() -> None:
    result = match_component_to_bom_item(
        make_component(
            part_number="CAP-10UF-0805",
            lot_number="L2025X09",
            date_code="2519",
        ),
        make_bom_item(),
    )

    assert result.status == ScanResult.WRONG_PART
    assert result.violations == (
        ScanResult.WRONG_PART,
        ScanResult.LOT_MISMATCH,
        ScanResult.DATECODE_MISMATCH,
    )


def test_blocked_component_has_highest_priority() -> None:
    result = match_component_to_bom_item(
        make_component(
            part_number="CAP-10UF-0805",
            status=ComponentStatus.BLOCKED,
        ),
        make_bom_item(),
    )

    assert result.status == ScanResult.BLOCKED_TAG
    assert ScanResult.BLOCKED_TAG in result.violations
    assert ScanResult.WRONG_PART in result.violations
    assert result.event_type == EventType.BLOCKED_TAG
    assert result.gateway_action.led == LedAction.RED
    assert (
        result.gateway_action.buzzer
        == BuzzerAction.LONG_BEEP
    )


def test_quantity_insufficient_does_not_create_new_status() -> None:
    result = match_component_to_bom_item(
        make_component(
            quantity_current=50,
        ),
        make_bom_item(
            required_quantity=100,
        ),
    )

    assert result.status == ScanResult.VALID
    assert result.violations == ()
    assert result.quantity_sufficient is False


def test_empty_allowed_lot_accepts_any_component_lot() -> None:
    result = match_component_to_bom_item(
        make_component(
            lot_number="ANY-LOT",
        ),
        make_bom_item(
            allowed_lot=None,
        ),
    )

    assert result.status == ScanResult.VALID


def test_open_date_code_range_accepts_value() -> None:
    result = match_component_to_bom_item(
        make_component(
            date_code="2601",
        ),
        make_bom_item(
            allowed_date_code_from=None,
            allowed_date_code_to=None,
        ),
    )

    assert result.status == ScanResult.VALID