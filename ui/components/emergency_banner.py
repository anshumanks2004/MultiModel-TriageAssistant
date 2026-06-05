"""Emergency banner component.

Renders a colour-coded, level-graded alert block whenever the emergency
detector fires. Accepts an EmergencyResult (from core.emergency_detector)
or a plain keyword list for legacy callers.
"""

import streamlit as st

from core.emergency_detector import EmergencyLevel, EmergencyResult
from ui.styles import COLOR

# Per-level display config: background, icon, headline, sub-text
_LEVEL_CFG: dict[str, dict] = {
    EmergencyLevel.CRITICAL: {
        "bg":       COLOR["emergency_critical"],
        "icon":     "🚨",
        "headline": "CALL 911 IMMEDIATELY",
        "sub":      "Life-threatening emergency detected. Call emergency services now.",
    },
    EmergencyLevel.HIGH: {
        "bg":       COLOR["emergency_high"],
        "icon":     "⚠️",
        "headline": "Go to the Emergency Room Now",
        "sub":      "Serious emergency indicators detected. Seek immediate medical attention.",
    },
    EmergencyLevel.MODERATE: {
        "bg":       COLOR["emergency_moderate"],
        "icon":     "⚡",
        "headline": "Seek Care Today",
        "sub":      "Concerning symptoms detected. See a doctor or urgent-care clinic today.",
    },
}

_FALLBACK_CFG = {
    "bg":       COLOR["danger"],
    "icon":     "⚠️",
    "headline": "Emergency Symptoms Detected",
    "sub":      "Please seek medical attention immediately.",
}


def render_emergency_banner(
    result: "EmergencyResult | None" = None,
    keywords: "list[str] | None" = None,
) -> None:
    """Render the emergency alert banner.

    Args:
        result:   EmergencyResult from core.emergency_detector (preferred path).
        keywords: Fallback list of keyword strings when no EmergencyResult
                  is available (e.g. legacy symptom-page callers).
    """
    if result is None and not keywords:
        return

    if result is not None:
        if not result.is_emergency:
            return
        cfg = _LEVEL_CFG.get(result.level, _FALLBACK_CFG)
        score_txt = f"Score: {result.score:.0f}"
        alert_msg = result.alert_message
        triggered = [n.replace("_", " ").title() for n in result.triggered_categories]
        actions = result.immediate_actions[:6]
    else:
        cfg = _FALLBACK_CFG
        score_txt = ""
        alert_msg = cfg["sub"]
        triggered = keywords or []
        actions = []

    actions_html = "".join(f"<li style='margin:4px 0'>{a}</li>" for a in actions)
    categories_str = ", ".join(triggered) if triggered else "—"
    score_badge = (
        f'<span style="font-size:0.8rem;opacity:0.85;margin-left:10px">{score_txt}</span>'
        if score_txt else ""
    )

    st.markdown(
        f"""
        <div class="ta-emergency" style="background:{cfg['bg']};">
            <div class="ta-emergency-title">
                {cfg['icon']}&nbsp;{cfg['headline']}{score_badge}
            </div>
            <div class="ta-emergency-body" style="margin-bottom:8px">
                {alert_msg}
            </div>
            <div class="ta-emergency-body" style="margin-bottom:10px">
                <strong>Detected:</strong> {categories_str}
            </div>
            {'<details style="margin-top:4px"><summary style="cursor:pointer;font-weight:700;color:#fff;font-size:0.88rem">Immediate actions ▾</summary><ul style="margin:8px 0 0;padding-left:18px;font-size:0.88rem;color:rgba(255,255,255,0.95)">' + actions_html + '</ul></details>' if actions else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
