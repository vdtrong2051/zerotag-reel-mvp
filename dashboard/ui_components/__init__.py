"""Các UI component dùng chung của ZeroTag Dashboard."""

from dashboard.ui_components.alert_panels import (
    AlertTone,
    alert_panel_html,
    build_scan_result_alert,
    normalize_alert_tone,
    render_alert_panel,
    render_scan_result_alert,
)
from dashboard.ui_components.event_table import (
    empty_event_table_html,
    event_table_html,
    render_event_table,
)
from dashboard.ui_components.metric_cards import (
    MetricTone,
    format_metric_value,
    metric_card_html,
    normalize_metric_tone,
    render_metric_card,
)
from dashboard.ui_components.reel_preview import (
    reel_preview_html,
    render_reel_preview,
)
from dashboard.ui_components.status_badges import (
    StatusTone,
    get_status_label,
    get_status_tone,
    normalize_status,
    render_status_badge,
    status_badge_html,
)


__all__ = [
    # Status badges
    "StatusTone",
    "get_status_label",
    "get_status_tone",
    "normalize_status",
    "render_status_badge",
    "status_badge_html",

    # Metric cards
    "MetricTone",
    "format_metric_value",
    "metric_card_html",
    "normalize_metric_tone",
    "render_metric_card",

    # Alert panels
    "AlertTone",
    "alert_panel_html",
    "build_scan_result_alert",
    "normalize_alert_tone",
    "render_alert_panel",
    "render_scan_result_alert",

    # Reel preview
    "reel_preview_html",
    "render_reel_preview",

    # Event table
    "empty_event_table_html",
    "event_table_html",
    "render_event_table",
]