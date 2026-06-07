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


def normalize_metric_tone(
    tone: str | None,
) -> MetricTone:
    """Chuẩn hóa tone màu của Metric Card."""

    if tone is None:
        return "neutral"

    normalized = tone.strip().lower()

    return TONE_MAP.get(
        normalized,
        "neutral",
    )


def format_metric_value(
    value: Any,
) -> str:
    """Định dạng giá trị Metric theo cách hiển thị tiếng Việt."""

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

        formatted = f"{value:,.1f}"

        return (
            formatted
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )

    cleaned = str(value).strip()

    return cleaned or "—"


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
        tone
    )

    cleaned_label = label.strip() or "Chỉ số"

    display_value = format_metric_value(
        value
    )

    safe_label = escape(cleaned_label)
    safe_value = escape(display_value)

    icon_html = ""

    if icon is not None:
        cleaned_icon = icon.strip()

        if cleaned_icon:
            safe_icon = escape(cleaned_icon)

            icon_html = (
                '<span class="zt-metric-card__icon" '
                'aria-hidden="true">'
                f"{safe_icon}"
                "</span>"
            )

    unit_html = ""

    if unit is not None:
        cleaned_unit = unit.strip()

        if cleaned_unit:
            safe_unit = escape(cleaned_unit)

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
                cleaned_caption
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
    """Hiển thị một Metric Card trên Streamlit."""

    st.markdown(
        metric_card_html(
            label,
            value,
            tone=tone,
            caption=caption,
            icon=icon,
            unit=unit,
        ),
        unsafe_allow_html=True,
    )


__all__ = [
    "MetricTone",
    "format_metric_value",
    "metric_card_html",
    "normalize_metric_tone",
    "render_metric_card",
]