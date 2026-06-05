"""PDF text extraction: PyMuPDF first, EasyOCR fallback for image-only pages.

Strategy per page:
1. PyMuPDF attempts native text extraction (fast, layout-aware).
2. If a page yields fewer than MIN_CHARS_NATIVE characters (scanned/image page),
   render it to a pixel buffer and run EasyOCR on that buffer.

EasyOCR reader is initialized once and reused (model load is expensive).
"""

import logging
from io import BytesIO
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

MIN_CHARS_NATIVE = 30  # below this threshold, treat page as image-only
OCR_DPI = 200          # render DPI for EasyOCR; 200 is a good speed/accuracy balance

# Lazy-loaded EasyOCR reader — imported only when an image page is encountered.
_ocr_reader: Optional[object] = None


def _get_ocr_reader():
    """Return a cached EasyOCR Reader instance, loading it on first call."""
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(
                "easyocr is required for scanned PDF pages. "
                "Install it with: pip install easyocr"
            ) from exc
        logger.info("Initializing EasyOCR reader (first-time load, may take a moment)...")
        _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        logger.info("EasyOCR reader ready.")
    return _ocr_reader


def _render_page_to_bytes(page: fitz.Page, dpi: int = OCR_DPI) -> bytes:
    """Render a PyMuPDF page to PNG bytes at the given DPI."""
    zoom = dpi / 72  # PyMuPDF default is 72 DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
    return pix.tobytes("png")


def _ocr_page(page: fitz.Page) -> str:
    """Run EasyOCR on a rendered page image and return joined text."""
    reader = _get_ocr_reader()
    img_bytes = _render_page_to_bytes(page)
    results = reader.readtext(img_bytes, detail=0, paragraph=True)
    return "\n".join(results)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract all text from a PDF, using OCR for image-only pages.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages, separated by form-feed characters.

    Raises:
        FileNotFoundError: if the PDF does not exist.
        RuntimeError: if the file cannot be opened as a PDF.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        raise RuntimeError(f"Cannot open PDF '{pdf_path}': {exc}") from exc

    page_texts: list[str] = []
    ocr_pages: list[int] = []

    with doc:
        for page_num, page in enumerate(doc, start=1):
            native_text = page.get_text("text").strip()
            if len(native_text) >= MIN_CHARS_NATIVE:
                logger.debug("Page %d: native extraction (%d chars)", page_num, len(native_text))
                page_texts.append(native_text)
            else:
                logger.debug("Page %d: falling back to EasyOCR", page_num)
                ocr_pages.append(page_num)
                ocr_text = _ocr_page(page)
                page_texts.append(ocr_text)

    if ocr_pages:
        logger.info("OCR used on pages: %s", ocr_pages)

    return "\f".join(page_texts)
