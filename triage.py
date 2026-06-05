"""MultiModel-TriageAssistant — Streamlit application entry point.

Architecture
------------
triage.py               Bootstraps page config, CSS, sidebar, and router.
ui/styles.py            Global CSS theme injected once here.
ui/pages/               One module per page; each exposes render().
ui/components/          Reusable Streamlit widgets (cards, badges, banners).
modules/                Business logic — symptom / image / report analysis.
core/                   Ollama client, emergency detector, response parser.
config/                 Settings constants and LLM prompt templates.
utils/                  Input validators and logging setup.

Navigation
----------
Session state key "current_page" controls which page render() is called.
Sidebar buttons set that key and call st.rerun(). Home-page tiles do the
same, so navigation is consistent from both entry points.
"""

import streamlit as st

from core.ollama_client import check_health
from ui.pages import about_page, home_page, image_page, report_page, symptom_page
from ui.styles import inject_css
from utils.logger import setup_logging

# Initialise Python logging before any module emits log records.
setup_logging()

# ── Page configuration ─────────────────────────────────────────────────────────
# Must be the very first Streamlit call in the script.
st.set_page_config(
    page_title="MultiModel-TriageAssistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**MultiModel-TriageAssistant** — Educational health risk assessment "
            "powered by local LLMs via Ollama. Not a medical device."
        ),
    },
)

# Inject global CSS theme (custom properties, card styles, sidebar overrides, etc.)
inject_css()

# ── Session state defaults ─────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

# ── Navigation map ─────────────────────────────────────────────────────────────
# Ordered list of (sidebar_label, page_key, page_module).
# page_key is stored in session state; page_module is called for rendering.
NAV_ITEMS = [
    ("🏠  Home",             "Home",             home_page),
    ("🩺  Symptom Checker",  "Symptom Checker",  symptom_page),
    ("🖼️  Image Analysis",   "Image Analysis",   image_page),
    ("📄  Report Analysis",  "Report Analysis",  report_page),
    ("ℹ️  About",            "About",            about_page),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Brand header
    st.markdown(
        """
        <div style="text-align:center;padding:18px 0 20px">
            <span style="font-size:2.8rem">🏥</span><br>
            <strong style="font-size:1.05rem;color:#FDFEFE;letter-spacing:0.01em">
                MultiModel-TriageAssistant
            </strong><br>
            <small style="color:rgba(255,255,255,0.65);font-size:0.78rem">
                Intelligent Health Risk Assessment
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15);margin:0 0 12px'>",
                unsafe_allow_html=True)

    # Navigation buttons
    current = st.session_state["current_page"]
    for label, key, _ in NAV_ITEMS:
        is_active = current == key
        if st.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            if not is_active:
                st.session_state["current_page"] = key
                st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15);margin:12px 0'>",
                unsafe_allow_html=True)

    # System status — cached for 30 s to avoid hammering Ollama on every rerun
    @st.cache_data(ttl=30, show_spinner=False)
    def _get_health() -> dict:
        return check_health()

    health = _get_health()

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.55);"
        "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px'>"
        "System Status</p>",
        unsafe_allow_html=True,
    )

    status_rows = [
        ("Ollama",  health.get("ollama", False)),
        ("Llama3",  health.get("llama3", False)),
        ("LLaVA",   health.get("llava",  False)),
    ]
    for name, online in status_rows:
        dot   = "🟢" if online else "🔴"
        label = "Online" if online else "Offline"
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;"
            f"align-items:center;padding:3px 0;font-size:0.86rem'>"
            f"<span>{dot}&nbsp;{name}</span>"
            f"<span style='opacity:0.65;font-size:0.78rem'>{label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if not health.get("ollama", False):
        st.markdown(
            "<div style='background:rgba(255,255,255,0.08);border-radius:6px;"
            "padding:8px 10px;margin-top:10px;font-size:0.78rem;"
            "color:rgba(255,255,255,0.75)'>"
            "Run <code>ollama serve</code> to start the AI engine."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15);margin:12px 0'>",
                unsafe_allow_html=True)

    # Disclaimer
    st.markdown(
        "<div style='background:rgba(255,255,255,0.08);border-radius:8px;"
        "padding:10px 12px;font-size:0.76rem;color:rgba(255,255,255,0.70);"
        "line-height:1.5'>"
        "⚠ <strong style='color:rgba(255,255,255,0.90)'>Disclaimer:</strong> "
        "For <em>educational use only</em>. Not a substitute for professional "
        "medical advice."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center;font-size:0.72rem;"
        "color:rgba(255,255,255,0.35);margin-top:16px'>v1.0.0 · College Project</p>",
        unsafe_allow_html=True,
    )

# ── Page router ────────────────────────────────────────────────────────────────
# Resolve the active page module from the session-state key.
active_page = st.session_state["current_page"]
page_module  = next(
    (mod for _, key, mod in NAV_ITEMS if key == active_page),
    home_page,  # fallback if session state holds an unknown value
)
page_module.render()
