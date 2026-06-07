from __future__ import annotations

from collections.abc import Mapping
from html import escape
from typing import Any

import streamlit as st

from dashboard.ui_components.status_badges import (
    status_badge_html,
)


def _display_text(
    value: Any,
    *,
    default: str = "—",
) -> str:
    """Chuẩn hóa giá trị văn bản để hiển thị."""

    if value is None:
        return default

    cleaned = str(value).strip()

    return cleaned or default


def _display_number(
    value: Any,
) -> str:
    """Định dạng số theo cách hiển thị tiếng Việt."""

    if isinstance(value, bool):
        return "—"

    try:
        number = int(value)
    except (TypeError, ValueError):
        return "—"

    return f"{number:,}".replace(",", ".")


def _quantity_percentage(
    current_quantity: Any,
    initial_quantity: Any,
) -> float:
    """Tính tỷ lệ số lượng còn lại trong khoảng 0 đến 100."""

    try:
        current = int(current_quantity)
        initial = int(initial_quantity)
    except (TypeError, ValueError):
        return 0.0

    if initial <= 0:
        return 0.0

    percentage = current / initial * 100

    return max(
        0.0,
        min(100.0, percentage),
    )


def _field_html(
    label: str,
    value: Any,
    *,
    monospace: bool = False,
) -> str:
    """Tạo một trường thông tin an toàn."""

    safe_label = escape(
        label.strip() or "Thông tin"
    )

    safe_value = escape(
        _display_text(value)
    )

    value_class = "zt-reel-preview__value"

    if monospace:
        value_class += (
            " zt-reel-preview__value--identifier"
        )

    return (
        '<div class="zt-reel-preview__field">'
        '<div class="zt-reel-preview__label">'
        f"{safe_label}"
        "</div>"
        f'<div class="{value_class}">'
        f"{safe_value}"
        "</div>"
        "</div>"
    )


def reel_preview_html(
    component: Mapping[str, Any],
    *,
    title: str | None = None,
    compact: bool = False,
) -> str:
    """Tạo HTML hồ sơ tóm tắt của một cuộn linh kiện."""

    zerotag_id = _display_text(
        component.get("zerotag_id")
    )

    component_name = _display_text(
        component.get("component_name"),
        default="Linh kiện chưa xác định",
    )

    status = component.get("status")

    tamper_status = component.get(
        "tamper_status"
    )

    current_quantity = component.get(
        "quantity_current"
    )

    initial_quantity = component.get(
        "quantity_initial"
    )

    percentage = _quantity_percentage(
        current_quantity,
        initial_quantity,
    )

    safe_title = escape(
        (
            title.strip()
            if title is not None
            else "Thông tin cuộn linh kiện"
        )
        or "Thông tin cuộn linh kiện"
    )

    safe_zerotag_id = escape(
        zerotag_id
    )

    safe_component_name = escape(
        component_name
    )

    current_display = escape(
        _display_number(current_quantity)
    )

    initial_display = escape(
        _display_number(initial_quantity)
    )

    quantity_text = (
        f"{current_display} / {initial_display}"
    )

    fields = [
        _field_html(
            "Mã linh kiện",
            component.get("part_number"),
            monospace=True,
        ),
        _field_html(
            "Lot",
            component.get("lot_number"),
            monospace=True,
        ),
        _field_html(
            "Date-code",
            component.get("date_code"),
            monospace=True,
        ),
        _field_html(
            "Vị trí",
            component.get("location"),
        ),
    ]

    if not compact:
        fields.extend(
            [
                _field_html(
                    "Nhà sản xuất",
                    component.get(
                        "manufacturer"
                    ),
                ),
                _field_html(
                    "Nhà cung cấp",
                    component.get(
                        "supplier"
                    ),
                ),
                _field_html(
                    "Loại nhãn",
                    component.get(
                        "label_type"
                    ),
                ),
                _field_html(
                    "Tag UID",
                    component.get("tag_uid"),
                    monospace=True,
                ),
            ]
        )

    tamper_badge = ""

    if tamper_status is not None:
        tamper_badge = (
            '<div class="zt-reel-preview__tamper">'
            f"{status_badge_html(tamper_status)}"
            "</div>"
        )

    compact_class = (
        " zt-reel-preview--compact"
        if compact
        else ""
    )

    return (
        '<section class="zt-reel-preview'
        f'{compact_class}">'
        '<div class="zt-reel-preview__header">'
        '<div class="zt-reel-preview__identity">'
        '<div class="zt-reel-preview__heading-label">'
        f"{safe_title}"
        "</div>"
        '<div class="zt-reel-preview__id">'
        f"{safe_zerotag_id}"
        "</div>"
        '<div class="zt-reel-preview__name">'
        f"{safe_component_name}"
        "</div>"
        "</div>"
        '<div class="zt-reel-preview__status">'
        f"{status_badge_html(status)}"
        f"{tamper_badge}"
        "</div>"
        "</div>"
        '<div class="zt-reel-preview__body">'
        '<div class="zt-reel-preview__visual-area">'
        '<div class="zt-reel-visual" '
        'aria-hidden="true">'
        '<div class="zt-reel-visual__ring">'
        '<div class="zt-reel-visual__hub">'
        '<div class="zt-reel-visual__hub-core">'
        "</div>"
        "</div>"
        "</div>"
        '<div class="zt-reel-visual__label">'
        f"{safe_zerotag_id}"
        "</div>"
        "</div>"
        "</div>"
        '<div class="zt-reel-preview__information">'
        '<div class="zt-reel-preview__grid">'
        f"{''.join(fields)}"
        "</div>"
        '<div class="zt-reel-preview__quantity">'
        '<div class="zt-reel-preview__quantity-header">'
        '<div>'
        '<div class="zt-reel-preview__label">'
        "Số lượng còn lại"
        "</div>"
        '<div class="zt-reel-preview__quantity-value">'
        f"{quantity_text}"
        '<span class="zt-reel-preview__quantity-unit">'
        " linh kiện"
        "</span>"
        "</div>"
        "</div>"
        '<div class="zt-reel-preview__quantity-percent">'
        f"{percentage:.0f}%"
        "</div>"
        "</div>"
        '<div class="zt-reel-preview__progress" '
        'role="progressbar" '
        'aria-valuemin="0" '
        'aria-valuemax="100" '
        f'aria-valuenow="{percentage:.0f}">'
        '<div class="zt-reel-preview__progress-value" '
        f'style="width: {percentage:.2f}%;">'
        "</div>"
        "</div>"
        "</div>"
        "</div>"
        "</div>"
        "</section>"
    )


def render_reel_preview(
    component: Mapping[str, Any],
    *,
    title: str | None = None,
    compact: bool = False,
) -> None:
    """Hiển thị hồ sơ tóm tắt của một cuộn linh kiện."""

    st.markdown(
        reel_preview_html(
            component,
            title=title,
            compact=compact,
        ),
        unsafe_allow_html=True,
    )


__all__ = [
    "reel_preview_html",
    "render_reel_preview",
]