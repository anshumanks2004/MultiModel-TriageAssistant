"""Symptom Checker page — input form + AI triage results.

Flow:
    Patient context form → validation → analyze_symptoms() →
    emergency banner (if triggered) → severity + conditions + recommendations
    → consultation urgency → confidence → disclaimer → reset
"""

import streamlit as st

from modules.symptom_analysis.analyzer import SymptomAnalysisError, analyze_symptoms
from modules.symptom_analysis.schema import SymptomInput, SymptomResult
from ui.components.emergency_banner import render_emergency_banner
from ui.components.result_card import render_info_card, render_result_card
from ui.components.severity_badge import render_severity_badge
from ui.styles import COLOR, urgency_color
from utils.validators import ValidationError, validate_age, validate_symptom_text

_INTENSITY_LABELS = {1: "Very mild", 2: "Mild", 3: "Moderate", 4: "Severe", 5: "Very severe"}

# Pulled out of f-strings to avoid nested-bracket parse errors
_MUTED = COLOR["text_muted"]


def render() -> None:
    """Render the Symptom Checker page."""

    # ── Page header ────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="ta-page-title">🩺 Symptom Checker</p>'
        '<p class="ta-page-subtitle">'
        "Describe your symptoms and receive an AI-powered triage assessment. "
        "Emergency detection runs automatically before LLM analysis."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Input card ─────────────────────────────────────────────────────────────
    # _r suffix makes every widget key unique per reset cycle so Streamlit
    # re-mounts them fresh (clearing typed text, selections, slider value).
    _r = st.session_state.get("symptom_form_reset", 0)

    with st.container():
        # Patient context row
        st.markdown("**Patient Context** *(optional)*")
        col1, col2 = st.columns(2)
        with col1:
            age_input = st.text_input(
                "Age",
                placeholder="e.g. 35",
                key=f"symptom_age_{_r}",
                help="Enter a number between 0 and 130, or leave blank.",
            )
        with col2:
            sex_input = st.selectbox(
                "Biological Sex",
                ["Not specified", "Male", "Female", "Other"],
                key=f"symptom_sex_{_r}",
            )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Symptoms text area
        st.markdown("**Describe Your Symptoms** *(required)*")
        symptoms_text = st.text_area(
            label="Symptoms",
            placeholder=(
                "Example: I have had a severe headache, nausea, and sensitivity to light "
                "for the past 2 days. The pain is throbbing and gets worse with movement."
            ),
            height=150,
            key=f"symptom_text_{_r}",
            label_visibility="collapsed",
            help="Between 10 and 2,000 characters.",
        )
        char_count = len(symptoms_text.strip())
        st.caption(f"{char_count} / 2000 characters")

        # Duration + intensity row
        col3, col4 = st.columns(2)
        with col3:
            duration = st.selectbox(
                "Duration",
                [
                    "Not specified",
                    "Less than 24 hours",
                    "1–3 days",
                    "4–7 days",
                    "1–2 weeks",
                    "More than 2 weeks",
                ],
                key=f"symptom_duration_{_r}",
                help="How long have you had these symptoms?",
            )
        with col4:
            intensity = st.slider(
                "Self-rated Intensity",
                min_value=1,
                max_value=5,
                value=3,
                key=f"symptom_intensity_{_r}",
                help="1 = Very mild  ·  5 = Very severe",
            )
            st.caption(_INTENSITY_LABELS.get(intensity, ""))

        analyze_clicked = st.button(
            "🔍 Analyze Symptoms",
            type="primary",
            use_container_width=True,
            key="btn_analyze_symptoms",
            disabled=(char_count < 10),
        )

    # ── Analysis logic ─────────────────────────────────────────────────────────
    if analyze_clicked:
        try:
            clean_symptoms = validate_symptom_text(symptoms_text)
            clean_age = validate_age(age_input)
        except ValidationError as exc:
            st.error(str(exc))
            return

        symptom_input = SymptomInput(
            symptoms=clean_symptoms,
            age=clean_age,
            sex=sex_input,
            duration=duration,
            intensity=intensity,
        )

        with st.spinner("Analyzing symptoms… this may take up to 30 seconds"):
            try:
                result: SymptomResult = analyze_symptoms(symptom_input)
            except SymptomAnalysisError as exc:
                st.error(f"Analysis failed: {exc}")
                _render_ollama_hint()
                return
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
                return

        st.session_state["symptom_result"] = result
        st.rerun()

    # ── Results display ────────────────────────────────────────────────────────
    result: SymptomResult | None = st.session_state.get("symptom_result")
    if result is None:
        return

    st.markdown("<hr class='ta-divider'>", unsafe_allow_html=True)
    st.markdown("### Assessment Results")

    # Emergency banner — always rendered first
    if result.emergency_detected:
        render_emergency_banner(keywords=result.emergency_keywords)

    # Severity badge + reasoning
    render_severity_badge(result.severity_level)
    st.markdown(
        f"<p style='color:{_MUTED};font-size:0.9rem;margin-top:4px'>"
        f"{result.severity_reasoning}</p>",
        unsafe_allow_html=True,
    )

    # Conditions + recommendations side by side
    col_left, col_right = st.columns(2)
    with col_left:
        condition_items = []
        for c in result.possible_conditions:
            condition_items.append(
                f"<strong>{c.name}</strong> "
                f"<span style='color:{_MUTED}'>({c.likelihood} likelihood)</span>"
                f"<br><span style='font-size:0.85rem'>{c.brief_explanation}</span>"
            )
        render_result_card("Possible Conditions", "🔬", condition_items)

    with col_right:
        render_result_card("Recommendations", "💊", result.recommendations)

    # Consultation urgency banner
    urg_color = urgency_color(result.consultation_urgency)
    st.markdown(
        f"<div style='background:{urg_color};color:#fff;padding:14px 20px;"
        f"border-radius:10px;margin:12px 0;'>"
        f"<strong>🏥 Doctor Consultation Urgency:</strong>&nbsp;"
        f"{result.consultation_urgency}<br>"
        f"<small style='opacity:0.9'>{result.urgency_reasoning}</small>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Confidence
    render_info_card(
        "Confidence in Assessment",
        "📊",
        f"<strong>{result.confidence_level}</strong> — {result.confidence_reasoning}",
    )

    # Disclaimer
    st.markdown(
        f'<div class="ta-disclaimer">⚠ {result.disclaimer}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Reset — increment counter so all form widgets re-mount with blank state
    if st.button("🔄 Analyze Another", key="btn_reset_symptoms"):
        st.session_state.pop("symptom_result", None)
        st.session_state["symptom_form_reset"] = (
            st.session_state.get("symptom_form_reset", 0) + 1
        )
        st.rerun()


def _render_ollama_hint() -> None:
    """Show a troubleshooting tip when Ollama appears unreachable."""
    st.info(
        "**Troubleshooting:** Make sure Ollama is running and Llama3 is pulled.\n\n"
        "```bash\nollama serve\nollama pull llama3\n```",
        icon="💡",
    )
