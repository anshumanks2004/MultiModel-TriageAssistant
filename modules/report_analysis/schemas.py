"""Pydantic schemas for medical report analysis output."""

from typing import Literal

from pydantic import BaseModel, Field


class KeyFinding(BaseModel):
    parameter: str = Field(description="Lab parameter or clinical observation name")
    value: str = Field(description="Reported value with units")
    status: Literal["normal", "abnormal", "critical"] = Field(
        description="Interpretation relative to reference range"
    )
    reference_range: str = Field(default="", description="Normal reference range if available")


class RiskIndicator(BaseModel):
    name: str = Field(description="Name of the risk or condition")
    severity: Literal["Low", "Medium", "High"] = Field(description="Severity level")
    rationale: str = Field(description="Brief clinical rationale from report values")


class Recommendation(BaseModel):
    action: str = Field(description="Specific actionable recommendation")
    priority: Literal["Routine", "Soon", "Urgent"] = Field(
        description="Time-sensitivity of the action"
    )


class DoctorConsultation(BaseModel):
    required: bool = Field(description="Whether doctor consultation is needed")
    urgency: Literal["Routine (within 1-2 weeks)", "Soon (within 2-3 days)", "Urgent (within 24 hours)", "EMERGENCY"] = Field(
        description="Urgency of consultation"
    )
    specialties: list[str] = Field(
        default_factory=list,
        description="Relevant medical specialties to consult",
    )
    reason: str = Field(description="Summary reason for consultation")


class MedicalReportResult(BaseModel):
    report_type: str = Field(description="Type of medical report, e.g. 'Complete Blood Count'")
    summary: str = Field(description="One-paragraph plain-language summary of the report")
    key_findings: list[KeyFinding] = Field(default_factory=list)
    risk_indicators: list[RiskIndicator] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    doctor_consultation: DoctorConsultation
    disclaimer: str = Field(
        default=(
            "This analysis is AI-generated for informational purposes only. "
            "It is not a substitute for professional medical advice, diagnosis, or treatment."
        )
    )
