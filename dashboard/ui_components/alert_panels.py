from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
from typing import Any, Literal

import streamlit as st

from dashboard.ui_components.status_badges import (
    get_status_label,
    get_status_tone,
    normalize_status,
    status_badge_html,
)


AlertTone = Literal[
    "neutral",
    "success",
    "warning",
    "danger",
    "info",
]


ALERT_TONES: set[str] = {
    "neutral",
    "success",
    "warning",
    "danger",
    "info",
}


SCAN_RESULT_TITLES: dict[str, str] = {
    "VALID": "Đối chiếu BOM hợp lệ",
    "WRONG_PART": "Sai mã linh kiện",
    "LOT_MISMATCH": (
        "Đúng mã linh kiện nhưng sai lot"
    ),
    "DATECODE_MISMATCH": (
        "Date-code không thuộc phạm vi cho phép"
    ),
    "UNKNOWN_TAG": "Không nhận diện được thẻ",
    "BLOCKED_TAG": "Thẻ đã bị khóa",
    "QR_RFID_MISMATCH": (
        "Mã QR và RFID không khớp"
    ),
    "TAMPER_WARNING": "Phát hiện dấu hiệu can thiệp",
}


SCAN_RESULT_MESSAGES: dict[str, str] = {
    "VALID": (
        "Cuộn linh kiện phù hợp với yêu cầu BOM "
        "và có thể tiếp tục quy trình cấp phát."
    ),
    "WRONG_PART": (
        "Mã linh kiện trên cuộn đã quét không khớp "
        "với mã linh kiện được yêu cầu trong BOM."
    ),
    "LOT_MISMATCH": (
        "Mã linh kiện phù hợp nhưng lot của cuộn "
        "không nằm trong lot được BOM cho phép."
    ),
    "DATECODE_MISMATCH": (
        "Date-code của cuộn linh kiện nằm ngoài "
        "phạm vi được BOM cho phép."
    ),
    "UNKNOWN_TAG": (
        "Không tìm thấy thẻ hoặc ZeroTag ID này "
        "trong hệ thống."
    ),
    "BLOCKED_TAG": (
        "Thẻ đã bị khóa và không được phép "
        "tiếp tục sử dụng."
    ),
    "QR_RFID_MISMATCH": (
        "Thông tin nhận dạng từ mã QR và RFID "
        "không trùng khớp."
    ),
    "TAMPER_WARNING": (
        "Hệ thống phát hiện dấu hiệu can thiệp "
        "hoặc thay đổi tính toàn vẹn của nhãn."
    ),
}


def normalize_alert_tone(
    tone: str | None,
) -> AlertTone:
    """Chuẩn hóa tone của Alert Panel."""

    if tone is None:
        return "neutral"

    normalized = tone.strip().lower()

    if normalized in ALERT_TONES:
        return normalized  # type: ignore[return-value]

    return "neutral"


def _display_value(
    value: Any,
) -> str:
    """Chuyển giá trị thành chuỗi hiển thị an toàn."""

    if value is None:
        return "—"

    if isinstance(value, bool):
        return "Có" if value else "Không"

    if isinstance(value, (list, tuple, set)):
        values = [
            _display_value(item)
            for item in value
        ]

        return ", ".join(values) if values else "—"

    cleaned = str(value).strip()

    return cleaned or "—"


def _normalize_details(
    details: (
        Mapping[str, Any]
        | Sequence[tuple[str, Any]]
        | None
    ),
) -> list[tuple[str, Any]]:
    """Chuẩn hóa dữ liệu chi tiết thành danh sách cặp."""

    if details is None:
        return []

    if isinstance(details, Mapping):
        return list(details.items())

    return list(details)

