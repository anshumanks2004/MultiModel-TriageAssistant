"""Reusable card components for analysis result display."""

import streamlit as st

from ui.styles import COLOR


def render_result_card(title: str, icon: str, items: list[str]) -> None:
    """Render a white card with a heading and a bulleted list of items.

    Args:
        title: Card heading text.
        icon:  Emoji or short string shown before the title.
        items: List of plain or HTML strings rendered as list items.
    """
    if not items:
        return
    items_html = "".join(
        f"<li style='padding:5px 0;border-bottom:1px solid #F2F3F4;font-size:0.9rem'>{item}</li>"
        for item in items
    )
    st.markdown(
        f"""
        <div class="ta-card">
            <div class="ta-card-header">
                <span style="font-size:1.3rem">{icon}</span>
                <span class="ta-card-title">{title}</span>
            </div>
            <ul style="margin:0;padding-left:20px;list-style:disc;color:{COLOR['text']}">
                {items_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, icon: str, body: str) -> None:
    """Render a white card with a heading and free-form HTML body.

    Args:
        title: Card heading text.
        icon:  Emoji or short string shown before the title.
        body:  HTML string rendered inside the card body.
    """
    st.markdown(
        f"""
        <div class="ta-card">
            <div class="ta-card-header">
                <span style="font-size:1.3rem">{icon}</span>
                <span class="ta-card-title">{title}</span>
            </div>
            <div style="font-size:0.9rem;color:{COLOR['text']}">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(value: str, label: str, color: str | None = None) -> None:
    """Render a compact stat tile (value + label) for dashboard-style rows.

    Args:
        value: Large number or short text to display prominently.
        label: Descriptive label beneath the value.
        color: Optional hex colour override for the value text.
    """
    c = color or COLOR["primary"]
    st.markdown(
        f"""
        <div class="ta-stat">
            <div class="ta-stat-value" style="color:{c}">{value}</div>
            <div class="ta-stat-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
