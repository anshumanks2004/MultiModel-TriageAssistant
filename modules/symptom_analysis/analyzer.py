"""Symptom Analysis pipeline.

Data flow:
    SymptomInput
        → emergency_detector  (fast keyword scan, pre-LLM)
        → prompt builder      (fills SYMPTOM_USER_PROMPT template)
        → ollama_client       (Llama3 text inference)
        → response_parser     (JSON extraction + Pydantic validation)
        → SymptomResult       (returned to UI)

Never imports from UI layer — direction of dependency is one-way.
"""

import logging

from config.prompts import SYMPTOM_SYSTEM_PROMPT, SYMPTOM_USER_PROMPT
from config.settings import SEVERITY_HIGH, URGENCY_EMERGENCY
from core.emergency_detector import is_emergency
from core.ollama_client import OllamaClientError, generate_text
from core.response_parser import parse_llm_response
from modules.symptom_analysis.schema import SymptomInput, SymptomResult

logger = logging.getLogger(__name__)


class SymptomAnalysisError(Exception):
    """Raised when the analysis pipeline fails unrecoverably."""


def analyze_symptoms(symptom_input: SymptomInput) -> SymptomResult:
    """Run the full symptom analysis pipeline.

    Args:
        symptom_input: Validated SymptomInput from the UI layer.

    Returns:
        SymptomResult with all fields populated.

    Raises:
        SymptomAnalysisError: on LLM or parsing failure.
    """
    # ── Step 1: Fast emergency pre-scan ───────────────────────────────────────
    emergency_triggered, matched_keywords = is_emergency(symptom_input.symptoms)
    logger.info(
        "Emergency scan complete: triggered=%s keywords=%s",
        emergency_triggered,
        matched_keywords,
    )

    # ── Step 2: Build the user prompt ─────────────────────────────────────────
    user_prompt = SYMPTOM_USER_PROMPT.format(
        age=symptom_input.age or "Not specified",
        sex=symptom_input.sex or "Not specified",
        symptoms=symptom_input.symptoms,
        duration=symptom_input.duration or "Not specified",
        intensity=symptom_input.intensity or 3,
    )

    # ── Step 3: Call Llama3 via Ollama ────────────────────────────────────────
    logger.info("Sending symptom analysis request to Llama3")
    try:
        raw_response = generate_text(
            system_prompt=SYMPTOM_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
    except OllamaClientError as exc:
        raise SymptomAnalysisError(
            f"Could not reach the AI model. Please ensure Ollama is running. Details: {exc}"
        ) from exc

    # ── Step 4: Parse and validate JSON response ──────────────────────────────
    logger.info("Parsing LLM response")
    try:
        result = parse_llm_response(raw_response, SymptomResult)
    except ValueError as exc:
        raise SymptomAnalysisError(
            f"AI model returned an unexpected response format. Please try again. Details: {exc}"
        ) from exc

    # ── Step 5: Inject emergency context into result ──────────────────────────
    result.emergency_detected = emergency_triggered
    result.emergency_keywords = matched_keywords

    # If emergency was detected, force severity to High regardless of LLM output
    if emergency_triggered:
        result.severity_level = SEVERITY_HIGH
        result.consultation_urgency = URGENCY_EMERGENCY
        logger.warning("Emergency override applied: severity=High, urgency=EMERGENCY")

    logger.info(
        "Symptom analysis complete: severity=%s urgency=%s",
        result.severity_level,
        result.consultation_urgency,
    )
    return result
