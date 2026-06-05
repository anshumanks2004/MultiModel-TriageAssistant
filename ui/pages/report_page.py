"""Medical Report Analysis page — PDF upload + structured results display.

Flow:
    PDF upload → temp file → extract text (PyMuPDF + EasyOCR) →
    clean → Llama3 inference → MedicalReportResult →
    report type + summary → key findings table → risk indicators →
    recommendations → doctor consultation → disclaimer
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from modules.report_analysis import MedicalReportResult, analyze_report
from ui.components.result_card import render_result_card
from ui.components.severity_badge import render_severity_badge
from ui.styles import COLOR, status_color, urgency_color

_PRIMARY = COLOR["primary"]
_MUTED = COLOR["text_muted"]

# Priority colours for recommendation pills
_PRIORITY_COLORS = {
    "Urgent": COLOR["danger"],
    "Soon": COLOR["info"],
    "Routine": COLOR["success"],
}


def render() -> None:
    """Render the Medical Report Analysis page."""

    # ── Page header ────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="ta-page-title">📄 Medical Report Analysis</p>'
        '<p class="ta-page-subtitle">'
        "Upload a PDF medical report — lab results, blood work, or diagnostics — "
        "for an AI-powered plain-language summary and risk assessment."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Upload section ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload your medical report (PDF, max 20 MB)",
        type=["pdf"],
        key="report_uploader",
        help="Only PDF files are supported. Maximum file size: 20 MB.",
    )

    if uploaded_file:
        size_kb = len(uploaded_file.getvalue()) / 1024
        st.caption(
            f"📎 `{uploaded_file.name}` · {size_kb:.1f} KB · "
            "Text will be extracted and sent to Llama3 for analysis."
        )

    analyze_clicked = st.button(
        "🔍 Analyse Report",
        type="primary",
        use_container_width=True,
        key="btn_analyse_report",
        disabled=(uploaded_file is None),
    )

    # ── Analysis logic ─────────────────────────────────────────────────────────
    if analyze_clicked and uploaded_file is not None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = Path(tmp.name)

        with st.spinner("Extracting and analysing report… this may take 30–60 seconds"):
            try:
                result: MedicalReportResult = analyze_report(tmp_path)
                st.session_state["report_result"] = result
            except FileNotFoundError as exc:
                st.error(str(exc))
                return
            except ValueError as exc:
                st.error(f"Could not process report: {exc}")
                return
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                _render_ollama_hint()
                return
            finally:
                tmp_path.unlink(missing_ok=True)

        st.rerun()

    # ── Results display ────────────────────────────────────────────────────────
    result: MedicalReportResult | None = st.session_state.get("report_result")
    if result is None:
        return

    st.markdown("<hr class='ta-divider'>", unsafe_allow_html=True)

    # Report type + summary
    st.markdown(
        f"<h3 style='color:{_PRIMARY};margin-bottom:4px'>{result.report_type}</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(result.summary)

    # ── Key Findings table ─────────────────────────────────────────────────────
    st.markdown(
        f"<p style='font-weight:700;font-size:1rem;color:{_PRIMARY};margin:16px 0 6px'>Key Findings</p>",
        unsafe_allow_html=True,
    )

    if result.key_findings:
        rows_html = ""
        for f in result.key_findings:
            badge_color = status_color(f.status)
            badge = (
                f"<span style='background:{badge_color};color:#fff;"
                f"padding:2px 10px;border-radius:999px;font-size:0.78rem;"
                f"font-weight:700;letter-spacing:0.04em'>{f.status.upper()}</span>"
            )
            rows_html += (
                f"<tr>"
                f"<td>{f.parameter}</td>"
                f"<td>{f.value}</td>"
                f"<td>{badge}</td>"
                f"<td>{f.reference_range or '—'}</td>"
                f"</tr>"
            )
        st.markdown(
            f"""
            <div class="ta-table-wrap">
              <table class="ta-table">
                <thead><tr>
                  <th>Parameter</th><th>Value</th>
                  <th>Status</th><th>Reference Range</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No individual parameters were identified in this report.")

    # ── Risk Indicators ────────────────────────────────────────────────────────
    if result.risk_indicators:
        st.markdown(
            f"<p style='font-weight:700;font-size:1rem;color:{_PRIMARY};margin:16px 0 6px'>"
            "Risk Indicators</p>",
            unsafe_allow_html=True,
        )
        for risk in result.risk_indicators:
            with st.container():
                col_badge, col_text = st.columns([1, 5])
                with col_badge:
                    render_severity_badge(risk.severity)
                with col_text:
                    st.markdown(
                        f"<strong>{risk.name}</strong><br>"
                        f"<span style='font-size:0.88rem;color:{_MUTED}'>{risk.rationale}</span>",
                        unsafe_allow_html=True,
                    )

    # ── Recommendations ────────────────────────────────────────────────────────
    if result.recommendations:
        rec_items = []
        for r in result.recommendations:
            pill_color = _PRIORITY_COLORS.get(r.priority, COLOR["text_muted"])
            rec_items.append(
                f"<span style='background:{pill_color};color:#fff;padding:1px 8px;"
                f"border-radius:999px;font-size:0.76rem;font-weight:700;"
                f"margin-right:6px'>{r.priority}</span>{r.action}"
            )
        render_result_card("Recommendations", "💊", rec_items)

    # ── Doctor Consultation ────────────────────────────────────────────────────
    consult = result.doctor_consultation
    urg_color = urgency_color(consult.urgency)
    specialties_str = (
        ", ".join(consult.specialties) if consult.specialties else "General Practitioner"
    )
    st.markdown(
        f"<div style='background:{urg_color};color:#fff;padding:16px 20px;"
        f"border-radius:10px;margin:14px 0;'>"
        f"<strong>🏥 Doctor Consultation:</strong>&nbsp;{consult.urgency}<br>"
        f"<small style='opacity:0.9'><strong>Specialties:</strong> {specialties_str}</small><br>"
        f"<small style='opacity:0.9'>{consult.reason}</small>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Disclaimer
    st.markdown(
        f'<div class="ta-disclaimer">⚠ {result.disclaimer}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("🔄 Analyse Another Report", key="btn_reset_report"):
        st.session_state.pop("report_result", None)
        st.rerun()


def _render_ollama_hint() -> None:
    """Show a troubleshooting tip when Ollama appears unreachable."""
    st.info(
        "**Troubleshooting:** Make sure Ollama is running and Llama3 is pulled.\n\n"
        "```bash\nollama serve\nollama pull llama3\n```",
        icon="💡",
    )
