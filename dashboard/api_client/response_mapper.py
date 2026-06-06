from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

import pandas as pd


COMPONENT_TABLE_COLUMNS = [
    "ZeroTag ID",
    "Part Number",
    "Component Name",
    "Lot",
    "Date-code",
    "Initial Quantity",
    "Current Quantity",
    "Status",
    "Location",
    "Supplier",
    "Manufacturer",
    "Label Type",
    "Tamper Status",
    "Updated At",
]


EVENT_TABLE_COLUMNS = [
    "Time",
    "ZeroTag ID",
    "Event Type",
    "Result",
    "Message",
    "Location",
    "Transaction ID",
    "BOM Ref",
    "Sequence",
    "Event ID",
    "Created At",
]


def _text(
    value: Any,
    *,
    default: str = "—",
) -> str:
    """Chuyển một giá trị thành chuỗi hiển thị an toàn."""

    if value is None:
        return default

    cleaned = str(value).strip()

    return cleaned or default


def _integer(
    value: Any,
    *,
    default: int = 0,
) -> int:
    """Chuyển một giá trị thành số nguyên an toàn."""

    if isinstance(value, bool):
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_datetime(
    value: Any,
) -> datetime | None:
    """Đọc ISO datetime từ Backend."""

    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"

    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def format_datetime(
    value: Any,
    *,
    include_date: bool = True,
) -> str:
    """Định dạng thời gian dùng trên Dashboard."""

    parsed = _parse_datetime(value)

    if parsed is None:
        return "—"

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone()

    if include_date:
        return parsed.strftime("%Y-%m-%d %H:%M:%S")

    return parsed.strftime("%H:%M:%S")


def parse_event_metadata(
    metadata_json: Any,
) -> dict[str, Any]:
    """Đọc metadata_json của Event mà không làm UI bị lỗi."""

    if isinstance(metadata_json, dict):
        return dict(metadata_json)

    if not isinstance(metadata_json, str):
        return {}

    cleaned = metadata_json.strip()

    if not cleaned:
        return {}

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed


def _nested_mapping(
    value: Any,
) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value

    return {}


def get_event_zerotag_id(
    event: Mapping[str, Any],
) -> str | None:
    """Lấy ZeroTag ID từ metadata của Event."""

    metadata = parse_event_metadata(
        event.get("metadata_json")
    )

    component = _nested_mapping(
        metadata.get("component")
    )

    zerotag_id = component.get("zerotag_id")

    if not isinstance(zerotag_id, str):
        return None

    cleaned = zerotag_id.strip()

    return cleaned or None


def map_components_to_dataframe(
    components: Sequence[Mapping[str, Any]],
) -> pd.DataFrame:
    """Chuyển Component API response thành bảng Inventory."""

    rows: list[dict[str, Any]] = []

    for component in components:
        rows.append(
            {
                "ZeroTag ID": _text(
                    component.get("zerotag_id")
                ),
                "Part Number": _text(
                    component.get("part_number")
                ),
                "Component Name": _text(
                    component.get("component_name")
                ),
                "Lot": _text(
                    component.get("lot_number")
                ),
                "Date-code": _text(
                    component.get("date_code")
                ),
                "Initial Quantity": _integer(
                    component.get("quantity_initial")
                ),
                "Current Quantity": _integer(
                    component.get("quantity_current")
                ),
                "Status": _text(
                    component.get("status")
                ),
                "Location": _text(
                    component.get("location")
                ),
                "Supplier": _text(
                    component.get("supplier")
                ),
                "Manufacturer": _text(
                    component.get("manufacturer")
                ),
                "Label Type": _text(
                    component.get("label_type")
                ),
                "Tamper Status": _text(
                    component.get("tamper_status")
                ),
                "Updated At": format_datetime(
                    component.get("updated_at")
                ),
            }
        )

    return pd.DataFrame(
        rows,
        columns=COMPONENT_TABLE_COLUMNS,
    )


def map_events_to_dataframe(
    events: Sequence[Mapping[str, Any]],
) -> pd.DataFrame:
    """Chuyển Event API response thành bảng Event Log."""

    rows: list[dict[str, Any]] = []

    for event in events:
        metadata = parse_event_metadata(
            event.get("metadata_json")
        )

        component = _nested_mapping(
            metadata.get("component")
        )

        bom_item = _nested_mapping(
            metadata.get("bom_item")
        )

        created_at = event.get("created_at")

        rows.append(
            {
                "Time": format_datetime(
                    created_at,
                    include_date=False,
                ),
                "ZeroTag ID": _text(
                    component.get("zerotag_id")
                ),
                "Event Type": _text(
                    event.get("event_type")
                ),
                "Result": _text(
                    event.get("result")
                ),
                "Message": _text(
                    event.get("message")
                ),
                "Location": _text(
                    metadata.get("location")
                ),
                "Transaction ID": _text(
                    metadata.get("transaction_id")
                ),
                "BOM Ref": _text(
                    bom_item.get("bom_ref")
                ),
                "Sequence": _integer(
                    event.get("sequence_no")
                ),
                "Event ID": _text(
                    event.get("event_id")
                ),
                "Created At": format_datetime(
                    created_at
                ),
            }
        )

    return pd.DataFrame(
        rows,
        columns=EVENT_TABLE_COLUMNS,
    )


