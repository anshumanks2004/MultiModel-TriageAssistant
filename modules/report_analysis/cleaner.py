"""Text cleaning pipeline for raw PDF/OCR output.

Cleaning stages (applied in order):
1. Normalize Unicode and fix common OCR character substitutions.
2. Remove headers/footers (page numbers, clinic name repetitions).
3. Collapse excessive whitespace.
4. Remove non-printable control characters.
5. Truncate to the LLM token budget.

The output is a single clean string ready for prompt injection.
"""

import re
import unicodedata

# Maximum characters sent to the LLM. Llama3-8B context is ~8k tokens;
# 6000 chars is roughly 1500 tokens, leaving room for the prompt itself.
MAX_CHARS = 6000

# OCR often confuses these pairs; correct them in medical numeric contexts.
_OCR_SUBSTITUTIONS = [
    (r"\b0(?=[A-Za-z])", "O"),   # 0 → O before letters (e.g. 0verall → Overall)
    (r"(?<=[A-Za-z])0\b", "O"),  # 0 → O after letters
    (r"\bl(?=\d)", "1"),          # l → 1 before digits (l23 → 123)
    (r"(?<=\d)l\b", "1"),         # l → 1 after digits
    (r"(?<!\d)S(?=\d)", "5"),     # S → 5 in numeric context
]

# Patterns that mark header/footer noise common in medical PDFs.
_NOISE_PATTERNS = [
    re.compile(r"Page\s+\d+\s+of\s+\d+", re.IGNORECASE),
    re.compile(r"\bConfidential\b.*", re.IGNORECASE),
    re.compile(r"^\s*[-–—]{3,}\s*$", re.MULTILINE),  # horizontal rules
    re.compile(r"(?m)^\s*\d+\s*$"),                  # lone page numbers
]


def _normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC and replace fancy punctuation with ASCII."""
    text = unicodedata.normalize("NFC", text)
    # Smart quotes → straight quotes
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    # Em-dash / en-dash → hyphen
    text = text.replace("–", "-").replace("—", "-")
    # Bullet variants → hyphen-space
    text = re.sub(r"[•‣◦⁃]", "- ", text)
    return text


def _fix_ocr_substitutions(text: str) -> str:
    for pattern, replacement in _OCR_SUBSTITUTIONS:
        text = re.sub(pattern, replacement, text)
    return text


def _remove_noise(text: str) -> str:
    for pattern in _NOISE_PATTERNS:
        text = pattern.sub("", text)
    return text


def _collapse_whitespace(text: str) -> str:
    # Replace form-feed (page break) with double newline
    text = text.replace("\f", "\n\n")
    # Collapse runs of blank lines to at most two
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces/tabs to a single space on each line
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _remove_control_chars(text: str) -> str:
    # Remove non-printable characters except newline and tab
    return re.sub(r"[^\x09\x0A\x20-\x7E -￿]", "", text)


def clean_extracted_text(raw_text: str, max_chars: int = MAX_CHARS) -> str:
    """Run the full cleaning pipeline on raw extracted PDF/OCR text.

    Args:
        raw_text: Text as returned by the extractor.
        max_chars: Hard cap on output length (characters).

    Returns:
        Cleaned, truncated text string.
    """
    text = _normalize_unicode(raw_text)
    text = _fix_ocr_substitutions(text)
    text = _remove_noise(text)
    text = _remove_control_chars(text)
    text = _collapse_whitespace(text)

    if len(text) > max_chars:
        # Truncate at a word boundary near the limit
        text = text[:max_chars].rsplit(" ", 1)[0] + " [truncated]"

    return text
