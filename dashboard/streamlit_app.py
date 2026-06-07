from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from dashboard.api_client import (
    BackendClient,
    BackendClientError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STYLE_PATH = (
    PROJECT_ROOT
    / "dashboard"
    / "assets"
    / "styles"
    / "main.css"
)

BACKEND_CLIENT = BackendClient.from_env()


CORE_PAGES = [
    {
        "number": "01",
        "title": "Tổng quan hệ thống",
        "description": (
            "Theo dõi tổng số cuộn linh kiện, trạng thái tồn kho, "
            "cảnh báo BOM và các sự kiện mới nhất."
        ),
    },
    {
        "number": "02",
        "title": "Danh sách linh kiện",
        "description": (
            "Tìm kiếm và lọc cuộn linh kiện theo ZeroTag ID, "
            "mã linh kiện, lot và trạng thái."
        ),
    },
    {
        "number": "03",
        "title": "Hồ sơ số linh kiện",
        "description": (
            "Xem thông tin linh kiện, lot, date-code, số lượng, "
            "vị trí và dòng thời gian truy xuất."
        ),
    },
    {
        "number": "04",
        "title": "Đối chiếu BOM",
        "description": (
            "Gửi yêu cầu quét tới Backend và hiển thị kết quả "
            "hợp lệ, sai mã linh kiện hoặc sai lot."
        ),
    },
    {
        "number": "05",
        "title": "Nhật ký sự kiện",
        "description": (
            "Theo dõi lịch sử giao dịch quét và lọc theo "
            "loại sự kiện hoặc kết quả xử lý."
        ),
    },
]


def load_dashboard_styles() -> None:
    """Nạp CSS chung của Dashboard."""

    if not STYLE_PATH.exists():
        return

    css_content = STYLE_PATH.read_text(
        encoding="utf-8",
    )

    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True,
    )


def render_page_card(
    number: str,
    title: str,
    description: str,
) -> None:
    """Hiển thị card giới thiệu một trang Dashboard."""

    card_html = (
        '<div class="zt-card">'
        f'<div class="zt-card-number">{number}</div>'
        f'<div class="zt-card-title">{title}</div>'
        f'<div class="zt-card-text">{description}</div>'
        "</div>"
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )


@st.cache_data(
    ttl=5,
    show_spinner=False,
)
def check_backend_health(
    base_url: str,
    api_prefix: str,
) -> tuple[bool, dict[str, Any] | str]:
    """Kiểm tra Backend mà không làm Dashboard bị crash."""

    client = BackendClient(
        base_url=base_url,
        api_prefix=api_prefix,
    )

    try:
        health_data = client.health_check()
    except BackendClientError as error:
        return False, str(error)

    return True, health_data


def get_backend_identity(
    backend_health: dict[str, Any] | str,
) -> tuple[str, str]:
    """Lấy tên ứng dụng và môi trường từ health response."""

    if not isinstance(backend_health, dict):
        return "ZeroTag Backend", "không xác định"

    backend_name = backend_health.get(
        "app",
        "ZeroTag Backend",
    )

    environment = backend_health.get(
        "environment",
        "không xác định",
    )

    return str(backend_name), str(environment)


st.set_page_config(
    page_title="Trung tâm truy xuất cuộn linh kiện",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dashboard_styles()


backend_online, backend_health = check_backend_health(
    BACKEND_CLIENT.base_url,
    BACKEND_CLIENT.api_prefix,
)

backend_name, backend_environment = get_backend_identity(
    backend_health
)


with st.sidebar:
    st.markdown("## ZeroTag")
    st.caption("Hệ thống truy xuất cuộn linh kiện")

    st.divider()

    st.markdown("**Địa chỉ Backend**")

    st.code(
        BACKEND_CLIENT.base_url,
        language=None,
    )

    if backend_online:
        st.success(
            "Backend đã kết nối",
            icon="✅",
        )

        st.caption(
            f"{backend_name} · {backend_environment}"
        )
    else:
        st.error(
            "Backend ngoại tuyến",
            icon="⚠️",
        )

        st.caption(
            str(backend_health)
        )

    if st.button(
        "Làm mới kết nối",
        use_container_width=True,
    ):
        check_backend_health.clear()
        st.rerun()

    st.divider()

    st.markdown("**Phạm vi Day 4**")

    st.caption(
        "Tổng quan · Danh sách linh kiện · Hồ sơ số · "
        "Đối chiếu BOM · Nhật ký sự kiện"
    )

    st.divider()

    st.caption(
        "Theo dõi MSL và Xác minh chưa nằm trong "
        "phạm vi chức năng của Day 4."
    )


hero_html = (
    '<section class="zt-hero">'
    '<div class="zt-eyebrow">ZEROTAG REEL MVP</div>'
    '<h1 class="zt-title">'
    "Trung tâm truy xuất cuộn linh kiện"
    "</h1>"
    '<div class="zt-subtitle">'
    "Dashboard vận hành tập trung để theo dõi cuộn linh kiện, "
    "đối chiếu BOM, quản lý hồ sơ số và nhật ký sự kiện "
    "trong môi trường SMT/EMS."
    "</div>"
    "</section>"
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


title_column, status_column = st.columns(
    [3, 1],
    vertical_alignment="center",
)

with title_column:
    st.subheader("Các chức năng chính")

    st.caption(
        "Chọn một trang trong thanh điều hướng để bắt đầu."
    )

with status_column:
    if backend_online:
        st.success(
            "Backend đã kết nối",
            icon="✅",
        )

        st.caption(
            f"{backend_name} · {backend_environment}"
        )
    else:
        st.warning(
            "Backend ngoại tuyến",
            icon="⚠️",
        )

        st.caption(
            "Khởi động FastAPI Backend rồi bấm "
            "Làm mới kết nối."
        )


first_row = st.columns(3)

for column, page in zip(
    first_row,
    CORE_PAGES[:3],
    strict=True,
):
    with column:
        render_page_card(
            page["number"],
            page["title"],
            page["description"],
        )


second_row = st.columns(3)

for column, page in zip(
    second_row[:2],
    CORE_PAGES[3:],
    strict=True,
):
    with column:
        render_page_card(
            page["number"],
            page["title"],
            page["description"],
        )


footer_html = (
    '<div class="zt-footer">'
    "Day 4 · Streamlit Dashboard Core · "
    "Đã kích hoạt kiểm tra kết nối Backend API"
    "</div>"
)

st.markdown(
    footer_html,
    unsafe_allow_html=True,
)