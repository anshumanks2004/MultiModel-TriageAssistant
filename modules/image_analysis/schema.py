"""Pydantic schemas for Image Analysis input and output.

ImageInput  — validated user-facing input (image bytes + context)
ImageMeta   — technical metadata produced by the preprocessor
ImageResult — full structured result returned to the UI
"""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ── Supported image types (user-selectable context hint) ──────────────────────

IMAGE_TYPES: list[str] = [
    "Not specified",
    "Skin Rash",
    "Wound / Laceration",
    "Burn",
    "Swelling / Edema",
    "Bruise / Contusion",
    "Skin Lesion",
    "Eye Condition",
    "Other",
]

# Accepted MIME types → Pillow format names
ALLOWED_MIME_TYPES: dict[str, str] = {
    "image/jpeg": "JPEG",
    "image/jpg":  "JPEG",
    "image/png":  "PNG",
    "image/bmp":  "BMP",
    "image/webp": "WEBP",
}

ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

MAX_IMAGE_BYTES = 10 * 1024 * 1024   # 10 MB
MIN_DIMENSION_PX = 100               # too small to be useful
MAX_DIMENSION_PX = 1344              # LLaVA optimal upper bound


# ── Input ─────────────────────────────────────────────────────────────────────

class ImageInput(BaseModel):
    """Validated input for image analysis."""

    image_bytes: bytes = Field(..., description="Raw image file bytes from uploader")
    image_type: str = Field(default="Not specified")
    filename: str = Field(default="upload")
    user_context: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional free-text context provided by the user",
    )

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("image_bytes")
    @classmethod
    def validate_size(cls, v: bytes) -> bytes:
        if len(v) == 0:
            raise ValueError("Image file is empty.")
        if len(v) > MAX_IMAGE_BYTES:
            mb = len(v) / (1024 * 1024)
            raise ValueError(f"Image is too large ({mb:.1f} MB). Maximum is 10 MB.")
        return v

    @field_validator("image_type")
    @classmethod
    def validate_image_type(cls, v: str) -> str:
        if v not in IMAGE_TYPES:
            return "Not specified"
        return v


# ── Preprocessor output ───────────────────────────────────────────────────────

class ImageMeta(BaseModel):
    """Technical metadata about the image after preprocessing."""

    original_width: int
    original_height: int
    processed_width: int
    processed_height: int
    original_format: str          # e.g. "JPEG", "PNG"
    original_size_kb: float
    processed_size_kb: float
    was_resized: bool
    base64_encoded: str           # the payload sent to LLaVA


# ── LLM output sub-models ─────────────────────────────────────────────────────

class VisualFinding(BaseModel):
    """A single discrete visual observation."""

    observation: str
    location: Optional[str] = None        # e.g. "upper-left quadrant"
    significance: Literal["Low", "Moderate", "High"] = "Moderate"


class PossibleCondition(BaseModel):
    name: str
    likelihood: Literal["Low", "Moderate", "High"]
    brief_explanation: str


class ImageResult(BaseModel):
    """Complete structured output from image analysis."""

    # Visual description
    visual_findings: str
    structured_findings: list[VisualFinding] = Field(default_factory=list)

    # Differential / possible conditions
    possible_conditions: list[PossibleCondition]

    # Risk assessment
    severity_level: Literal["Low", "Medium", "High"]
    severity_reasoning: str
    seek_immediate_care: bool

    # Recommendations
    recommendations: list[str]
    consultation_urgency: str

    # Confidence and limitations
    confidence_level: Literal["Low", "Moderate", "High"]
    confidence_reasoning: str
    image_quality_note: Optional[str] = None

    # Always-present disclaimer
    disclaimer: str

    # Runtime-injected fields (not from LLM JSON)
    emergency_detected: bool = False
    emergency_keywords: list[str] = Field(default_factory=list)
    image_meta: Optional[ImageMeta] = None
