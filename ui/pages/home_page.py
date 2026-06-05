"""Home page — landing screen with feature overview and system status."""

import streamlit as st

from core.ollama_client import check_health
from ui.components.result_card import render_stat_card
from ui.styles import COLOR

_PRIMARY = COLOR["primary"]
_MUTED = COLOR["text_muted"]

# Feature tiles: (icon, title, description, page_key)
_FEATURES = [
    (
        "🩺",
        "Symptom Checker",
        "Describe symptoms in plain language and receive an AI triage assessment "
        "with severity level, possible conditions, and consultation urgency.",
        "Symptom Checker",
    ),
    (
        "🖼️",
        "Image Analysis",
        "Upload a photo of a visible condition (rash, wound, burn, swelling) for "
        "AI-powered visual assessment using the LLaVA vision model.",
        "Image Analysis",
    ),
    (
        "📄",
        "Report Analysis",
        "Upload a PDF lab report or diagnostic document to extract key findings, "
        "risk indicators, and plain-language recommendations via Llama3.",
        "Report Analysis",
    ),
    (
        "🚨",
        "Emergency Detection",
        "A fast, rule-based pre-scan runs on every input before the LLM — "
        "always-on protection that never relies on AI for life-threatening alerts.",
        None,
    ),
]


def render() -> None:
    """Render the Home landing page."""

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,{_PRIMARY} 0%,#2E86C1 100%);
                    color:#fff;border-radius:14px;padding:36px 40px;margin-bottom:28px;">
            <h1 style="margin:0 0 8px;color:#fff;font-size:2rem;font-weight:800;">
                🏥 MultiModel-TriageAssistant
            </h1>
            <p style="margin:0;font-size:1.05rem;opacity:0.92;max-width:600px;">
                Intelligent health risk assessment powered by local LLMs.
                All analysis runs on your machine — no data leaves your device.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Quick stats ────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("3", "Analysis Modules")
    with c2:
        render_stat_card("100%", "Local / Private", color=COLOR["success"])
    with c3:
        render_stat_card("9", "Emergency Categories")
    with c4:
        render_stat_card("0", "Data Uploaded", color=COLOR["success"])

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Feature tiles ──────────────────────────────────────────────────────────
    st.markdown(
        f"<p style='font-weight:700;font-size:1.1rem;color:{_PRIMARY};"
        "margin-bottom:12px'>Features</p>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    for idx, (icon, title, desc, page_key) in enumerate(_FEATURES):
        container = col_a if idx % 2 == 0 else col_b
        with container:
            st.markdown(
                f"""
                <div class="ta-card" style="min-height:140px">
                    <div class="ta-card-header">
                        <span style="font-size:1.6rem">{icon}</span>
                        <span class="ta-card-title" style="font-size:1rem">{title}</span>
                    </div>
                    <p style="font-size:0.88rem;color:{_MUTED};margin:0">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if page_key:
                if st.button(
                    f"Open {title} →",
                    key=f"home_nav_{page_key}",
                    use_container_width=True,
                ):
                    st.session_state["current_page"] = page_key
                    st.rerun()

    # ── System status ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-weight:700;font-size:1.1rem;color:{_PRIMARY};"
        "margin-bottom:10px'>System Status</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Checking Ollama…"):
        health = check_health()

    status_items = [
        ("Ollama server", health.get("ollama", False), "http://localhost:11434"),
        ("Llama3 (text)", health.get("llama3", False), "ollama pull llama3"),
        ("LLaVA (vision)", health.get("llava", False), "ollama pull llava"),
    ]

    cols = st.columns(3)
    for col, (name, online, hint) in zip(cols, status_items):
        dot = "🟢" if online else "🔴"
        state = "Online" if online else "Offline"
        tip = "" if online else f"  \n`{hint}`"
        col.markdown(
            f"**{dot} {name}**  \n"
            f"<span style='font-size:0.82rem;color:{_MUTED}'>{state}{tip}</span>",
            unsafe_allow_html=True,
        )

    # ── Disclaimer ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="ta-disclaimer">'
        "⚠ <strong>Disclaimer:</strong> This tool is for <em>educational purposes only</em> "
        "and is <strong>not a substitute for professional medical advice</strong>. "
        "Always consult a licensed healthcare provider for diagnosis and treatment."
        "</div>",
        unsafe_allow_html=True,
    )
