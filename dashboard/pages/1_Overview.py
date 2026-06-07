from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from dashboard.api_client import (
    BackendClient,
    BackendClientError,
    build_overview_metrics,
)
from dashboard.ui_components import (
    render_metric_card,
)
from dashboard.ui_components.alert_panels import (
    render_alert_panel,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

STYLE_PATH = (
    PROJECT_ROOT
    / "dashboard"
    / "assets"
    / "styles"
    / "main.css"
)

BACKEND_CLIENT = BackendClient.from_env()


def load_dashboard_styles() -> None:
    """Nạp Design System chung của Dashboard."""

    if not STYLE_PATH.exists():
        st.error(
            "Không tìm thấy file giao diện "
            "dashboard/assets/styles/main.css."
        )
        return

    css_content = STYLE_PATH.read_text(
        encoding="utf-8",
    )

    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True,
    )


def render_page_header() -> None:
    """Hiển thị tiêu đề và mô tả trang Tổng quan."""

    header_html = (
        '<div class="zt-page-header__content">'
        '<div class="zt-page-header__eyebrow">'
        "ZEROTAG REEL MVP"
        "</div>"
        '<h1 class="zt-page-header__title">'
        "Tổng quan hệ thống"
        "</h1>"
        '<div class="zt-page-header__description">'
        "Theo dõi trạng thái cuộn linh kiện, cảnh báo BOM "
        "và hoạt động truy xuất trong môi trường SMT/EMS."
        "</div>"
        "</div>"
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )


def render_section_title(
    title: str,
    description: str,
) -> None:
    """Hiển thị tiêu đề của một khu vực trên trang."""

    safe_title = escape(title)
    safe_description = escape(description)

    section_html = (
        '<div class="zt-section-header">'
        "<div>"
        '<h2 class="zt-section-title">'
        f"{safe_title}"
        "</h2>"
        '<div class="zt-card-text">'
        f"{safe_description}"
        "</div>"
        "</div>"
        "</div>"
    )

    st.markdown(
        section_html,
        unsafe_allow_html=True,
    )


def render_placeholder_panel(
    title: str,
    message: str,
) -> None:
    """Hiển thị panel tạm trong giai đoạn dựng khung trang."""

    safe_title = escape(title)
    safe_message = escape(message)

    panel_html = (
        '<section class="zt-panel">'
        '<div class="zt-panel__header">'
        '<div class="zt-panel__title">'
        f"{safe_title}"
        "</div>"
        "</div>"
        '<div class="zt-empty-state">'
        '<div class="zt-empty-state__title">'
        "Chưa tải dữ liệu"
        "</div>"
        '<div class="zt-empty-state__message">'
        f"{safe_message}"
        "</div>"
        "</div>"
        "</section>"
    )

    st.markdown(
        panel_html,
        unsafe_allow_html=True,
    )

