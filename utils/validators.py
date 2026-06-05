"""Input validation for all user-facing entry points.

All validation happens here — modules receive clean, validated data.
"""

from config.settings import (
    MAX_SYMPTOM_TEXT_LENGTH,
    MIN_SYMPTOM_TEXT_LENGTH,
)


class ValidationError(Exception):
    """User-facing validation error with a readable message."""


def validate_symptom_text(text: str) -> str:
    """Validate and clean raw symptom text from UI.

    Returns the stripped text.
    Raises ValidationError with a UI-ready message on failure.
    """
    if not text or not text.strip():
        raise ValidationError("Please describe your symptoms before analyzing.")

    stripped = text.strip()

    if len(stripped) < MIN_SYMPTOM_TEXT_LENGTH:
        raise ValidationError(
            f"Please provide more detail about your symptoms (at least {MIN_SYMPTOM_TEXT_LENGTH} characters)."
        )

    if len(stripped) > MAX_SYMPTOM_TEXT_LENGTH:
        raise ValidationError(
            f"Symptom description is too long. Please limit to {MAX_SYMPTOM_TEXT_LENGTH} characters."
        )

    return stripped


def validate_age(age_str: str) -> str:
    """Validate optional age input. Returns 'Not specified' if empty."""
    if not age_str or not age_str.strip():
        return "Not specified"
    stripped = age_str.strip()
    try:
        age = int(stripped)
        if age < 0 or age > 130:
            raise ValidationError("Please enter a valid age (0–130).")
    except ValueError:
        raise ValidationError("Age must be a number.")
    return stripped


def validate_intensity(value: int) -> int:
    """Ensure intensity is within 1–5."""
    if not isinstance(value, int) or value < 1 or value > 5:
        raise ValidationError("Intensity must be between 1 and 5.")
    return value