def alert_panel_html(
    title: str,
    message: str,
    *,
    tone: str = "info",
    details: (
        Mapping[str, Any]
        | Sequence[tuple[str, Any]]
        | None
    ) = None,
    status: Any | None = None,
    compact: bool = False,
) -> str:
    """Tạo HTML an toàn cho Alert Panel."""

    normalized_tone = normalize_alert_tone(
        tone,
    )

    safe_title = escape(
        title.strip() or "Thông báo",
    )

    safe_message = escape(
        message.strip() or "Không có nội dung.",
    )

    alert_classes = [
        "zt-alert",
        f"zt-alert--{normalized_tone}",
    ]

    if compact:
        alert_classes.append(
            "zt-alert--compact",
        )

    alert_class = " ".join(
        alert_classes,
    )

    status_html = ""

    if status is not None:
        status_html = (
            '<div class="zt-alert__status">'
            f"{status_badge_html(status)}"
            "</div>"
        )

    detail_items = _normalize_details(
        details,
    )

    details_html = ""

    if detail_items:
        detail_rows: list[str] = []

        for label, value in detail_items:
            safe_label = escape(
                str(label).strip() or "Thông tin",
            )

            safe_value = escape(
                _display_value(value),
            )

            detail_rows.append(
                '<div class="zt-alert__detail">'
                '<div class="zt-alert__detail-label">'
                f"{safe_label}"
                "</div>"
                '<div class="zt-alert__detail-value">'
                f"{safe_value}"
                "</div>"
                "</div>"
            )

        details_html = (
            '<div class="zt-alert__details">'
            '<div class="zt-alert__details-grid">'
            f"{''.join(detail_rows)}"
            "</div>"
            "</div>"
        )

    return (
        f'<section class="{alert_class}">'
        '<div class="zt-alert__header">'
        '<div class="zt-alert__heading">'
        '<div class="zt-alert__title">'
        f"{safe_title}"
        "</div>"
        '<div class="zt-alert__message">'
        f"{safe_message}"
        "</div>"
        "</div>"
        f"{status_html}"
        "</div>"
        f"{details_html}"
        "</section>"
    )

def render_alert_panel(
    title: str,
    message: str,
    *,
    tone: str = "info",
    details: (
        Mapping[str, Any]
        | Sequence[tuple[str, Any]]
        | None
    ) = None,
    status: Any | None = None,
    compact: bool = False,
) -> None:
    """Hiển thị Alert Panel trên Streamlit."""

    st.markdown(
        alert_panel_html(
            title,
            message,
            tone=tone,
            details=details,
            status=status,
            compact=compact,
        ),
        unsafe_allow_html=True,
    )

def build_scan_result_alert(
    scan_view: Mapping[str, Any],
) -> dict[str, Any]:
    """Tạo dữ liệu Alert Panel từ Scan Response đã map."""

    normalized_status = normalize_status(
        scan_view.get("status")
    )

    tone = get_status_tone(
        normalized_status
    )

    title = SCAN_RESULT_TITLES.get(
        normalized_status,
        "Kết quả kiểm tra",
    )

    raw_message = scan_view.get("message")

    if isinstance(raw_message, str):
        message = raw_message.strip()
    else:
        message = ""

    if not message:
        message = SCAN_RESULT_MESSAGES.get(
            normalized_status,
            "Backend đã trả về kết quả kiểm tra.",
        )

    scanned = scan_view.get("scanned")

    if not isinstance(scanned, Mapping):
        scanned = {}

    expected = scan_view.get("expected")

    if not isinstance(expected, Mapping):
        expected = {}

    gateway = scan_view.get("gateway")

    if not isinstance(gateway, Mapping):
        gateway = {}

    violations = scan_view.get("violations")

    translated_violations: list[str] = []

    if isinstance(violations, list):
        translated_violations = [
            get_status_label(violation)
            for violation in violations
        ]

    details: list[tuple[str, Any]] = [
        (
            "ZeroTag ID",
            scanned.get("zerotag_id"),
        ),
        (
            "Mã BOM",
            expected.get("bom_code"),
        ),
        (
            "Vị trí BOM",
            expected.get("bom_ref"),
        ),
        (
            "Mã linh kiện đã quét",
            scanned.get("part_number"),
        ),
        (
            "Mã linh kiện yêu cầu",
            expected.get("part_number"),
        ),
        (
            "Lot đã quét",
            scanned.get("lot_number"),
        ),
        (
            "Lot yêu cầu",
            expected.get("lot_number"),
        ),
        (
            "Đèn Gateway",
            gateway.get("led"),
        ),
        (
            "Còi Gateway",
            gateway.get("buzzer"),
        ),
    ]

    if translated_violations:
        details.append(
            (
                "Vi phạm",
                translated_violations,
            )
        )

    return {
        "title": title,
        "message": message,
        "tone": tone,
        "status": normalized_status,
        "details": details,
    }


def render_scan_result_alert(
    scan_view: Mapping[str, Any],
) -> None:
    """Hiển thị kết quả Scan theo dữ liệu Backend."""

    alert_data = build_scan_result_alert(
        scan_view
    )

    render_alert_panel(
        alert_data["title"],
        alert_data["message"],
        tone=alert_data["tone"],
        status=alert_data["status"],
        details=alert_data["details"],
    )


__all__ = [
    "AlertTone",
    "alert_panel_html",
    "build_scan_result_alert",
    "normalize_alert_tone",
    "render_alert_panel",
    "render_scan_result_alert",
]