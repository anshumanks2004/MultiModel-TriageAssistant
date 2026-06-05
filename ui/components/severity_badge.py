"""Severity badge component — renders a colour-coded pill."""

import streamlit as st

from ui.styles import severity_color


def render_severity_badge(level: str, label_prefix: str = "Severity") -> None:
    """Render a coloured pill badge for a severity or urgency level.

    Args:
        level:        Severity string — Low / Medium / High / Critical.
        label_prefix: Text shown before the level value.
    """
    color = severity_color(level)
    st.markdown(
        f"""
        <div style="display:inline-block;padding:6px 20px;border-radius:999px;
                    background:{color};color:#fff;font-weight:700;
                    font-size:0.88rem;letter-spacing:0.06em;margin-bottom:10px;">
            {label_prefix}: {level.upper()}
        </div>
        """,
        unsafe_allow_html=True,
    )
