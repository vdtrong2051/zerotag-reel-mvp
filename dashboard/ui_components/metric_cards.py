from __future__ import annotations

from html import escape
from typing import Any, Literal

import streamlit as st


MetricTone = Literal[
    "neutral",
    "success",
    "warning",
    "danger",
    "info",
]


TONE_MAP: dict[str, MetricTone] = {
    "neutral": "neutral",
    "success": "success",
    "warning": "warning",
    "danger": "danger",
    "info": "info",
}


# SVG nội bộ của Metric Card.
# Chỉ nhận khóa icon đã định nghĩa, không đưa HTML bên ngoài vào trang.
METRIC_ICON_SVG: dict[str, str] = {
    "reel": (
        '<circle cx="12" cy="12" r="8"/>'
        '<circle cx="12" cy="12" r="2.5"/>'
        '<path d="M12 4v5"/>'
        '<path d="M12 15v5"/>'
        '<path d="M4 12h5"/>'
        '<path d="M15 12h5"/>'
    ),
    "inventory": (
        '<path d="m4 7 8-4 8 4-8 4-8-4Z"/>'
        '<path d="M4 7v10l8 4 8-4V7"/>'
        '<path d="M12 11v10"/>'
    ),
    "issued": (
        '<path d="M14 5h5v5"/>'
        '<path d="m19 5-8 8"/>'
        '<path d="M19 13v5a2 2 0 0 1-2 2H6'
        'a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5"/>'
    ),
    "bom_alert": (
        '<path d="M10.3 4.4 2.6 18a2 2 0 0 0 '
        '1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 '
        '4.4a2 2 0 0 0-3.4 0Z"/>'
        '<path d="M12 9v4"/>'
        '<path d="M12 17h.01"/>'
    ),
    "calendar_warning": (
        '<rect x="3" y="5" width="18" height="16" rx="2"/>'
        '<path d="M16 3v4"/>'
        '<path d="M8 3v4"/>'
        '<path d="M3 10h18"/>'
        '<path d="M12 14v3"/>'
        '<path d="M12 19h.01"/>'
    ),
    "analytics": (
        '<path d="M4 19V11"/>'
        '<path d="M10 19V6"/>'
        '<path d="M16 19v-8"/>'
        '<path d="M21 19V8"/>'
        '<path d="M3 19h19"/>'
    ),
    "activity": (
        '<path d="M3 12h4l2-6 4 12 2-6h6"/>'
    ),
}


def normalize_metric_tone(
    tone: str | None,
) -> MetricTone:
    """Chuẩn hóa tone màu của Metric Card."""

    if tone is None:
        return "neutral"

    normalized_tone = tone.strip().lower()

    return TONE_MAP.get(
        normalized_tone,
        "neutral",
    )


def format_metric_value(
    value: Any,
) -> str:
    """Định dạng giá trị Metric theo quy ước tiếng Việt."""

    if value is None:
        return "—"

    if isinstance(value, bool):
        return "Có" if value else "Không"

    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")

    if isinstance(value, float):
        if value.is_integer():
            integer_value = int(value)

            return f"{integer_value:,}".replace(
                ",",
                ".",
            )

        formatted_value = f"{value:,.1f}"

        return (
            formatted_value
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )

    cleaned_value = str(value).strip()

    return cleaned_value or "—"


def metric_icon_html(
    icon: str | None,
) -> str:
    """Tạo HTML SVG cho icon Metric Card."""

    if icon is None:
        return ""

    icon_key = icon.strip().lower()

    if not icon_key:
        return ""

    # Khóa không tồn tại dùng icon hoạt động chung.
    # Tuyệt đối không in lại icon_key dưới dạng chữ.
    svg_content = METRIC_ICON_SVG.get(
        icon_key,
        METRIC_ICON_SVG["activity"],
    )

    return (
        '<span class="zt-metric-card__icon" '
        'aria-hidden="true">'
        '<svg class="zt-metric-card__icon-svg" '
        'xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 24 24" '
        'fill="none" '
        'stroke="currentColor" '
        'stroke-width="1.8" '
        'stroke-linecap="round" '
        'stroke-linejoin="round" '
        'focusable="false">'
        f"{svg_content}"
        "</svg>"
        "</span>"
    )


def metric_card_html(
    label: str,
    value: Any,
    *,
    tone: str = "neutral",
    caption: str | None = None,
    icon: str | None = None,
    unit: str | None = None,
) -> str:
    """Tạo HTML an toàn cho một Metric Card."""

    normalized_tone = normalize_metric_tone(
        tone,
    )

    cleaned_label = label.strip() or "Chỉ số"

    display_value = format_metric_value(
        value,
    )

    safe_label = escape(
        cleaned_label,
    )

    safe_value = escape(
        display_value,
    )

    icon_html = metric_icon_html(
        icon,
    )

    unit_html = ""

    if unit is not None:
        cleaned_unit = unit.strip()

        if cleaned_unit:
            safe_unit = escape(
                cleaned_unit,
            )

            unit_html = (
                '<span class="zt-metric-card__unit">'
                f"{safe_unit}"
                "</span>"
            )

    caption_html = ""

    if caption is not None:
        cleaned_caption = caption.strip()

        if cleaned_caption:
            safe_caption = escape(
                cleaned_caption,
            )

            caption_html = (
                '<div class="zt-metric-card__caption">'
                f"{safe_caption}"
                "</div>"
            )

    return (
        '<div class="zt-metric-card '
        f'zt-metric-card--{normalized_tone}">'
        '<div class="zt-metric-card__top">'
        '<div class="zt-metric-card__label-group">'
        f"{icon_html}"
        '<div class="zt-metric-card__label">'
        f"{safe_label}"
        "</div>"
        "</div>"
        "</div>"
        '<div class="zt-metric-card__value-line">'
        '<div class="zt-metric-card__value">'
        f"{safe_value}"
        "</div>"
        f"{unit_html}"
        "</div>"
        f"{caption_html}"
        "</div>"
    )


def render_metric_card(
    label: str,
    value: Any,
    *,
    tone: str = "neutral",
    caption: str | None = None,
    icon: str | None = None,
    unit: str | None = None,
) -> None:
    """Render Metric Card trong Streamlit."""

    card_html = metric_card_html(
        label,
        value,
        tone=tone,
        caption=caption,
        icon=icon,
        unit=unit,
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )


__all__ = [
    "MetricTone",
    "format_metric_value",
    "metric_card_html",
    "metric_icon_html",
    "normalize_metric_tone",
    "render_metric_card",
]