"""Top-level orchestrator: PDF → clean text → LLM → MedicalReportResult.

This is the single public entry point consumed by the Streamlit UI and
any other callers. All sub-steps are isolated in their own modules so
they can be tested or swapped independently.
"""

import logging
from pathlib import Path

from config.settings import MAX_REPORT_FILE_SIZE_MB
from core.ollama_client import OllamaClientError, generate_text
from core.response_parser import parse_llm_response

from .cleaner import clean_extracted_text
from .extractor import extract_text_from_pdf
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .schemas import MedicalReportResult

logger = logging.getLogger(__name__)

_MAX_BYTES = MAX_REPORT_FILE_SIZE_MB * 1024 * 1024


def _validate_pdf_path(pdf_path: Path) -> None:
    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")
    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {pdf_path.suffix}")
    size = pdf_path.stat().st_size
    if size > _MAX_BYTES:
        raise ValueError(
            f"File size {size / 1_048_576:.1f} MB exceeds the "
            f"{MAX_REPORT_FILE_SIZE_MB} MB limit."
        )


def analyze_report(pdf_path: str | Path) -> MedicalReportResult:
    """Analyse a medical PDF report and return structured findings.

    Steps:
        1. Validate the file.
        2. Extract text via PyMuPDF + EasyOCR fallback.
        3. Clean and truncate the text.
        4. Send to Ollama Llama3 with an engineered prompt.
        5. Parse and validate the JSON response into MedicalReportResult.

    Args:
        pdf_path: Path to the PDF medical report.

    Returns:
        MedicalReportResult — fully validated structured output.

    Raises:
        FileNotFoundError: PDF does not exist.
        ValueError: File is not a PDF, oversized, or LLM output is malformed.
        OllamaClientError: Ollama is unreachable or returned an error.
    """
    pdf_path = Path(pdf_path)
    logger.info("Starting medical report analysis: %s", pdf_path.name)

    # Step 1 — validate
    _validate_pdf_path(pdf_path)

    # Step 2 — extract
    logger.info("Extracting text from PDF...")
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text.strip():
        raise ValueError("No text could be extracted from the PDF.")
    logger.info("Extracted %d characters of raw text.", len(raw_text))

    # Step 3 — clean
    clean_text = clean_extracted_text(raw_text)
    logger.info("Cleaned text: %d characters.", len(clean_text))

    # Step 4 — analyse
    logger.info("Sending report to Ollama Llama3 for analysis...")
    user_prompt = build_user_prompt(clean_text)
    try:
        raw_response = generate_text(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
        )
    except OllamaClientError as exc:
        logger.error("Ollama inference failed: %s", exc)
        raise

    # Step 5 — parse
    logger.info("Parsing LLM response...")
    result = parse_llm_response(raw_response, MedicalReportResult)
    logger.info("Analysis complete. Report type: %s", result.report_type)
    return result
