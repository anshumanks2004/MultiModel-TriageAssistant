"""Pydantic schemas for Symptom Analysis input and output.

These models are the contracts between the UI, the analyzer,
and the LLM response parser. Any field mismatch is caught here
before it reaches the UI.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ── Input ─────────────────────────────────────────────────────────────────────

class SymptomInput(BaseModel):
    """Validated user-facing input for symptom analysis."""

    symptoms: str = Field(..., min_length=10, max_length=2000)
    age: Optional[str] = Field(default="Not specified")
    sex: Optional[str] = Field(default="Not specified")
    duration: Optional[str] = Field(default="Not specified")
    intensity: Optional[int] = Field(default=3, ge=1, le=5)

    @field_validator("symptoms")
    @classmethod
    def symptoms_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Symptoms text cannot be empty.")
        return stripped


# ── Output sub-models ─────────────────────────────────────────────────────────

class PossibleCondition(BaseModel):
    """A single candidate condition returned by the LLM."""

    name: str
    likelihood: Literal["Low", "Moderate", "High"]
    brief_explanation: str


class SymptomResult(BaseModel):
    """Full structured result from symptom analysis."""

    possible_conditions: list[PossibleCondition]
    severity_level: Literal["Low", "Medium", "High"]
    severity_reasoning: str
    recommendations: list[str]
    consultation_urgency: str
    urgency_reasoning: str
    confidence_level: Literal["Low", "Moderate", "High"]
    confidence_reasoning: str
    disclaimer: str

    # Runtime-injected fields (not from LLM JSON)
    emergency_detected: bool = False
    emergency_keywords: list[str] = Field(default_factory=list)
