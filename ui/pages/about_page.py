"""About page — project overview, tech stack, and architecture diagram."""

import streamlit as st

from ui.styles import COLOR

_PRIMARY = COLOR["primary"]
_MUTED = COLOR["text_muted"]
_SUCCESS = COLOR["success"]

_STACK = [
    ("🖥️", "Streamlit", "UI framework — multi-page, component-based"),
    ("🤖", "Ollama", "Local LLM runtime — no cloud dependency"),
    ("📝", "Llama3", "Text analysis — symptom + report modules"),
    ("👁️", "LLaVA", "Vision analysis — image module"),
    ("🔍", "EasyOCR", "OCR fallback for scanned PDF pages"),
    ("📄", "PyMuPDF", "Native PDF text extraction"),
    ("✅", "Pydantic", "Schema validation for all LLM outputs"),
    ("🐍", "Python 3.12", "Runtime environment"),
]

_ARCHITECTURE = """
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                             │
│   Home · Symptom Checker · Image Analysis · Report Analysis    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
          ┌─────────────▼──────────────┐
          │      Validation Layer       │
          │  validators.py · Pydantic   │
          └─────────────┬──────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
┌────▼────┐       ┌─────▼─────┐      ┌────▼─────┐
│ Symptom │       │   Image   │      │  Report  │
│ Analyzer│       │  Analyzer │      │ Analyzer │
└────┬────┘       └─────┬─────┘      └────┬─────┘
     │                  │                  │
     │           ┌──────▼──────┐    ┌──────▼──────┐
     │           │ Preprocessor│    │  Extractor  │
     │           │  (PIL/EXIF) │    │PyMuPDF+OCR  │
     │           └──────┬──────┘    └──────┬──────┘
     │                  │                  │
┌────▼──────────────────▼──────────────────▼──────┐
│               Core Layer                         │
│  emergency_detector · ollama_client · parser     │
└────────────────────┬─────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   Ollama (local)    │
          │  Llama3 · LLaVA     │
          └─────────────────────┘
"""


def render() -> None:
    """Render the About page."""

    st.markdown(
        f"<p class='ta-page-title'>ℹ️ About This Project</p>"
        f"<p class='ta-page-subtitle'>"
        "MultiModel-TriageAssistant — a college-level project demonstrating intelligent "
        "health risk assessment using local LLMs via Ollama."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Tech stack ─────────────────────────────────────────────────────────────
    st.markdown(
        f"<p style='font-weight:700;font-size:1rem;color:{_PRIMARY};margin-bottom:10px'>"
        "Technology Stack</p>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    for idx, (icon, name, desc) in enumerate(_STACK):
        col = col_a if idx % 2 == 0 else col_b
        with col:
            st.markdown(
                f"<div class='ta-card' style='padding:14px 18px;margin-bottom:10px'>"
                f"<span style='font-size:1.2rem'>{icon}</span>&nbsp;"
                f"<strong style='color:{_PRIMARY}'>{name}</strong><br>"
                f"<span style='font-size:0.84rem;color:{_MUTED}'>{desc}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Architecture diagram ───────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-weight:700;font-size:1rem;color:{_PRIMARY};margin-bottom:6px'>"
        "Architecture</p>",
        unsafe_allow_html=True,
    )
    st.code(_ARCHITECTURE, language=None)

    # ── Key design principles ──────────────────────────────────────────────────
    st.markdown(
        f"<p style='font-weight:700;font-size:1rem;color:{_PRIMARY};"
        "margin:16px 0 8px'>Design Principles</p>",
        unsafe_allow_html=True,
    )
    principles = [
        ("🔒 Privacy-first", "All inference runs locally — no patient data leaves the device."),
        ("⚡ Fast emergency detection", "Rule-based pre-scan runs before any LLM call, ensuring life-threatening keywords are never missed due to model latency."),
        ("🧱 Layered architecture", "UI → Validation → Module → Core → Ollama. Each layer is independently testable."),
        ("✅ Schema-validated outputs", "All LLM responses are parsed through Pydantic models — hallucinated fields are rejected at the boundary."),
        ("🔁 Graceful OCR fallback", "PyMuPDF handles native PDFs; EasyOCR handles scanned pages — the caller sees one unified text string."),
    ]
    for icon_title, body in principles:
        st.markdown(
            f"<div class='ta-card' style='padding:12px 18px;margin-bottom:8px'>"
            f"<strong style='color:{_PRIMARY}'>{icon_title}</strong><br>"
            f"<span style='font-size:0.88rem;color:{_MUTED}'>{body}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='ta-footer'>v1.0.0 · College Project · "
        "Built with Streamlit + Ollama + PyMuPDF + EasyOCR</div>",
        unsafe_allow_html=True,
    )
