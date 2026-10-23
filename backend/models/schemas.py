"""
Pydantic schemas for EduVerify AI backend.

These models define the data contract between the backend and the frontend.
All fields are serialised to/from JSON by FastAPI automatically.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ReviewStatus(str, Enum):
    """Human-review state of an application."""

    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class DocumentStatus(str, Enum):
    """Whether a required document has been submitted."""

    PRESENT = "present"
    MISSING = "missing"
    UNREADABLE = "unreadable"


class EligibilityOutcome(str, Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    REQUIRES_REVIEW = "requires_review"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class AcademicRecord(BaseModel):
    """Extracted (or fixture-provided) academic fields for an applicant."""

    institution: str
    degree: str
    field_of_study: str
    graduation_year: int
    cgpa: Optional[float] = Field(
        None,
        description="Cumulative GPA on a 10-point scale, or None if not extractable.",
    )
    percentage: Optional[float] = Field(
        None,
        description="Aggregate percentage, or None if not extractable.",
    )
    backlogs_active: int = Field(
        0,
        description="Number of active (uncleared) backlogs.",
    )
    source_note: str = Field(
        description=(
            "Explains how this data was obtained. "
            "Must clearly state when data comes from a fixture, "
            "not from OCR or trusted-source verification."
        )
    )


class DocumentRecord(BaseModel):
    """Status of a single required supporting document."""

    name: str
    status: DocumentStatus
    note: Optional[str] = None


class RuleResult(BaseModel):
    """Result of evaluating one eligibility rule against an applicant."""

    rule_id: str = Field(description="Machine-readable rule identifier.")
    description: str = Field(description="Human-readable rule description.")
    passed: bool
    evidence: str = Field(
        description=(
            "Specific values and reasoning that led to this outcome. "
            "Must reference actual extracted fields, not fabricated confidence scores."
        )
    )


class EligibilityResult(BaseModel):
    """Aggregate eligibility assessment for one application."""

    application_id: str
    outcome: EligibilityOutcome
    rules: list[RuleResult]
    summary: str = Field(
        description="Plain-language summary of why the outcome was reached."
    )


# ---------------------------------------------------------------------------
# Core application model
# ---------------------------------------------------------------------------


class Application(BaseModel):
    """A single student application in the admissions pipeline."""

    id: str
    applicant_name: str
    email: str
    programme_applied: str
    academic_record: AcademicRecord
    documents: list[DocumentRecord]
    review_status: ReviewStatus
    submitted_at: str = Field(description="ISO-8601 date string (YYYY-MM-DD).")
    data_source: str = Field(
        default="fixture",
        description=(
            "Origin of this application record. "
            "'fixture' means synthetic test data created for development. "
            "Never use 'ocr' or 'verified' unless real extraction has occurred."
        ),
    )


class ApplicationSummary(BaseModel):
    """Lightweight row used in the application listing table."""

    id: str
    applicant_name: str
    programme_applied: str
    review_status: ReviewStatus
    submitted_at: str
    eligibility_outcome: Optional[EligibilityOutcome] = None
    data_source: str


# ---------------------------------------------------------------------------
# API response wrappers
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    version: str


class ApplicationListResponse(BaseModel):
    count: int
    items: list[ApplicationSummary]


class ApplicationDetailResponse(BaseModel):
    application: Application
    eligibility: EligibilityResult
