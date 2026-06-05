"""Prompt templates for Ollama Llama3 medical report analysis.

Design principles:
- System prompt establishes role, output contract, and safety guardrails.
- User prompt injects the cleaned report text and the exact JSON schema.
- Temperature is kept at 0.1 to favour deterministic, factual output.
- The schema is embedded in the prompt so the model can self-validate.
"""

SYSTEM_PROMPT = """\
You are a clinical decision-support assistant. Your job is to analyse \
the text of a medical lab or diagnostic report and return a structured \
JSON summary for a non-specialist patient audience.

Rules you MUST follow:
1. Output ONLY valid JSON — no preamble, no markdown fences, no commentary.
2. Never invent values not present in the report text.
3. Use plain language in the `summary` and `rationale` fields; avoid jargon.
4. Always include the disclaimer field verbatim.
5. If a field cannot be determined from the report, use an empty string or \
   empty list — never omit required fields.
6. Severity and urgency must use only the exact string literals defined in \
   the schema; do not paraphrase them.
"""

_SCHEMA_BLOCK = """\
{
  "report_type": "<string: type of report, e.g. 'Complete Blood Count'>",
  "summary": "<string: 2-4 sentence plain-language summary>",
  "key_findings": [
    {
      "parameter": "<string>",
      "value": "<string with units>",
      "status": "<'normal' | 'abnormal' | 'critical'>",
      "reference_range": "<string or empty>"
    }
  ],
  "risk_indicators": [
    {
      "name": "<string>",
      "severity": "<'Low' | 'Medium' | 'High'>",
      "rationale": "<string>"
    }
  ],
  "recommendations": [
    {
      "action": "<string>",
      "priority": "<'Routine' | 'Soon' | 'Urgent'>"
    }
  ],
  "doctor_consultation": {
    "required": <true | false>,
    "urgency": "<'Routine (within 1-2 weeks)' | 'Soon (within 2-3 days)' | 'Urgent (within 24 hours)' | 'EMERGENCY'>",
    "specialties": ["<string>"],
    "reason": "<string>"
  },
  "disclaimer": "This analysis is AI-generated for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment."
}"""


def build_user_prompt(cleaned_report_text: str) -> str:
    """Construct the user-turn prompt from cleaned report text.

    The schema is embedded directly so Llama3 can map each field without
    needing a second round-trip.
    """
    return f"""\
Analyse the following medical report and return a JSON object that \
strictly matches the schema below.

=== REPORT TEXT ===
{cleaned_report_text}

=== REQUIRED JSON SCHEMA ===
{_SCHEMA_BLOCK}

Return the JSON object only. Do not include any text before or after it.
"""
