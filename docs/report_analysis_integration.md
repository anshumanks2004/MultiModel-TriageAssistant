# Medical Report Analysis — Integration Guide

## Architecture Overview

```
PDF File
  │
  ▼
┌─────────────────────────────────────┐
│  extractor.py                       │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  PyMuPDF    │→ │  EasyOCR     │  │  (OCR only for image-only pages)
│  │  native     │  │  fallback    │  │
│  └─────────────┘  └──────────────┘  │
└─────────────────────────────────────┘
  │  raw text (pages joined by \f)
  ▼
┌─────────────────────────────────────┐
│  cleaner.py                         │
│  Unicode → OCR fixup → noise strip  │
│  → whitespace collapse → truncate   │
└─────────────────────────────────────┘
  │  clean text (≤ 6000 chars)
  ▼
┌─────────────────────────────────────┐
│  prompts.py                         │
│  SYSTEM_PROMPT + build_user_prompt  │
└─────────────────────────────────────┘
  │  formatted prompt
  ▼
┌─────────────────────────────────────┐
│  core/ollama_client.py              │
│  Llama3 via Ollama REST API         │
│  temperature=0.1, retry=2           │
└─────────────────────────────────────┘
  │  raw JSON string
  ▼
┌─────────────────────────────────────┐
│  core/response_parser.py            │
│  Strip fences → JSON parse          │
│  → Pydantic MedicalReportResult     │
└─────────────────────────────────────┘
  │
  ▼
MedicalReportResult (structured output)
```

---

## Prerequisites

### 1. Python dependencies
All required packages are already in `requirements.txt`:
```
pymupdf>=1.24.0
easyocr>=1.7.1
```
Install with:
```bash
pip install -r requirements.txt
```

### 2. Ollama + Llama3
```bash
# Install Ollama (macOS)
brew install ollama

# Pull the model (one-time, ~4 GB)
ollama pull llama3

# Start the server
ollama serve
```
Verify it is running:
```bash
curl http://localhost:11434/api/tags
```

---

## OCR Workflow

EasyOCR is **lazy-loaded** — the model files (~100 MB) are downloaded on the first scanned page encountered, then cached in memory for the session.

| Page type | Detection | Method |
|-----------|-----------|--------|
| Native PDF text | `len(page.get_text()) >= 30` chars | PyMuPDF — fast |
| Scanned / image | Below threshold | Render at 200 DPI → EasyOCR |

Tune `MIN_CHARS_NATIVE` and `OCR_DPI` in [extractor.py](../modules/report_analysis/extractor.py) if needed.

---

## Prompt Engineering

The system uses a **two-turn chat** structure with Llama3:

**System prompt** (`SYSTEM_PROMPT` in [prompts.py](../modules/report_analysis/prompts.py)):
- Establishes clinical decision-support role.
- Enforces JSON-only output (no markdown fences, no preamble).
- Lists exact string literals for enum fields to prevent hallucinated values.
- Instructs the model never to invent values absent from the report.

**User prompt** (`build_user_prompt()`):
- Injects the cleaned report text inside a clearly delimited block.
- Embeds the full JSON schema inline so the model self-validates field names and types.
- Ends with an explicit "return JSON only" instruction.

**Temperature**: `0.1` — deterministic, factual output preferred over creativity.

---

## Output Schema

`MedicalReportResult` fields:

| Field | Type | Description |
|-------|------|-------------|
| `report_type` | str | e.g. "Complete Blood Count" |
| `summary` | str | Plain-language 2–4 sentence overview |
| `key_findings` | list[KeyFinding] | Per-parameter values and status |
| `risk_indicators` | list[RiskIndicator] | Named risks with Low/Medium/High severity |
| `recommendations` | list[Recommendation] | Actions with Routine/Soon/Urgent priority |
| `doctor_consultation` | DoctorConsultation | Urgency, specialties, reason |
| `disclaimer` | str | Fixed safety disclaimer |

---

## Programmatic Usage

```python
from modules.report_analysis import analyze_report, MedicalReportResult

result: MedicalReportResult = analyze_report("path/to/report.pdf")

print(result.report_type)
print(result.summary)

for finding in result.key_findings:
    print(f"{finding.parameter}: {finding.value} [{finding.status}]")

for risk in result.risk_indicators:
    print(f"[{risk.severity}] {risk.name} — {risk.rationale}")

for rec in result.recommendations:
    print(f"[{rec.priority}] {rec.action}")

consult = result.doctor_consultation
print(f"Consultation: {consult.urgency} — {consult.reason}")
```

---

## Error Handling

| Exception | Cause | Caller action |
|-----------|-------|---------------|
| `FileNotFoundError` | PDF path doesn't exist | Show user error |
| `ValueError` | Not a PDF / oversized / LLM malformed JSON | Show user error |
| `OllamaClientError` | Ollama unreachable or HTTP error | Show connectivity hint |

---

## Configuration

Relevant constants in [config/settings.py](../config/settings.py):

| Constant | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_TEXT_MODEL` | `"llama3"` | Model used for report analysis |
| `OLLAMA_TIMEOUT` | `120` s | Per-request timeout |
| `OLLAMA_RETRY_ATTEMPTS` | `2` | Retries on connection error |
| `MAX_REPORT_FILE_SIZE_MB` | `20` | Upload size gate |

Extractor-level tuning in [extractor.py](../modules/report_analysis/extractor.py):

| Constant | Default | Purpose |
|----------|---------|---------|
| `MIN_CHARS_NATIVE` | `30` | Characters threshold before OCR fallback |
| `OCR_DPI` | `200` | Render resolution for EasyOCR |

Cleaner limit in [cleaner.py](../modules/report_analysis/cleaner.py):

| Constant | Default | Purpose |
|----------|---------|---------|
| `MAX_CHARS` | `6000` | Max characters sent to LLM |
