"""Medical Image Analysis page — upload form + LLaVA visual assessment results.

Flow:
    File upload + type selection + optional context →
    ImageInput validation → preprocess → LLaVA inference →
    emergency banner → severity → visual findings → conditions →
    consultation urgency → confidence → processing details → disclaimer
"""

from __future__ import annotations

import streamlit as st

from core.emergency_detector import EmergencyLevel, EmergencyResult
from modules.image_analysis.analyzer import ImageAnalysisError, analyze_image
from modules.image_analysis.preprocessor import ImagePreprocessError
from modules.image_analysis.schema import IMAGE_TYPES, ImageInput, ImageResult
from ui.components.emergency_banner import render_emergency_banner
from ui.components.result_card import render_info_card, render_result_card
from ui.components.severity_badge import render_severity_badge
from ui.styles import COLOR, urgency_color

_MUTED = COLOR["text_muted"]
_PRIMARY = COLOR["primary"]


def render() -> None:
    """Render the Medical Image Analysis page."""

    # ── Page header ────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="ta-page-title">🖼️ Medical Image Analysis</p>'
        '<p class="ta-page-subtitle">'
        "Upload a photograph of a visible medical condition for AI-powered visual "
        "assessment. Educational use only — not a diagnostic tool."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Limitations notice ─────────────────────────────────────────────────────
    with st.expander("⚠️ Important Limitations — Read Before Using", expanded=False):
        st.markdown(
            "- AI vision models analyse **photographs**, not patients — they cannot "
            "palpate, smell, or assess temperature.\n"
            "- Image quality, lighting, angle, and skin tone all affect accuracy.\n"
            "- LLaVA is a general-purpose vision model — it is **not trained on clinical "
            "dermatology datasets**.\n"
            "- Findings are descriptive observations, **not medical diagnoses**.\n"
            "- A photograph cannot replace physical examination, laboratory tests, or imaging.\n"
            "- **Never use this output to delay or avoid professional medical care.**"
        )

    # ── Upload section ─────────────────────────────────────────────────────────
    st.markdown("**Upload Medical Image**")
    # uploader_key increments on reset so Streamlit treats it as a new widget,
    # which clears the selected file from the UI.
    uploader_key = f"image_uploader_{st.session_state.get('image_uploader_reset', 0)}"

    col_up, col_type = st.columns([3, 1])
    with col_up:
        uploaded_file = st.file_uploader(
            label="Choose an image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            help="Supported: JPG, PNG, BMP, WEBP · Maximum: 10 MB",
            key=uploader_key,
            label_visibility="collapsed",
        )
    with col_type:
        image_type = st.selectbox(
            "Image Category",
            IMAGE_TYPES,
            help="Select the type of condition for a more focused analysis.",
            key="image_type_select",
        )

    user_context = st.text_area(
        "Additional Context *(optional)*",
        placeholder=(
            "Example: This rash appeared 3 days ago and is spreading. "
            "It is itchy and slightly warm to the touch."
        ),
        height=80,
        max_chars=500,
        key="image_context",
    )

    # Image preview + file metadata
    if uploaded_file:
        col_prev, col_meta = st.columns([1, 1])
        with col_prev:
            st.image(
                uploaded_file,
                caption="Preview — image will be preprocessed before analysis",
                use_container_width=True,
            )
        with col_meta:
            size_kb = len(uploaded_file.getvalue()) / 1024
            st.markdown(
                f"**File:** `{uploaded_file.name}`  \n"
                f"**Size:** {size_kb:.1f} KB  \n"
                f"**Format:** {uploaded_file.type or 'Unknown'}  \n"
                f"**Category:** {image_type}"
            )

    analyze_clicked = st.button(
        "🔍 Analyze Image",
        type="primary",
        use_container_width=True,
        disabled=(uploaded_file is None),
        key="btn_analyze_image",
    )

    # ── Analysis logic ─────────────────────────────────────────────────────────
    if analyze_clicked and uploaded_file:
        image_bytes = uploaded_file.getvalue()

        try:
            image_input = ImageInput(
                image_bytes=image_bytes,
                image_type=image_type,
                filename=uploaded_file.name,
                user_context=user_context or None,
            )
        except Exception as exc:
            st.error(f"Input validation error: {exc}")
            return

        with st.spinner(
            "Preprocessing image and running visual analysis… this may take 30–60 seconds"
        ):
            try:
                result: ImageResult = analyze_image(image_input)
            except ImagePreprocessError as exc:
                st.error(f"Image processing error: {exc}")
                return
            except ImageAnalysisError as exc:
                st.error(f"Analysis failed: {exc}")
                _render_ollama_hint(model="llava")
                return
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
                return

        st.session_state["image_result"] = result
        st.rerun()

    # ── Results display ────────────────────────────────────────────────────────
    result: ImageResult | None = st.session_state.get("image_result")
    if result is None:
        return

    st.markdown("<hr class='ta-divider'>", unsafe_allow_html=True)
    st.markdown("### Analysis Results")

    # Emergency banner
    if result.emergency_detected:
        mock_er = EmergencyResult(
            level=EmergencyLevel.HIGH,
            score=40.0,
            alert_message="Emergency indicators detected in the context you provided.",
            immediate_actions=["Call 911 / 112 immediately if the situation is life-threatening."],
            triggered_categories=[],
            matched_phrases=result.emergency_keywords,
            override_triggered=False,
            detection_time_ms=0.0,
        )
        render_emergency_banner(mock_er)

    # Severity
    render_severity_badge(result.severity_level)
    if result.seek_immediate_care:
        st.error("⚠️ **Seek immediate medical care based on these findings.**")
    st.markdown(
        f"<p style='color:{_MUTED};font-size:0.9rem;margin-top:4px'>"
        f"{result.severity_reasoning}</p>",
        unsafe_allow_html=True,
    )

    # Visual findings (full-width)
    render_info_card("Visual Findings", "🔬", result.visual_findings)

    # Structured observations table
    if result.structured_findings:
        st.markdown(
            f"<p style='font-weight:700;color:{_PRIMARY};margin-bottom:4px'>"
            "Structured Observations</p>",
            unsafe_allow_html=True,
        )
        rows_html = "".join(
            f"<tr>"
            f"<td>{f.observation}</td>"
            f"<td>{f.location or '—'}</td>"
            f"<td>{f.significance}</td>"
            f"</tr>"
            for f in result.structured_findings
        )
        st.markdown(
            f"""
            <div class="ta-table-wrap">
              <table class="ta-table">
                <thead><tr>
                  <th>Observation</th><th>Location</th><th>Significance</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Conditions + recommendations
    col_left, col_right = st.columns(2)
    with col_left:
        condition_items = [
            f"<strong>{c.name}</strong> "
            f"<span style='color:{_MUTED}'>({c.likelihood})</span>"
            f"<br><span style='font-size:0.85rem'>{c.brief_explanation}</span>"
            for c in result.possible_conditions
        ]
        render_result_card("Possible Conditions", "📋", condition_items)
    with col_right:
        render_result_card("Recommendations", "💊", result.recommendations)

    # Consultation urgency
    urg_color = urgency_color(result.consultation_urgency)
    st.markdown(
        f"<div style='background:{urg_color};color:#fff;padding:14px 20px;"
        f"border-radius:10px;margin:12px 0;'>"
        f"<strong>🏥 Consultation Urgency:</strong>&nbsp;{result.consultation_urgency}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Confidence + image quality
    col_conf, col_qual = st.columns(2)
    with col_conf:
        render_info_card(
            "Assessment Confidence",
            "📊",
            f"<strong>{result.confidence_level}</strong> — {result.confidence_reasoning}",
        )
    with col_qual:
        quality_note = (
            result.image_quality_note or "Image quality appears adequate for assessment."
        )
        render_info_card("Image Quality Note", "📷", quality_note)

    # Processing details expander
    if result.image_meta:
        meta = result.image_meta
        with st.expander("🔧 Processing Details", expanded=False):
            st.markdown(
                f"| Detail | Value |\n|---|---|\n"
                f"| Original dimensions | {meta.original_width} × {meta.original_height} px |\n"
                f"| Processed dimensions | {meta.processed_width} × {meta.processed_height} px |\n"
                f"| Original size | {meta.original_size_kb:.1f} KB |\n"
                f"| Processed size | {meta.processed_size_kb:.1f} KB |\n"
                f"| Resized | {'Yes' if meta.was_resized else 'No'} |\n"
                f"| Original format | {meta.original_format} |"
            )

    # Disclaimer
    st.markdown(
        f'<div class="ta-disclaimer">⚠ {result.disclaimer}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("🔄 Analyze Another Image", key="btn_reset_image"):
        st.session_state.pop("image_result", None)
        # Increment the key so the file uploader widget is re-mounted fresh
        st.session_state["image_uploader_reset"] = (
            st.session_state.get("image_uploader_reset", 0) + 1
        )
        st.rerun()


def _render_ollama_hint(model: str = "llava") -> None:
    """Show a troubleshooting tip when Ollama appears unreachable."""
    st.info(
        f"**Troubleshooting:** Make sure Ollama is running and `{model}` is pulled.\n\n"
        f"```bash\nollama serve\nollama pull {model}\n```",
        icon="💡",
    )
