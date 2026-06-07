from __future__ import annotations

from collections.abc import Sequence

import streamlit as st
from streamlit.navigation.page import StreamlitPage


SIDEBAR_STATE_KEY = "zt_sidebar_compact"


def toggle_sidebar() -> None:
    """Chuyển sidebar giữa trạng thái đầy đủ và thu gọn."""
    current_state = bool(st.session_state.get(SIDEBAR_STATE_KEY, False))
    st.session_state[SIDEBAR_STATE_KEY] = not current_state


def build_sidebar_css(*, compact: bool) -> str:
    """Tạo CSS cho sidebar ZeroTag."""

    sidebar_width = "64px" if compact else "216px"

    # ── Trạng thái THU GỌN (rail 64px) ──────────────────────────────────────
    compact_css = """
    /* Ẩn tất cả text */
    .zt-sidebar-brand__text,
    .zt-sidebar-copyright,
    .st-key-zt_sidebar_links a p,
    .st-key-zt_sidebar_links button p,
    .st-key-zt_sidebar_footer button p {
        display: none !important;
    }

    /* Brand: chỉ icon, căn giữa */
    .zt-sidebar-brand {
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 72px !important;
        padding: 0 !important;
        gap: 0 !important;
        border-bottom: 1px solid var(--zt-border-default, #d6e0e3);
    }
    .zt-sidebar-brand__icon {
        flex: 0 0 40px !important;
        width: 40px !important;
        height: 40px !important;
    }

    /* Nav items: căn giữa, vuông 42×42 */
    .st-key-zt_sidebar_links [data-testid="stPageLink"],
    .st-key-zt_sidebar_links [data-testid="stButton"],
    .st-key-zt_sidebar_footer [data-testid="stButton"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 0 4px !important;
        padding: 0 !important;
    }

    .st-key-zt_sidebar_links a,
    .st-key-zt_sidebar_links button,
    .st-key-zt_sidebar_footer button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        width: 42px !important;
        min-width: 42px !important;
        max-width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
        overflow: hidden !important;
    }

    .st-key-zt_sidebar_links a > div,
    .st-key-zt_sidebar_links button > div,
    .st-key-zt_sidebar_footer button > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }

    /* Icon cố định 22px */
    .st-key-zt_sidebar_links [data-testid="stIconMaterial"],
    .st-key-zt_sidebar_footer [data-testid="stIconMaterial"] {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex: 0 0 22px !important;
        width: 22px !important;
        min-width: 22px !important;
        max-width: 22px !important;
        height: 22px !important;
        font-size: 22px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    """

    # ── Trạng thái MỞ RỘNG (216px) ──────────────────────────────────────────
    expanded_css = """
    /* ── Trạng thái mở rộng 216px ─────────────────────────── */

    .st-key-zt_sidebar_links [data-testid="stPageLink"],
    .st-key-zt_sidebar_links [data-testid="stButton"],
    .st-key-zt_sidebar_footer [data-testid="stButton"] {
        display: flex !important;

        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;

        margin: 0 0 4px !important;
        padding: 0 !important;
    }

    .st-key-zt_sidebar_links a,
    .st-key-zt_sidebar_links button,
    .st-key-zt_sidebar_footer button {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;

        box-sizing: border-box !important;

        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;

        height: 46px !important;
        min-height: 46px !important;

        padding: 0 12px !important;

        /* Icon và chữ là sibling trực tiếp. */
        column-gap: 12px !important;
    }

    /* Wrapper nội bộ không được chiếm hết chiều rộng và nuốt gap. */
    .st-key-zt_sidebar_links a > div,
    .st-key-zt_sidebar_links button > div,
    .st-key-zt_sidebar_footer button > div {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;

        width: auto !important;
        min-width: 0 !important;

        margin: 0 !important;
        padding: 0 !important;

        gap: 0 !important;
    }

    .st-key-zt_sidebar_links a p,
    .st-key-zt_sidebar_links button p,
    .st-key-zt_sidebar_footer button p {
        display: block !important;

        flex: 1 1 auto !important;

        width: auto !important;
        min-width: 0 !important;

        margin: 0 !important;
        padding: 0 !important;

        overflow: hidden !important;

        font-size: 13px !important;
        line-height: 1.25 !important;

        text-align: left !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }

    .st-key-zt_sidebar_links [data-testid="stIconMaterial"],
    .st-key-zt_sidebar_footer [data-testid="stIconMaterial"] {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;

        flex: 0 0 21px !important;

        width: 21px !important;
        min-width: 21px !important;
        max-width: 21px !important;

        height: 21px !important;

        margin: 0 !important;
        padding: 0 !important;

        font-size: 21px !important;
    }
    """
    

    state_css = compact_css if compact else expanded_css

    css = f"""
    <style>
    /* ── Ẩn nav mặc định Streamlit ─────────────────────────────────────────── */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }}

    section[data-testid="stSidebar"]
    [data-testid="stSidebarContent"] {{
        padding-top: 0 !important;
    }}

    /* ── Layout: flex row, sidebar + main chia nhau không gian ─────────────── */

    /* Sidebar: flex item cứng */
    section[data-testid="stSidebar"] {{
        display: flex !important;
        flex-direction: column !important;
        flex: 0 0 {sidebar_width} !important;
        width: {sidebar_width} !important;
        min-width: {sidebar_width} !important;
        max-width: {sidebar_width} !important;
        height: 100vh !important;
        height: 100dvh !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        transform: none !important;
        position: relative !important;
        background: var(--zt-bg-sidebar, #eaf2f4);
        border-right: 1px solid var(--zt-border-default, #d6e0e3);
        transition:
            width 140ms ease,
            min-width 140ms ease,
            max-width 140ms ease,
            flex 140ms ease;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        background: var(--zt-bg-sidebar, #eaf2f4);
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
        display: flex !important;
        flex-direction: column !important;
        box-sizing: border-box !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        flex: 1 1 auto !important;
    }}

    /* Wrapper trực tiếp dùng đủ chiều cao sidebar. */
    section[data-testid="stSidebar"]
    [data-testid="stSidebarUserContent"]
    > div:first-child {{
        box-sizing: border-box !important;

        width: 100% !important;
        height: 100% !important;
        min-height: 0 !important;

        margin: 0 !important;
        padding: 0 !important;
    }}


    /* Chỉ block chứa brand + nav + footer mới là flex-column toàn chiều cao. */
    section[data-testid="stSidebar"]
    [data-testid="stSidebarUserContent"]
    section[data-testid="stSidebar"]
    [data-testid="stSidebarUserContent"]
    [data-testid="stVerticalBlock"]:has(
        .st-key-zt_sidebar_brand
    ):has(
        .st-key-zt_sidebar_links
    ):has(
        .st-key-zt_sidebar_footer
    ) {{
        display: flex !important;
        flex-direction: column !important;

        box-sizing: border-box !important;

        width: 100% !important;
        height: 100% !important;
        min-height: 0 !important;

        margin: 0 !important;
        padding: 0 !important;

        gap: 0 !important;
    }}


    /* Các VerticalBlock con trở lại kích thước nội dung bình thường. */
    section[data-testid="stSidebar"]
    [data-testid="stSidebarUserContent"]
    [data-testid="stVerticalBlock"]
    [data-testid="stVerticalBlock"] {{
        height: auto !important;
        min-height: 0 !important;

        flex: 0 0 auto !important;
    }}

    /* Main content: phần còn lại */
    [data-testid="stMain"] {{
        min-width: 0 !important;
        width: auto !important;
        margin-left: 0 !important;
        overflow-x: hidden !important;
    }}


    [data-testid="stMainBlockContainer"] {{
        width: 100% !important;
        max-width: none !important;
    }}

    /* ── Brand: sticky ở đầu, layout DỌC (icon trên, text dưới) ────────────── */
    .st-key-zt_sidebar_brand {{
        position: static !important;
        z-index: 10 !important;

        flex-shrink: 0 !important;

        box-sizing: border-box !important;

        width: 100% !important;

        margin: 0 !important;
        padding: 8px 12px 0 !important;

        overflow: hidden !important;

        background:
            var(--zt-bg-sidebar, #eaf2f4);
    }}


    .st-key-zt_sidebar_brand > div,
    .st-key-zt_sidebar_brand
    [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;

        margin: 0 !important;
        padding: 0 !important;
    }}


    /* Logo và tên nằm ngang như bản thiết kế. */
    .zt-sidebar-brand {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;

        box-sizing: border-box !important;

        width: 100% !important;
        min-height: 72px !important;

        margin: 0 !important;
        padding: 0 0 14px !important;

        gap: 10px !important;

        border-bottom: 1px solid
            var(--zt-border-default, #d6e0e3);
    }}


    .zt-sidebar-brand__icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;

        flex: 0 0 40px;

        width: 40px;
        height: 40px;

        color:
            var(--zt-text-on-primary, #ffffff);

        background:
            var(--zt-primary, #00969f);

        border-radius:
            var(--zt-radius-medium, 8px);
    }}


    .zt-sidebar-brand__icon svg {{
        display: block;

        width: 22px;
        height: 22px;
    }}


    .zt-sidebar-brand__text {{
        min-width: 0;

        overflow: hidden;
    }}


    .zt-sidebar-brand__name {{
        overflow: hidden;

        color:
            var(--zt-text-primary, #10232d);

        font-size: 19px;
        font-weight:
            var(--zt-weight-bold, 700);
        line-height: 1.15;

        text-overflow: ellipsis;
        white-space: nowrap;
    }}


    .zt-sidebar-brand__caption {{
        margin-top: 4px;

        overflow: hidden;

        color:
            var(--zt-primary-active, #007c86);

        font-size: 10px;
        font-weight:
            var(--zt-weight-semibold, 600);

        letter-spacing: 0.05em;
        line-height: 1.2;

        text-overflow: ellipsis;
        text-transform: uppercase;
        white-space: nowrap;
    }}

    /* ── Navigation: chiếm khoảng giữa ──────────────────────────────────────── */
    .st-key-zt_sidebar_links {{
        position: relative !important;
        z-index: 9 !important;
        flex: 1 1 auto !important;
        box-sizing: border-box !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 10px 8px !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        background: var(--zt-bg-sidebar, #eaf2f4);
        scrollbar-width: none;
    }}

    .st-key-zt_sidebar_links::-webkit-scrollbar {{
        display: none;
    }}

    .st-key-zt_sidebar_links > div,
    .st-key-zt_sidebar_links [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Base style cho tất cả link & button nav */
    .st-key-zt_sidebar_links a,
    .st-key-zt_sidebar_links button {{
        min-height: 48px !important;
        color: var(--zt-text-secondary, #526771) !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: var(--zt-radius-medium, 8px) !important;
        box-shadow: none !important;
    }}

    .st-key-zt_sidebar_links a:hover,
    .st-key-zt_sidebar_links button:hover {{
        color: var(--zt-primary-active, #007c86) !important;
        background: var(--zt-bg-hover, #deedef) !important;
        border-color: var(--zt-border-default, #d6e0e3) !important;
    }}

    /* Active: filled xanh đậm + text trắng, giống thiết kế gốc */
    .st-key-zt_sidebar_links
    a[aria-current="page"] {{
        position: relative !important;

        color:
            var(--zt-primary-active, #007c86)
            !important;

        background:
            var(--zt-bg-selected, #d8edef)
            !important;

        border-color: #9fcfd3 !important;

        box-shadow:
            inset 3px 0 0
            var(--zt-primary, #00969f) !important;

        font-weight:
            var(--zt-weight-semibold, 600)
            !important;
    }}


    .st-key-zt_sidebar_links
    a[aria-current="page"]
    [data-testid="stIconMaterial"] {{
        color:
            var(--zt-primary-active, #007c86)
            !important;
    }}

    .st-key-zt_sidebar_links a[aria-current="page"] [data-testid="stIconMaterial"] {{
        color: #ffffff !important;
    }}

    .st-key-zt_sidebar_links button:disabled {{
        color: var(--zt-text-disabled, #91a0a7) !important;
        background: transparent !important;
        border-color: transparent !important;
        opacity: 0.65;
    }}

    /* ── Footer: sticky ở cuối ───────────────────────────────────────────────── */
    .st-key-zt_sidebar_footer {{
        position: static !important;
        z-index: 10 !important;
        flex-shrink: 0 !important;
        box-sizing: border-box !important;
        width: 100% !important;
        margin: 0 0 !important;
        padding: 8px 8px !important;
        overflow: hidden !important;
        background: var(--zt-bg-sidebar, #eaf2f4);
        border-top: 1px solid var(--zt-border-default, #d6e0e3);
    }}

    .st-key-zt_sidebar_footer > div,
    .st-key-zt_sidebar_footer [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }}

    /* Copyright text */
    .zt-sidebar-copyright {{
        display: block;

        box-sizing: border-box;

        width: 100%;

        margin: 0;
        padding: 0 8px 10px;

        overflow: hidden;

        color:
            var(--zt-text-muted, #82949d);

        font-size: 10px;
        line-height: 1.5;

        white-space: normal;
    }}

    .st-key-zt_sidebar_footer button {{
        min-height: 40px !important;
        color: var(--zt-text-secondary, #526771) !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: var(--zt-radius-medium, 8px) !important;
        box-shadow: none !important;
    }}

    .st-key-zt_sidebar_footer button:hover {{
        color: var(--zt-primary-active, #007c86) !important;
        background: var(--zt-bg-hover, #deedef) !important;
        border-color: var(--zt-border-default, #d6e0e3) !important;
    }}

    .st-key-zt_sidebar_footer button {{
        height: 42px !important;
        min-height: 42px !important;

        padding: 0 10px !important;
    }}


    .st-key-zt_sidebar_footer button p {{
        font-size: 12px !important;
        font-weight: 500 !important;
    }}

    {state_css}
    </style>
    """

    return css