def fetch_overview_events(
    client: BackendClient,
    *,
    max_records: int = 500,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """Tải Event theo từng trang do Backend giới hạn 100 bản ghi."""

    events: list[dict[str, Any]] = []
    offset = 0

    while len(events) < max_records:
        remaining = max_records - len(events)

        current_limit = min(
            page_size,
            remaining,
        )

        event_page = client.get_events(
            offset=offset,
            limit=current_limit,
        )

        events.extend(event_page)

        if len(event_page) < current_limit:
            break

        offset += len(event_page)

    return events

@st.cache_data(
    ttl=10,
    show_spinner=False,
)
def load_overview_data(
    base_url: str,
    api_prefix: str,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    str | None,
    str | None,
]:
    """Tải Component và Event độc lập từ Backend."""

    client = BackendClient(
        base_url=base_url,
        api_prefix=api_prefix,
    )

    components: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    components_error: str | None = None
    events_error: str | None = None

    try:
        components = client.get_components(
            limit=100,
        )
    except BackendClientError as error:
        components_error = str(error)

    try:
        events = fetch_overview_events(
            client,
            max_records=500,
            page_size=100,
        )
    except BackendClientError as error:
        events_error = str(error)

    return (
        components,
        events,
        components_error,
        events_error,
    )


def get_data_status(
    components_error: str | None,
    events_error: str | None,
) -> str:
    """Xác định trạng thái tải dữ liệu tổng thể."""

    if (
        components_error is None
        and events_error is None
    ):
        return "ready"

    if (
        components_error is not None
        and events_error is not None
    ):
        return "offline"

    return "partial"

def render_data_status_panel(
    data_status: str,
) -> None:
    """Hiển thị trạng thái dữ liệu bằng Alert Panel ZeroTag."""

    status_config: dict[str, tuple[str, str, str]] = {
        "ready": (
            "Dữ liệu đã sẵn sàng",
            "Backend và các API cần thiết đang phản hồi.",
            "success",
        ),
        "partial": (
            "Dữ liệu chưa đầy đủ",
            (
                "Một phần API chưa phản hồi. "
                "Dashboard vẫn hiển thị dữ liệu khả dụng."
            ),
            "warning",
        ),
        "offline": (
            "Backend không khả dụng",
            "Không thể tải dữ liệu vận hành từ Backend.",
            "danger",
        ),
    }

    title, message, tone = status_config.get(
        data_status,
        (
            "Chưa xác định trạng thái",
            "Không thể xác định trạng thái dữ liệu.",
            "neutral",
        ),
    )

    render_alert_panel(
        title,
        message,
        tone=tone,
        compact=True,
    )

def build_overview_metric_items(
    components: list[dict[str, Any]],
    events: list[dict[str, Any]],
    *,
    components_error: str | None,
    events_error: str | None,
) -> list[dict[str, Any]]:
    """Tạo cấu hình sáu Metric Card của trang Tổng quan."""

    metrics = build_overview_metrics(
        components,
        events,
    )

    components_available = (
        components_error is None
    )

    events_available = (
        events_error is None
    )

    component_caption = (
        "Tất cả cuộn đã đăng ký"
        if components_available
        else "Component API không khả dụng"
    )

    stock_caption = (
        "Sẵn sàng cấp phát"
        if components_available
        else "Component API không khả dụng"
    )

    issued_caption = (
        "Đang sử dụng tại dây chuyền"
        if components_available
        else "Component API không khả dụng"
    )

    wrong_bom_caption = (
        "Cần kiểm tra ngay"
        if events_available
        else "Event API không khả dụng"
    )

    warning_caption = (
        "Cần xác nhận thủ công"
        if events_available
        else "Event API không khả dụng"
    )

    today_caption = (
        "Đã ghi vào nhật ký"
        if events_available
        else "Event API không khả dụng"
    )

    return [
        {
            "label": "Tổng số cuộn",
            "value": (
                metrics["total_reels"]
                if components_available
                else None
            ),
            "tone": "info",
            "icon": "reel",
            "caption": component_caption,
            "unit": "cuộn",
        },
        {
            "label": "Trong kho",
            "value": (
                metrics["in_stock"]
                if components_available
                else None
            ),
            "tone": "success",
            "icon": "inventory",
            "caption": stock_caption,
            "unit": "cuộn",
        },
        {
            "label": "Đã cấp phát",
            "value": (
                metrics["issued"]
                if components_available
                else None
            ),
            "tone": "info",
            "icon": "issued",
            "caption": issued_caption,
            "unit": "cuộn",
        },
        {
            "label": "Cảnh báo sai BOM",
            "value": (
                metrics["wrong_bom_alerts"]
                if events_available
                else None
            ),
            "tone": "danger",
            "icon": "bom_alert",
            "caption": wrong_bom_caption,
            "unit": "cảnh báo",
        },
        {
            "label": "Cảnh báo lot / date-code",
            "value": (
                metrics["lot_datecode_warnings"]
                if events_available
                else None
            ),
            "tone": "warning",
            "icon": "calendar_warning",
            "caption": warning_caption,
            "unit": "cảnh báo",
        },
        {
            "label": "Sự kiện hôm nay",
            "value": (
                metrics["events_today"]
                if events_available
                else None
            ),
            "tone": "neutral",
            "icon": "analytics",
            "caption": today_caption,
            "unit": "sự kiện",
        },
    ]

load_dashboard_styles()

with st.spinner("Đang tải dữ liệu vận hành..."):
    (
        components,
        events,
        components_error,
        events_error,
    ) = load_overview_data(
        BACKEND_CLIENT.base_url,
        BACKEND_CLIENT.api_prefix,
    )

data_status = get_data_status(
    components_error,
    events_error,
)

metric_items = build_overview_metric_items(
    components,
    events,
    components_error=components_error,
    events_error=events_error,
)

header_content, header_action = st.columns(
    [4.2, 1.3],
    vertical_alignment="center",
)

with header_content:
    render_page_header()

with header_action:
    st.caption("Trạng thái dữ liệu")

    render_data_status_panel(
        data_status,
    )

    st.caption(
        f"{len(components)} cuộn · "
        f"{len(events)} sự kiện"
    )

    if st.button(
        "Làm mới dữ liệu",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

st.divider()

if components_error:
    render_alert_panel(
        "Không thể tải dữ liệu cuộn linh kiện",
        str(components_error),
        tone="warning",
        compact=True,
    )

if events_error:
    render_alert_panel(
        "Không thể tải nhật ký sự kiện",
        str(events_error),
        tone="warning",
        compact=True,
    )

render_section_title(
    "Chỉ số vận hành",
    "Các chỉ số tổng hợp về cuộn linh kiện và cảnh báo.",
)

with st.container(
    key="zt_overview_metrics",
):
    metric_columns = st.columns(
        6,
        gap="small",
    )

    for column, metric in zip(
        metric_columns,
        metric_items,
        strict=True,
    ):
        with column:
            render_metric_card(
                metric["label"],
                metric["value"],
                tone=metric["tone"],
                icon=metric["icon"],
                caption=metric["caption"],
                unit=metric["unit"],
            )

st.write("")

with st.container(
    key="zt_overview_insights",
):
    analysis_columns = st.columns(
        [1.05, 1.35, 0.90],
        gap="medium",
    )

    with analysis_columns[0]:
        if events_error is not None:
            activity_message = (
                "Chưa thể tải hoạt động gần đây "
                "do Event API không khả dụng."
            )
        elif events:
            activity_message = (
                f"Đã tải {len(events)} sự kiện. "
                "Sáu sự kiện mới nhất sẽ được hiển thị "
                "tại Bước 7.5."
            )
        else:
            activity_message = (
                "Backend hoạt động nhưng chưa có sự kiện."
            )

        render_placeholder_panel(
            "Hoạt động gần đây",
            activity_message,
        )

    with analysis_columns[1]:
        if events_error is not None:
            chart_message = (
                "Chưa thể tổng hợp biểu đồ "
                "do Event API không khả dụng."
            )
        elif events:
            chart_message = (
                f"Đã nhận {len(events)} sự kiện. "
                "Biểu đồ bảy ngày sẽ được dựng "
                "tại Bước 7.6."
            )
        else:
            chart_message = (
                "Chưa có sự kiện. Biểu đồ sẽ hiển thị "
                "giá trị 0 cho toàn bộ bảy ngày."
            )

        render_placeholder_panel(
            "Sự kiện trong 7 ngày",
            chart_message,
        )

    with analysis_columns[2]:
        if events_error is not None:
            health_message = (
                "Chưa thể tổng hợp kết quả xử lý "
                "do Event API không khả dụng."
            )
        elif events:
            health_message = (
                "Dữ liệu sự kiện đã sẵn sàng để tổng hợp "
                "Bình thường, Cảnh báo và Thất bại."
            )
        else:
            health_message = (
                "Chưa có kết quả sự kiện để tổng hợp."
            )

        render_placeholder_panel(
            "Tình trạng xử lý",
            health_message,
        )

st.write("")

render_section_title(
    "Cuộn linh kiện cập nhật gần đây",
    "Danh sách các cuộn có thời gian cập nhật mới nhất.",
)

if components_error is not None:
    reel_message = (
        "Chưa thể tải danh sách cuộn linh kiện "
        "do Component API không khả dụng."
    )
elif components:
    reel_message = (
        f"Đã tải {len(components)} cuộn linh kiện. "
        "Các cuộn cập nhật gần đây sẽ được hiển thị "
        "tại Bước 7.8."
    )
else:
    reel_message = (
        "Backend hoạt động nhưng chưa có cuộn linh kiện."
    )


render_placeholder_panel(
    "Danh sách cuộn linh kiện",
    reel_message,
)

footer_html = (
    '<div class="zt-footer">'
    "ZeroTag Reel MVP · Trang Tổng quan hệ thống"
    "</div>"
)

st.markdown(
    footer_html,
    unsafe_allow_html=True,
)