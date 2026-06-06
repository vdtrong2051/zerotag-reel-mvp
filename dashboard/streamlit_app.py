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
        "title": "Overview Dashboard",
        "description": (
            "Theo dõi tổng số reel, trạng thái tồn kho, "
            "cảnh báo BOM và các event mới nhất."
        ),
    },
    {
        "number": "02",
        "title": "Component Inventory",
        "description": (
            "Tìm kiếm và lọc reel theo ZeroTag ID, "
            "part number, lot và trạng thái."
        ),
    },
    {
        "number": "03",
        "title": "Digital Component Passport",
        "description": (
            "Xem hồ sơ số, thông tin lô, date-code, "
            "số lượng và timeline truy xuất."
        ),
    },
    {
        "number": "04",
        "title": "BOM Matching",
        "description": (
            "Gửi yêu cầu scan tới backend và hiển thị "
            "VALID, WRONG_PART hoặc LOT_MISMATCH."
        ),
    },
    {
        "number": "05",
        "title": "Event Log",
        "description": (
            "Theo dõi audit trail của các scan transaction "
            "và lọc theo loại event hoặc kết quả."
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

    st.markdown(
        f"""
        <div class="zt-card">
            <div class="zt-card-number">{number}</div>
            <div class="zt-card-title">{title}</div>
            <div class="zt-card-text">{description}</div>
        </div>
        """,
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
        return "ZeroTag Backend", "unknown"

    backend_name = backend_health.get(
        "app",
        "ZeroTag Backend",
    )

    environment = backend_health.get(
        "environment",
        "unknown",
    )

    return str(backend_name), str(environment)


st.set_page_config(
    page_title="ZeroTag Reel Control Center",
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
    st.caption("Reel Traceability MVP")

    st.divider()

    st.markdown("**Backend target**")

    st.code(
        BACKEND_CLIENT.base_url,
        language=None,
    )

    if backend_online:
        st.success(
            "Backend connected",
            icon="✅",
        )

        st.caption(
            f"{backend_name} · {backend_environment}"
        )
    else:
        st.error(
            "Backend offline",
            icon="⚠️",
        )

        st.caption(
            str(backend_health)
        )

    if st.button(
        "Refresh connection",
        use_container_width=True,
    ):
        check_backend_health.clear()
        st.rerun()

    st.divider()

    st.markdown("**Day 4 scope**")

    st.caption(
        "Overview · Inventory · Passport · "
        "BOM Matching · Event Log"
    )

    st.divider()

    st.caption(
        "MSL Tracking và Verification chưa nằm "
        "trong phạm vi chức năng Day 4."
    )


st.markdown(
    """
    <section class="zt-hero">
        <div class="zt-eyebrow">
            ZeroTag Reel MVP
        </div>

        <h1 class="zt-title">
            Reel Traceability Control Center
        </h1>

        <div class="zt-subtitle">
            Dashboard vận hành tập trung cho việc theo dõi
            component reel, kiểm tra BOM, hồ sơ số và audit
            event trong môi trường SMT/EMS.
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


title_column, status_column = st.columns(
    [3, 1],
    vertical_alignment="center",
)

with title_column:
    st.subheader("Dashboard Core Pages")

    st.caption(
        "Chọn một trang trong sidebar để bắt đầu."
    )

with status_column:
    if backend_online:
        st.success(
            "Backend connected",
            icon="✅",
        )

        st.caption(
            f"{backend_name} · {backend_environment}"
        )
    else:
        st.warning(
            "Backend offline",
            icon="⚠️",
        )

        st.caption(
            "Khởi động FastAPI backend rồi bấm "
            "Refresh connection."
        )


columns = st.columns(3)

for index, page in enumerate(CORE_PAGES):
    with columns[index % 3]:
        render_page_card(
            page["number"],
            page["title"],
            page["description"],
        )


st.markdown(
    """
    <div class="zt-footer">
        Day 4 · Streamlit Dashboard Core ·
        Backend API health check active
    </div>
    """,
    unsafe_allow_html=True,
)

