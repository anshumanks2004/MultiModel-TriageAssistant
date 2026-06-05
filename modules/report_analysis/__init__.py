"""Medical Report Analysis module.

Pipeline:
    PDF → PyMuPDF text extraction → EasyOCR fallback for scanned pages
         → text cleaning → Ollama Llama3 analysis → structured output

Public surface:
    analyze_report(pdf_path) -> MedicalReportResult
"""

from .analyzer import analyze_report
from .schemas import MedicalReportResult

__all__ = ["analyze_report", "MedicalReportResult"]
