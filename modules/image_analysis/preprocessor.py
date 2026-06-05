"""Image preprocessing pipeline for LLaVA compatibility.

Steps:
1. Decode bytes → Pillow Image
2. Validate minimum dimensions
3. Convert colour mode to RGB
4. Strip EXIF metadata (privacy + size reduction)
5. Resize to LLaVA's optimal resolution ceiling (1344 px on longest edge)
6. Re-encode to JPEG at quality=85
7. Base64-encode the final bytes
8. Return ImageMeta with all measurements

All processing is in-memory; no files are written to disk.
"""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from modules.image_analysis.schema import (
    ALLOWED_EXTENSIONS,
    MAX_DIMENSION_PX,
    MIN_DIMENSION_PX,
    ImageMeta,
)

logger = logging.getLogger(__name__)


class ImagePreprocessError(Exception):
    """User-facing error from preprocessing — message is shown in the UI."""


def _validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ImagePreprocessError(
            f"Unsupported file type '{ext}'. "
            f"Accepted formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )


def _decode_image(image_bytes: bytes, filename: str) -> Image.Image:
    """Decode raw bytes into a Pillow Image object."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()                    # detect truncated / corrupt files
    except UnidentifiedImageError:
        raise ImagePreprocessError("The uploaded file is not a valid image.")
    except Exception as exc:
        raise ImagePreprocessError(f"Could not open image: {exc}") from exc

    # Re-open after verify() (verify() closes the file handle)
    img = Image.open(io.BytesIO(image_bytes))
    return img


def _validate_dimensions(img: Image.Image) -> None:
    w, h = img.size
    if w < MIN_DIMENSION_PX or h < MIN_DIMENSION_PX:
        raise ImagePreprocessError(
            f"Image is too small ({w}×{h} px). "
            f"Minimum useful size is {MIN_DIMENSION_PX}×{MIN_DIMENSION_PX} px."
        )


def _to_rgb(img: Image.Image) -> Image.Image:
    """Convert any colour mode to RGB.

    LLaVA expects plain RGB. RGBA/P/CMYK all fail or produce wrong colours.
    For transparent images (RGBA) we composite on white before converting.
    """
    if img.mode == "RGB":
        return img
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img.convert("RGB"))
        return background
    return img.convert("RGB")


def _strip_exif(img: Image.Image) -> Image.Image:
    """Return a new Image with EXIF stripped by round-tripping through raw pixels."""
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    return clean


def _resize_if_needed(img: Image.Image) -> tuple[Image.Image, bool]:
    """Downsample if the longest edge exceeds MAX_DIMENSION_PX.

    Never upscales — that would degrade quality without helping LLaVA.
    Uses LANCZOS for best downscaling quality.
    """
    w, h = img.size
    if max(w, h) <= MAX_DIMENSION_PX:
        return img, False

    if w >= h:
        new_w = MAX_DIMENSION_PX
        new_h = int(h * MAX_DIMENSION_PX / w)
    else:
        new_h = MAX_DIMENSION_PX
        new_w = int(w * MAX_DIMENSION_PX / h)

    resized = img.resize((new_w, new_h), Image.LANCZOS)
    logger.debug("Resized image from %dx%d to %dx%d", w, h, new_w, new_h)
    return resized, True


def _encode_to_base64(img: Image.Image) -> tuple[str, float]:
    """Encode a PIL Image to a JPEG base64 string.

    Returns (base64_string, processed_size_kb).
    """
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    jpeg_bytes = buffer.getvalue()
    b64 = base64.b64encode(jpeg_bytes).decode("utf-8")
    size_kb = len(jpeg_bytes) / 1024
    return b64, size_kb


# ── Public API ─────────────────────────────────────────────────────────────────

def preprocess_image(image_bytes: bytes, filename: str = "upload") -> ImageMeta:
    """Run the full image preprocessing pipeline.

    Args:
        image_bytes: Raw bytes from st.file_uploader.
        filename:    Original filename (used only for extension validation).

    Returns:
        ImageMeta with base64_encoded payload ready for LLaVA.

    Raises:
        ImagePreprocessError: with a UI-ready message on any failure.
    """
    _validate_extension(filename)

    original_size_kb = len(image_bytes) / 1024
    img = _decode_image(image_bytes, filename)
    original_format = img.format or "UNKNOWN"
    original_w, original_h = img.size

    _validate_dimensions(img)

    img = _to_rgb(img)
    img = _strip_exif(img)
    img, was_resized = _resize_if_needed(img)

    processed_w, processed_h = img.size
    b64, processed_size_kb = _encode_to_base64(img)

    logger.info(
        "Image preprocessed: %s %dx%d → %dx%d  original=%.1f KB  processed=%.1f KB  resized=%s",
        original_format,
        original_w, original_h,
        processed_w, processed_h,
        original_size_kb,
        processed_size_kb,
        was_resized,
    )

    return ImageMeta(
        original_width=original_w,
        original_height=original_h,
        processed_width=processed_w,
        processed_height=processed_h,
        original_format=original_format,
        original_size_kb=round(original_size_kb, 1),
        processed_size_kb=round(processed_size_kb, 1),
        was_resized=was_resized,
        base64_encoded=b64,
    )
