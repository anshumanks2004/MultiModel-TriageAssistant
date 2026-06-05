"""Medical Image Analysis pipeline.

Data flow:
    ImageInput (bytes + context)
        → preprocessor.preprocess_image()   validate + resize + base64 encode
        → emergency_detector.detect_emergency()   pre-LLM fast scan on context
        → build_prompt()                    fill IMAGE_USER_PROMPT + type suffix
        → ollama_client.generate_vision()   LLaVA multimodal inference
        → response_parser.parse_llm_response()   JSON → ImageResult (Pydantic)
        → inject emergency context + ImageMeta
        → ImageResult returned to UI

This module never imports from the UI layer.
"""

from __future__ import annotations

import logging

from config.prompts import IMAGE_SYSTEM_PROMPT, IMAGE_TYPE_FOCUS, IMAGE_USER_PROMPT
from config.settings import SEVERITY_HIGH, URGENCY_EMERGENCY
from core.emergency_detector import detect_emergency
from core.ollama_client import OllamaClientError, generate_vision
from core.response_parser import parse_llm_response
from modules.image_analysis.preprocessor import ImagePreprocessError, preprocess_image
from modules.image_analysis.schema import ImageInput, ImageMeta, ImageResult

logger = logging.getLogger(__name__)


class ImageAnalysisError(Exception):
    """Raised when the image analysis pipeline fails unrecoverably."""


def _build_user_prompt(image_type: str, user_context: str | None) -> str:
    """Fill the IMAGE_USER_PROMPT template and optionally append type-specific focus."""
    context_text = user_context.strip() if user_context else "None provided"
    base_prompt = IMAGE_USER_PROMPT.format(
        image_type=image_type,
        user_context=context_text,
    )
    focus = IMAGE_TYPE_FOCUS.get(image_type, "")
    if focus:
        base_prompt = f"{base_prompt}\n\nAdditional assessment focus:\n{focus}"
    return base_prompt


def analyze_image(image_input: ImageInput) -> ImageResult:
    """Run the full image analysis pipeline.

    Args:
        image_input: Validated ImageInput from the UI layer.

    Returns:
        ImageResult with all fields populated.

    Raises:
        ImageAnalysisError: on preprocessing, LLM, or parsing failure.
        ImagePreprocessError: propagated if the image itself is invalid (shown in UI).
    """
    # ── Step 1: Preprocess image ───────────────────────────────────────────────
    logger.info("Starting image preprocessing: %s", image_input.filename)
    # Let ImagePreprocessError propagate — the UI catches it and shows the message.
    meta: ImageMeta = preprocess_image(image_input.image_bytes, image_input.filename)

    # ── Step 2: Emergency pre-scan on user-provided context ────────────────────
    scan_text = " ".join(filter(None, [
        image_input.image_type,
        image_input.user_context or "",
    ]))
    emergency_result = detect_emergency(scan_text)
    logger.info(
        "Emergency scan: level=%s  categories=%s",
        emergency_result.level.value,
        emergency_result.triggered_categories,
    )

    # ── Step 3: Build prompt ───────────────────────────────────────────────────
    user_prompt = _build_user_prompt(image_input.image_type, image_input.user_context)

    # ── Step 4: Call LLaVA ────────────────────────────────────────────────────
    logger.info(
        "Sending image to LLaVA: %dx%d px  %.1f KB",
        meta.processed_width,
        meta.processed_height,
        meta.processed_size_kb,
    )
    try:
        raw_response = generate_vision(
            system_prompt=IMAGE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            image_base64=meta.base64_encoded,
        )
    except OllamaClientError as exc:
        raise ImageAnalysisError(
            f"Could not reach the AI vision model. "
            f"Please ensure Ollama is running and LLaVA is installed. Details: {exc}"
        ) from exc

    # ── Step 5: Parse and validate ─────────────────────────────────────────────
    logger.info("Parsing LLaVA response")
    try:
        result: ImageResult = parse_llm_response(raw_response, ImageResult)
    except ValueError as exc:
        raise ImageAnalysisError(
            f"AI vision model returned an unexpected response format. "
            f"Please try again. Details: {exc}"
        ) from exc

    # ── Step 6: Inject runtime context ────────────────────────────────────────
    result.image_meta = meta
    result.emergency_detected = emergency_result.is_emergency
    result.emergency_keywords = emergency_result.matched_phrases

    # If context triggered an emergency, force severity up
    if emergency_result.requires_911:
        result.severity_level = SEVERITY_HIGH
        result.seek_immediate_care = True
        result.consultation_urgency = URGENCY_EMERGENCY
        logger.warning("Emergency override applied to image result")

    logger.info(
        "Image analysis complete: severity=%s urgency=%s confidence=%s",
        result.severity_level,
        result.consultation_urgency,
        result.confidence_level,
    )
    return result