def render_sidebar_navigation(
    pages: Sequence[StreamlitPage],
) -> None:
    """Hiển thị sidebar ZeroTag với một nút thu/mở."""

    if SIDEBAR_STATE_KEY not in st.session_state:
        st.session_state[SIDEBAR_STATE_KEY] = False

    compact = bool(st.session_state[SIDEBAR_STATE_KEY])

    st.markdown(
        build_sidebar_css(compact=compact),
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────────
        with st.container(key="zt_sidebar_brand"):
            brand_html = (
                '<div class="zt-sidebar-brand">'
                  '<div class="zt-sidebar-brand__icon" aria-hidden="true">'
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"'
                    ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                      '<path d="M20 13 13 20 3 10V3h7Z"/>'
                      '<circle cx="7.5" cy="7.5" r="1.5"/>'
                    "</svg>"
                  "</div>"
                  '<div class="zt-sidebar-brand__text">'
                    '<div class="zt-sidebar-brand__name">ZeroTag</div>'
                    '<div class="zt-sidebar-brand__caption">'
                    "Dashboard V1.0"
                    "</div>"
                  "</div>"
                "</div>"
            )
            st.markdown(brand_html, unsafe_allow_html=True)

        # ── Navigation links ─────────────────────────────────────────────────
        with st.container(key="zt_sidebar_links"):
            for page in pages:
                st.page_link(
                    page,
                    label=page.title,
                    icon=page.icon,
                    help=page.title if compact else None,
                    width="stretch",
                )

            st.button(
                "Theo dõi MSL",
                icon=":material/water_drop:",
                disabled=True,
                help="Chưa nằm trong phạm vi Day 4.",
                width="stretch",
                key="zt_msl_disabled",
            )

            st.button(
                "Xác minh",
                icon=":material/verified_user:",
                disabled=True,
                help="Chưa nằm trong phạm vi Day 4.",
                width="stretch",
                key="zt_verification_disabled",
            )

        # ── Footer (copyright + toggle) ───────────────────────────────────────
        with st.container(key="zt_sidebar_footer"):
            copyright_html = (
                '<div class="zt-sidebar-copyright">'
                "© 2026 ZeroTag Systems<br>All rights reserved."
                "</div>"
            )
            st.markdown(copyright_html, unsafe_allow_html=True)

            st.button(
                "Mở rộng" if compact else "Thu gọn",
                icon=(
                    ":material/keyboard_double_arrow_right:"
                    if compact
                    else ":material/keyboard_double_arrow_left:"
                ),
                help=(
                    "Mở rộng thanh điều hướng"
                    if compact
                    else "Thu gọn thanh điều hướng"
                ),
                width="stretch",
                key="zt_sidebar_toggle",
                on_click=toggle_sidebar,
            )