"""Centralised CSS theme for the MultiModel-TriageAssistant.

Call `inject_css()` once at the top of app.py after st.set_page_config().
All component-level inline styles reference the CSS custom properties
defined here so colours stay consistent across pages.
"""

import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────────────────
COLOR = {
    # Brand
    "primary": "#1B4F72",
    "primary_light": "#2E86C1",
    "primary_dark": "#154360",
    # Semantic
    "success": "#1E8449",
    "warning": "#D4AC0D",
    "danger": "#C0392B",
    "info": "#2E86C1",
    # Neutral
    "surface": "#FAFAFA",
    "border": "#E5E8E8",
    "text": "#1C2833",
    "text_muted": "#717D7E",
    # Status pills
    "normal": "#1E8449",
    "abnormal": "#D4AC0D",
    "critical": "#C0392B",
    # Emergency
    "emergency_critical": "#922B21",
    "emergency_high": "#CA6F1E",
    "emergency_moderate": "#B7950B",
}

SEVERITY_COLORS = {
    "Low": COLOR["success"],
    "Medium": COLOR["warning"],
    "High": COLOR["danger"],
    "Critical": COLOR["emergency_critical"],
}

URGENCY_COLORS = {
    "EMERGENCY": COLOR["emergency_critical"],
    "Urgent (within 24 hours)": COLOR["danger"],
    "Soon (within 2-3 days)": COLOR["info"],
    "Routine (within 1-2 weeks)": COLOR["success"],
}

STATUS_COLORS = {
    "normal": COLOR["normal"],
    "abnormal": COLOR["abnormal"],
    "critical": COLOR["critical"],
}