def filter_events_by_zerotag_id(
    events: Sequence[Mapping[str, Any]],
    zerotag_id: str,
) -> list[dict[str, Any]]:
    """Lọc Event theo ZeroTag ID trong metadata_json."""

    normalized_query = zerotag_id.strip().upper()

    if not normalized_query:
        return [
            dict(event)
            for event in events
        ]

    filtered: list[dict[str, Any]] = []

    for event in events:
        event_zerotag_id = get_event_zerotag_id(
            event
        )

        if event_zerotag_id is None:
            continue

        if normalized_query in event_zerotag_id.upper():
            filtered.append(
                dict(event)
            )

    return filtered


def build_passport_timeline(
    events: Sequence[Mapping[str, Any]],
    zerotag_id: str,
) -> pd.DataFrame:
    """Tạo timeline Event cho Digital Passport."""

    filtered_events = filter_events_by_zerotag_id(
        events,
        zerotag_id,
    )

    timeline = map_events_to_dataframe(
        filtered_events
    )

    if timeline.empty:
        return timeline

    return timeline.sort_values(
        by=[
            "Created At",
            "Sequence",
        ],
        ascending=True,
        kind="stable",
    ).reset_index(drop=True)


def build_overview_metrics(
    components: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
    *,
    today: date | None = None,
) -> dict[str, int]:
    """Tính metric cho Overview từ API response."""

    target_date = today or date.today()

    total_reels = len(components)

    in_stock = sum(
        1
        for component in components
        if component.get("status") == "IN_STOCK"
    )

    issued = sum(
        1
        for component in components
        if component.get("status") == "ISSUED"
    )

    wrong_bom_alerts = sum(
        1
        for event in events
        if event.get("event_type") == "BOM_MATCH_FAIL"
    )

    lot_datecode_warnings = sum(
        1
        for event in events
        if event.get("event_type")
        in {
            "LOT_MISMATCH",
            "DATECODE_MISMATCH",
        }
    )

    events_today = 0

    for event in events:
        created_at = _parse_datetime(
            event.get("created_at")
        )

        if created_at is None:
            continue

        if created_at.tzinfo is not None:
            created_at = created_at.astimezone()

        if created_at.date() == target_date:
            events_today += 1

    return {
        "total_reels": total_reels,
        "in_stock": in_stock,
        "issued": issued,
        "wrong_bom_alerts": wrong_bom_alerts,
        "lot_datecode_warnings": (
            lot_datecode_warnings
        ),
        "events_today": events_today,
    }


def map_scan_response(
    response: Mapping[str, Any],
) -> dict[str, Any]:
    """Chuẩn hóa ScanResponse để trang BOM Matching hiển thị."""

    component = _nested_mapping(
        response.get("component")
    )

    bom_check = _nested_mapping(
        response.get("bom_check")
    )

    gateway_action = _nested_mapping(
        response.get("gateway_action")
    )

    raw_violations = response.get("violations")

    violations = (
        [
            str(violation)
            for violation in raw_violations
        ]
        if isinstance(raw_violations, list)
        else []
    )

    allowed_date_code_from = _text(
        bom_check.get("allowed_date_code_from")
    )

    allowed_date_code_to = _text(
        bom_check.get("allowed_date_code_to")
    )

    return {
        "request_id": _text(
            response.get("request_id")
        ),
        "transaction_id": _text(
            response.get("transaction_id")
        ),
        "mode": _text(
            response.get("mode")
        ),
        "status": _text(
            response.get("status")
        ),
        "message": _text(
            response.get("message")
        ),
        "event_type": _text(
            response.get("event_type")
        ),
        "violations": violations,
        "replayed": bool(
            response.get("replayed", False)
        ),
        "processed_at": format_datetime(
            response.get("processed_at")
        ),
        "gateway": {
            "led": _text(
                gateway_action.get("led")
            ),
            "buzzer": _text(
                gateway_action.get("buzzer")
            ),
        },
        "scanned": {
            "zerotag_id": _text(
                component.get("zerotag_id")
            ),
            "part_number": _text(
                component.get("part_number")
            ),
            "lot_number": _text(
                component.get("lot_number")
            ),
            "date_code": _text(
                component.get("date_code")
            ),
            "quantity": _integer(
                component.get("quantity_current")
            ),
            "status_before": _text(
                component.get("status_before")
            ),
            "status_after": _text(
                component.get("status_after")
            ),
            "location": _text(
                component.get("location")
            ),
        },
        "expected": {
            "bom_code": _text(
                bom_check.get("bom_code")
            ),
            "bom_ref": _text(
                bom_check.get("bom_ref")
            ),
            "part_number": _text(
                bom_check.get(
                    "required_part_number"
                )
            ),
            "lot_number": _text(
                bom_check.get("required_lot")
            ),
            "date_code_from": (
                allowed_date_code_from
            ),
            "date_code_to": (
                allowed_date_code_to
            ),
            "date_code_range": (
                f"{allowed_date_code_from}"
                f" – {allowed_date_code_to}"
            ),
            "quantity": _integer(
                bom_check.get("required_quantity")
            ),
            "quantity_sufficient": bool(
                bom_check.get(
                    "quantity_sufficient",
                    False,
                )
            ),
        },
    }