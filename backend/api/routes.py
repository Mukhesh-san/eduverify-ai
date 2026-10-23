"""
API routes for EduVerify AI — Milestone 1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.core.consistency import evaluate_consistency
from backend.core.eligibility import evaluate_eligibility
from backend.data.fixtures import APPLICATION_INDEX, APPLICATIONS
from backend.models.schemas import (
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationSummary,
    HealthResponse,
)

router = APIRouter()

_API_VERSION = "0.1.0-milestone1"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    """Return API health status. Used by the frontend to confirm connectivity."""
    return HealthResponse(status="ok", version=_API_VERSION)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------


@router.get("/applications", response_model=ApplicationListResponse, tags=["applications"])
def list_applications() -> ApplicationListResponse:
    """
    Return a summary list of all applications.

    Eligibility is evaluated and included in each summary row so that the
    application table can show the outcome without a separate request.
    """
    items: list[ApplicationSummary] = []
    for app in APPLICATIONS:
        eligibility = evaluate_eligibility(app)
        items.append(
            ApplicationSummary(
                id=app.id,
                applicant_name=app.applicant_name,
                programme_applied=app.programme_applied,
                review_status=app.review_status,
                submitted_at=app.submitted_at,
                eligibility_outcome=eligibility.outcome,
                data_source=app.data_source,
            )
        )
    return ApplicationListResponse(count=len(items), items=items)


@router.get(
    "/applications/{application_id}",
    response_model=ApplicationDetailResponse,
    tags=["applications"],
)
def get_application(application_id: str) -> ApplicationDetailResponse:
    """
    Return full detail for a single application including eligibility and
    consistency results.

    Returns 404 if the application ID is not found.
    """
    app = APPLICATION_INDEX.get(application_id)
    if app is None:
        raise HTTPException(
            status_code=404,
            detail=f"Application '{application_id}' not found.",
        )
    eligibility = evaluate_eligibility(app)
    consistency = evaluate_consistency(app)
    return ApplicationDetailResponse(
        application=app,
        eligibility=eligibility,
        consistency=consistency,
    )
