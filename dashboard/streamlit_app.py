from __future__ import annotations

from pathlib import Path

import streamlit as st

from dashboard.ui_components.sidebar_navigation import (
    render_sidebar_navigation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PAGES_ROOT = (
    PROJECT_ROOT
    / "dashboard"
    / "pages"
)


st.set_page_config(
    page_title="ZeroTag Reel MVP",
    page_icon=":material/sell:",
    layout="wide",
    initial_sidebar_state="expanded",
)


overview_page = st.Page(
    PAGES_ROOT / "1_Overview.py",
    title="Tổng quan hệ thống",
    icon=":material/dashboard:",
    default=True,
)

inventory_page = st.Page(
    PAGES_ROOT / "2_Component_Inventory.py",
    title="Danh sách linh kiện",
    icon=":material/inventory_2:",
    url_path="component-inventory",
)

passport_page = st.Page(
    PAGES_ROOT / "3_Digital_Passport.py",
    title="Hồ sơ số linh kiện",
    icon=":material/badge:",
    url_path="digital-passport",
)

bom_page = st.Page(
    PAGES_ROOT / "4_BOM_Matching.py",
    title="Đối chiếu BOM",
    icon=":material/fact_check:",
    url_path="bom-matching",
)

event_page = st.Page(
    PAGES_ROOT / "5_Event_Log.py",
    title="Nhật ký sự kiện",
    icon=":material/list_alt:",
    url_path="event-log",
)


pages = [
    overview_page,
    inventory_page,
    passport_page,
    bom_page,
    event_page,
]


current_page = st.navigation(
    pages,
    position="hidden",
)


render_sidebar_navigation(
    pages,
)

current_page.run()