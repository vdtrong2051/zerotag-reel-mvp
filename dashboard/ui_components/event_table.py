from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from dashboard.ui_components.status_badges import (
    get_status_label,
    get_status_tone,
    normalize_status,
    status_badge_html,
)


REQUIRED_COLUMNS = [
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


def _display_text(
    value: Any,
    *,
    default: str = "—",
) -> str:
    """Chuẩn hóa một giá trị dùng trong bảng."""

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    cleaned = str(value).strip()

    return cleaned or default


def _safe_text(
    value: Any,
    *,
    default: str = "—",
) -> str:
    """Chuẩn hóa và escape HTML."""

    return escape(
        _display_text(
            value,
            default=default,
        )
    )


def _normalize_height(
    height: int | None,
) -> int | None:
    """Chuẩn hóa chiều cao vùng cuộn."""

    if height is None:
        return None

    if isinstance(height, bool):
        return None

    try:
        normalized = int(height)
    except (TypeError, ValueError):
        return None

    if normalized < 160:
        return 160

    return min(normalized, 900)


def _prepare_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Bổ sung các cột còn thiếu mà không sửa DataFrame gốc."""

    prepared = dataframe.copy()

    for column in REQUIRED_COLUMNS:
        if column not in prepared.columns:
            prepared[column] = None

    return prepared


def _event_type_html(
    event_type: Any,
) -> str:
    """Tạo ô loại sự kiện gồm nhãn Việt và mã kỹ thuật."""

    normalized = normalize_status(
        event_type
    )

    label = get_status_label(
        normalized
    )

    safe_label = escape(label)
    safe_code = escape(normalized)

    return (
        '<div class="zt-event-table__event">'
        '<div class="zt-event-table__event-name">'
        f"{safe_label}"
        "</div>"
        '<div class="zt-event-table__event-code">'
        f"{safe_code}"
        "</div>"
        "</div>"
    )


def _time_html(
    row: pd.Series,
) -> str:
    """Tạo ô thời gian và giữ timestamp đầy đủ trong tooltip."""

    short_time = _safe_text(
        row.get("Time")
    )

    created_at = _safe_text(
        row.get("Created At")
    )

    return (
        '<span class="zt-event-table__time" '
        f'title="{created_at}">'
        f"{short_time}"
        "</span>"
    )


def _sequence_html(
    value: Any,
) -> str:
    """Hiển thị thứ tự event."""

    display_value = _display_text(value)

    try:
        number = int(display_value)
    except (TypeError, ValueError):
        safe_value = escape(display_value)
    else:
        safe_value = str(number)

    return (
        '<span class="zt-event-table__sequence">'
        f"{safe_value}"
        "</span>"
    )


def _row_html(
    row: pd.Series,
    *,
    show_transaction: bool,
) -> str:
    """Tạo một dòng Event Table."""

    result = row.get("Result")
    tone = get_status_tone(result)

    zerotag_id = _safe_text(
        row.get("ZeroTag ID")
    )

    message = _safe_text(
        row.get("Message")
    )

    location = _safe_text(
        row.get("Location")
    )

    transaction_id = _safe_text(
        row.get("Transaction ID")
    )

    bom_ref = _safe_text(
        row.get("BOM Ref")
    )

    cells = [
        (
            '<td class="zt-event-table__cell-time">'
            f"{_time_html(row)}"
            "</td>"
        ),
        (
            '<td class="zt-table-identifier">'
            f"{zerotag_id}"
            "</td>"
        ),
        (
            "<td>"
            f"{_event_type_html(row.get('Event Type'))}"
            "</td>"
        ),
        (
            '<td class="zt-event-table__result">'
            f"{status_badge_html(result)}"
            "</td>"
        ),
        (
            '<td class="zt-event-table__message">'
            f"{message}"
            "</td>"
        ),
        (
            '<td class="zt-event-table__location">'
            f"{location}"
            "</td>"
        ),
    ]

    if show_transaction:
        cells.append(
            (
                '<td class="zt-table-identifier">'
                f"{transaction_id}"
                "</td>"
            )
        )

    cells.extend(
        [
            (
                '<td class="zt-event-table__bom-ref">'
                f"{bom_ref}"
                "</td>"
            ),
            (
                '<td class="zt-event-table__sequence-cell">'
                f"{_sequence_html(row.get('Sequence'))}"
                "</td>"
            ),
        ]
    )

    return (
        '<tr class="zt-event-row '
        f'zt-event-row--{tone}">'
        f"{''.join(cells)}"
        "</tr>"
    )


def _header_html(
    *,
    show_transaction: bool,
) -> str:
    """Tạo header tiếng Việt của Event Table."""

    headers = [
        "Thời gian",
        "ZeroTag ID",
        "Loại sự kiện",
        "Kết quả",
        "Nội dung",
        "Vị trí",
    ]

    if show_transaction:
        headers.append("Mã giao dịch")

    headers.extend(
        [
            "Vị trí BOM",
            "Thứ tự",
        ]
    )

    cells = [
        f"<th>{escape(header)}</th>"
        for header in headers
    ]

    return (
        "<thead>"
        "<tr>"
        f"{''.join(cells)}"
        "</tr>"
        "</thead>"
    )


def empty_event_table_html(
    *,
    title: str = "Chưa có sự kiện",
    message: str = (
        "Không tìm thấy sự kiện phù hợp "
        "với điều kiện hiện tại."
    ),
) -> str:
    """Tạo trạng thái rỗng của Event Table."""

    safe_title = escape(
        title.strip() or "Chưa có sự kiện"
    )

    safe_message = escape(
        message.strip()
        or "Không có dữ liệu để hiển thị."
    )

    return (
        '<div class="zt-empty-state">'
        '<div class="zt-empty-state__title">'
        f"{safe_title}"
        "</div>"
        '<div class="zt-empty-state__message">'
        f"{safe_message}"
        "</div>"
        "</div>"
    )


def event_table_html(
    dataframe: pd.DataFrame,
    *,
    title: str | None = None,
    height: int | None = None,
    show_transaction: bool = True,
) -> str:
    """Tạo HTML cho bảng nhật ký sự kiện."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

    prepared = _prepare_dataframe(
        dataframe
    )

    if prepared.empty:
        return empty_event_table_html()

    normalized_height = _normalize_height(
        height
    )

    scroll_style = ""

    if normalized_height is not None:
        scroll_style = (
            f' style="max-height: {normalized_height}px;"'
        )

    toolbar_html = ""

    if title is not None:
        cleaned_title = title.strip()

        if cleaned_title:
            safe_title = escape(cleaned_title)

            toolbar_html = (
                '<div class="zt-event-table-toolbar">'
                '<div class="zt-event-table-toolbar__title">'
                f"{safe_title}"
                "</div>"
                '<div class="zt-event-table-toolbar__count">'
                f"{len(prepared)} sự kiện"
                "</div>"
                "</div>"
            )

    rows = [
        _row_html(
            row,
            show_transaction=show_transaction,
        )
        for _, row in prepared.iterrows()
    ]

    return (
        '<section class="zt-event-table-wrapper">'
        f"{toolbar_html}"
        '<div class="zt-event-table__scroll"'
        f"{scroll_style}>"
        '<table class="zt-event-table">'
        f"{_header_html(show_transaction=show_transaction)}"
        "<tbody>"
        f"{''.join(rows)}"
        "</tbody>"
        "</table>"
        "</div>"
        "</section>"
    )


def render_event_table(
    dataframe: pd.DataFrame,
    *,
    title: str | None = None,
    height: int | None = None,
    show_transaction: bool = True,
) -> None:
    """Hiển thị bảng nhật ký sự kiện trên Streamlit."""

    st.markdown(
        event_table_html(
            dataframe,
            title=title,
            height=height,
            show_transaction=show_transaction,
        ),
        unsafe_allow_html=True,
    )


__all__ = [
    "empty_event_table_html",
    "event_table_html",
    "render_event_table",
]