# ── Global stylesheet ──────────────────────────────────────────────────────────
_CSS = """
<style>
/* ── Root variables ─────────────────────────────────────────────────────── */
:root {
    --color-primary:       #1B4F72;
    --color-primary-light: #2E86C1;
    --color-success:       #1E8449;
    --color-warning:       #D4AC0D;
    --color-danger:        #C0392B;
    --color-surface:       #FAFAFA;
    --color-border:        #E5E8E8;
    --color-text:          #1C2833;
    --color-text-muted:    #717D7E;
    --radius-sm:           6px;
    --radius-md:           10px;
    --radius-lg:           14px;
    --shadow-sm:           0 1px 3px rgba(0,0,0,0.08);
    --shadow-md:           0 3px 10px rgba(0,0,0,0.10);
    --transition:          0.18s ease;
}

/* ── Base overrides ─────────────────────────────────────────────────────── */
.stApp {
    background: #F0F4F8;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* Hide Streamlit's default top toolbar/header so it doesn't overlap content */
[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}

/* Also hide the top decoration bar (coloured line at very top) */
[data-testid="stDecoration"] {
    display: none !important;
}

/* Remove the gap Streamlit reserves for the hidden header */
[data-testid="stAppViewBlockContainer"],
.appview-container .main .block-container {
    padding-top: 1.5rem !important;
}

/* Canonical block-container selector — covers all Streamlit versions */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px;
}

/* ── Sidebar ────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B4F72 0%, #154360 100%);
    border-right: none;
}

[data-testid="stSidebar"] * {
    color: #FDFEFE !important;
}

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: var(--radius-md);
    color: #FDFEFE !important;
    font-weight: 500;
    letter-spacing: 0.01em;
    transition: background var(--transition), border-color var(--transition);
    margin-bottom: 4px;
    text-align: left;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.28);
}

/* Active nav button (primary type) */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: rgba(255,255,255,0.20);
    border-color: rgba(255,255,255,0.40);
    font-weight: 700;
}

/* ── Cards ──────────────────────────────────────────────────────────────── */
.ta-card {
    background: #FFFFFF;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 22px 24px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 16px;
}

.ta-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
}

.ta-card-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--color-primary);
    margin: 0;
}

.ta-card-body li {
    padding: 4px 0;
    border-bottom: 1px solid #F2F3F4;
    color: var(--color-text);
    font-size: 0.9rem;
}

.ta-card-body li:last-child { border-bottom: none; }

/* ── Stat tiles ─────────────────────────────────────────────────────────── */
.ta-stat {
    background: #FFFFFF;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    text-align: center;
    box-shadow: var(--shadow-sm);
}

.ta-stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--color-primary);
    line-height: 1;
}

.ta-stat-label {
    font-size: 0.78rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}

/* ── Severity & status badges ───────────────────────────────────────────── */
.ta-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #fff;
}

/* ── Page headings ──────────────────────────────────────────────────────── */
.ta-page-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--color-primary);
    margin-bottom: 2px;
}

.ta-page-subtitle {
    color: var(--color-text-muted);
    font-size: 0.9rem;
    margin-bottom: 20px;
}

/* ── Emergency banners ──────────────────────────────────────────────────── */
.ta-emergency {
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin-bottom: 18px;
    border-left: 5px solid rgba(255,255,255,0.5);
}

.ta-emergency-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #fff;
    margin-bottom: 6px;
}

.ta-emergency-body {
    color: rgba(255,255,255,0.92);
    font-size: 0.88rem;
}

/* ── Section divider ────────────────────────────────────────────────────── */
.ta-divider {
    height: 1px;
    background: var(--color-border);
    margin: 20px 0;
    border: none;
}

/* ── Upload area ────────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-lg);
    padding: 10px;
}

/* ── Primary button ─────────────────────────────────────────────────────── */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #1B4F72 0%, #2E86C1 100%);
    border: none;
    border-radius: var(--radius-md);
    font-weight: 700;
    letter-spacing: 0.02em;
    box-shadow: 0 2px 8px rgba(27,79,114,0.30);
    transition: opacity var(--transition), box-shadow var(--transition);
}

.stButton button[kind="primary"]:hover {
    opacity: 0.92;
    box-shadow: 0 4px 14px rgba(27,79,114,0.40);
}

/* ── Info / warning / error boxes ───────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-md) !important;
    font-size: 0.88rem;
}

/* ── Scrollable table ───────────────────────────────────────────────────── */
.ta-table-wrap {
    overflow-x: auto;
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
}

table.ta-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}

table.ta-table th {
    background: #EBF5FB;
    color: var(--color-primary);
    font-weight: 700;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 2px solid var(--color-border);
}

table.ta-table td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--color-border);
    vertical-align: middle;
}

table.ta-table tr:last-child td { border-bottom: none; }
table.ta-table tr:hover td { background: #F8FBFE; }

/* ── Spinner override ───────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--color-primary-light) !important;
}

/* ── Disclaimer box ─────────────────────────────────────────────────────── */
.ta-disclaimer {
    background: #FEF9E7;
    border: 1px solid #F9E79F;
    border-radius: var(--radius-md);
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #7D6608;
}

/* ── Footer ─────────────────────────────────────────────────────────────── */
.ta-footer {
    text-align: center;
    font-size: 0.75rem;
    color: var(--color-text-muted);
    padding: 24px 0 8px 0;
}
</style>
"""


def inject_css() -> None:
    """Inject the global stylesheet. Call once after st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def badge_html(text: str, color: str) -> str:
    """Return an inline HTML badge span."""
    return (
        f'<span class="ta-badge" style="background:{color}">{text}</span>'
    )


def urgency_color(urgency: str) -> str:
    """Map a consultation urgency string to a hex colour."""
    for key, color in URGENCY_COLORS.items():
        if key.upper() in urgency.upper():
            return color
    return COLOR["success"]


def severity_color(severity: str) -> str:
    """Map Low/Medium/High/Critical to a hex colour."""
    return SEVERITY_COLORS.get(severity, COLOR["text_muted"])


def status_color(status: str) -> str:
    """Map normal/abnormal/critical to a hex colour."""
    return STATUS_COLORS.get(status.lower(), COLOR["text_muted"])
