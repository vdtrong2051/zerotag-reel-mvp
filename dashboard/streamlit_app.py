from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STYLE_PATH = (
    PROJECT_ROOT
    / "dashboard"
    / "assets"
    / "styles"
    / "main.css"
)

load_dotenv(PROJECT_ROOT / ".env")


BACKEND_HOST = os.getenv(
    "BACKEND_HOST",
    "127.0.0.1",
)

BACKEND_PORT = os.getenv(
    "BACKEND_PORT",
    "8000",
)

BACKEND_BASE_URL = (
    f"http://{BACKEND_HOST}:{BACKEND_PORT}"
)


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
    """Nạp CSS chung cho Dashboard."""

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
    """Hiển thị một card mô tả trang Dashboard."""

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


st.set_page_config(
    page_title="ZeroTag Reel Control Center",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dashboard_styles()


with st.sidebar:
    st.markdown("## ZeroTag")
    st.caption("Reel Traceability MVP")

    st.divider()

    st.markdown("**Backend target**")
    st.code(
        BACKEND_BASE_URL,
        language=None,
    )

    st.markdown(
        '<span class="zt-pill">Connection not checked</span>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Backend health check sẽ được kết nối "
        "sau khi BackendClient hoàn thành."
    )

    st.divider()

    st.markdown("**Day 4 scope**")
    st.caption(
        "Overview · Inventory · Passport · "
        "BOM Matching · Event Log"
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
    st.info(
        "App shell ready",
        icon="✅",
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
        Backend API integration pending
    </div>
    """,
    unsafe_allow_html=True,
)