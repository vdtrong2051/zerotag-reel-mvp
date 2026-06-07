from __future__ import annotations

from enum import Enum
from html import escape
from typing import Any, Literal

import streamlit as st


StatusTone = Literal[
    "success",
    "warning",
    "danger",
    "info",
    "neutral",
]


STATUS_LABELS: dict[str, str] = {
    # Scan results
    "VALID": "Hợp lệ",
    "WRONG_PART": "Sai mã linh kiện",
    "LOT_MISMATCH": "Sai lot",
    "DATECODE_MISMATCH": "Sai date-code",
    "UNKNOWN_TAG": "Không nhận diện được thẻ",
    "BLOCKED_TAG": "Thẻ đã bị khóa",
    "QR_RFID_MISMATCH": "QR và RFID không khớp",
    "TAMPER_WARNING": "Cảnh báo can thiệp",

    # Component status
    "REGISTERED": "Đã đăng ký",
    "IN_STOCK": "Trong kho",
    "ISSUED": "Đã cấp phát",
    "BLOCKED": "Đã khóa",
    "SCRAPPED": "Đã loại bỏ",

    # BOM status
    "ACTIVE": "Đang hoạt động",
    "INACTIVE": "Không hoạt động",

    # Event results
    "OK": "Bình thường",
    "WARNING": "Cảnh báo",
    "FAIL": "Thất bại",

    # Event types
    "REEL_SCANNED": "Đã quét cuộn linh kiện",
    "WAREHOUSE_IN": "Nhập kho",
    "BOM_CHECK_STARTED": "Bắt đầu đối chiếu BOM",
    "BOM_MATCH_OK": "Đối chiếu BOM thành công",
    "BOM_MATCH_FAIL": "Đối chiếu BOM thất bại",
    "WARNING_ISSUED": "Đã phát cảnh báo",
    "RETURN_TO_STOCK": "Đã trả về kho",
    "COMPONENT_ISSUED": "Đã cấp phát linh kiện",
    "VERIFICATION_PASSED": "Xác minh thành công",
    "VERIFICATION_FAILED": "Xác minh thất bại",
    "TAG_BLOCKED": "Đã khóa thẻ",

    # Gateway
    "ONLINE": "Trực tuyến",
    "OFFLINE": "Ngoại tuyến",
    "DISABLED": "Đã vô hiệu hóa",
    "SIMULATOR": "Bộ mô phỏng",
    "ESP32_NFC": "Gateway ESP32 NFC",
    "ESP32_RFID": "Gateway ESP32 RFID",
    "ESP32_UHF": "Gateway ESP32 UHF",

    # Label and tamper
    "STANDARD": "Tiêu chuẩn",
    "ANTI_TAMPER": "Chống can thiệp",
    "NORMAL": "Bình thường",

    # MSL
    "NEED_BAKE": "Cần sấy",
}


SUCCESS_STATUSES = {
    "VALID",
    "IN_STOCK",
    "ONLINE",
    "OK",
    "NORMAL",
    "ACTIVE",
    "BOM_MATCH_OK",
    "VERIFICATION_PASSED",
}

WARNING_STATUSES = {
    "LOT_MISMATCH",
    "DATECODE_MISMATCH",
    "WARNING",
    "WARNING_ISSUED",
    "NEED_BAKE",
    "TAMPER_WARNING",
}

DANGER_STATUSES = {
    "WRONG_PART",
    "UNKNOWN_TAG",
    "BLOCKED_TAG",
    "QR_RFID_MISMATCH",
    "BLOCKED",
    "SCRAPPED",
    "FAIL",
    "BOM_MATCH_FAIL",
    "VERIFICATION_FAILED",
    "TAG_BLOCKED",
}

INFO_STATUSES = {
    "REGISTERED",
    "ISSUED",
    "REEL_SCANNED",
    "WAREHOUSE_IN",
    "BOM_CHECK_STARTED",
    "RETURN_TO_STOCK",
    "COMPONENT_ISSUED",
    "SIMULATOR",
    "ESP32_NFC",
    "ESP32_RFID",
    "ESP32_UHF",
}


def normalize_status(
    status: Any,
) -> str:
    """Chuẩn hóa status, enum hoặc chuỗi về dạng mã viết hoa."""

    if status is None:
        return "UNKNOWN"

    if isinstance(status, Enum):
        raw_value = status.value
    else:
        raw_value = status

    normalized = str(raw_value).strip().upper()

    return normalized or "UNKNOWN"


def get_status_tone(
    status: Any,
) -> StatusTone:
    """Xác định tone màu tương ứng với một trạng thái."""

    normalized = normalize_status(status)

    if normalized in SUCCESS_STATUSES:
        return "success"

    if normalized in WARNING_STATUSES:
        return "warning"

    if normalized in DANGER_STATUSES:
        return "danger"

    if normalized in INFO_STATUSES:
        return "info"

    return "neutral"


def get_status_label(
    status: Any,
    *,
    label: str | None = None,
) -> str:
    """Lấy nhãn tiếng Việt để hiển thị trên giao diện."""

    if label is not None:
        cleaned_label = label.strip()

        if cleaned_label:
            return cleaned_label

    normalized = normalize_status(status)

    translated_label = STATUS_LABELS.get(
        normalized
    )

    if translated_label is not None:
        return translated_label

    return normalized.replace("_", " ").title()


def status_badge_html(
    status: Any,
    *,
    label: str | None = None,
) -> str:
    """Tạo HTML badge an toàn từ trạng thái."""

    tone = get_status_tone(status)

    display_label = get_status_label(
        status,
        label=label,
    )

    safe_label = escape(display_label)

    return (
        '<span class="zt-status-badge '
        f'zt-status-badge--{tone}">'
        f"{safe_label}"
        "</span>"
    )


def render_status_badge(
    status: Any,
    *,
    label: str | None = None,
) -> None:
    """Render status badge bằng Streamlit."""

    st.markdown(
        status_badge_html(
            status,
            label=label,
        ),
        unsafe_allow_html=True,
    )


__all__ = [
    "StatusTone",
    "get_status_label",
    "get_status_tone",
    "normalize_status",
    "render_status_badge",
    "status_badge_html",
]