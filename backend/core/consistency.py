"""
Deterministic cross-document consistency checks for EduVerify AI.

This module is independent of eligibility. It compares application-level
fields with optional fixture-authored extracted fields on documents.

Statuses
--------
* consistent   — both sides present and equal after normalisation.
* mismatch     — both sides present and differ after normalisation.
* inconclusive — a side is missing, the document is missing/unreadable,
                 or no extracted field was provided.

String comparison ignores case and collapses internal whitespace.
Numeric comparison uses the values as given (CGPA rounded to 2 d.p.).

These checks are not authenticity verification and are not OCR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from backend.models.schemas import (
    Application,
    ConsistencyFinding,
    ConsistencyResult,
    ConsistencyStatus,
    DocumentStatus,
)


def _stringify(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _normalize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return " ".join(value.split()).casefold()
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, int):
        return value
    return value


def _document_field(app: Application, document_name: str, field_name: str) -> tuple[Any, str]:
    """
    Return (value, reason_if_unavailable).

    reason_if_unavailable is empty when a value was read.
    """
    doc = next((d for d in app.documents if d.name == document_name), None)
    if doc is None:
        return None, f"Document '{document_name}' is not on the application."
    if doc.status == DocumentStatus.MISSING:
        return None, f"Document '{document_name}' is missing."
    if doc.status == DocumentStatus.UNREADABLE:
        return None, f"Document '{document_name}' is unreadable."
    if doc.extracted_fields is None:
        return None, (
            f"Document '{document_name}' has no fixture-authored extracted fields."
        )
    value = getattr(doc.extracted_fields, field_name, None)
    if value is None:
        return None, (
            f"Document '{document_name}' has no extracted value for '{field_name}'."
        )
    return value, ""


@dataclass(frozen=True)
class _Comparison:
    finding_id: str
    field: str
    left_source: str
    right_source: str
    document_name: str
    document_field: str
    left_getter: Callable[[Application], Any]


_COMPARISONS: tuple[_Comparison, ...] = (
    _Comparison(
        finding_id="C01",
        field="applicant_name",
        left_source="application.applicant_name",
        right_source="documents['Aadhar Card'].extracted_fields.applicant_name",
        document_name="Aadhar Card",
        document_field="applicant_name",
        left_getter=lambda app: app.applicant_name,
    ),
    _Comparison(
        finding_id="C02",
        field="applicant_name",
        left_source="application.applicant_name",
        right_source=(
            "documents['Undergraduate Degree Certificate'].extracted_fields.applicant_name"
        ),
        document_name="Undergraduate Degree Certificate",
        document_field="applicant_name",
        left_getter=lambda app: app.applicant_name,
    ),
    _Comparison(
        finding_id="C03",
        field="cgpa",
        left_source="application.academic_record.cgpa",
        right_source=(
            "documents['Undergraduate Consolidated Marks Card'].extracted_fields.cgpa"
        ),
        document_name="Undergraduate Consolidated Marks Card",
        document_field="cgpa",
        left_getter=lambda app: app.academic_record.cgpa,
    ),
    _Comparison(
        finding_id="C04",
        field="institution",
        left_source="application.academic_record.institution",
        right_source=(
            "documents['Undergraduate Degree Certificate'].extracted_fields.institution"
        ),
        document_name="Undergraduate Degree Certificate",
        document_field="institution",
        left_getter=lambda app: app.academic_record.institution,
    ),
)


def _evaluate_comparison(app: Application, spec: _Comparison) -> ConsistencyFinding:
    left = spec.left_getter(app)
    right, right_reason = _document_field(app, spec.document_name, spec.document_field)

    if left is None or right is None:
        reasons: list[str] = []
        if left is None:
            reasons.append(f"{spec.left_source} is not available.")
        if right is None:
            reasons.append(right_reason or f"{spec.right_source} is not available.")
        return ConsistencyFinding(
            finding_id=spec.finding_id,
            field=spec.field,
            left_source=spec.left_source,
            right_source=spec.right_source,
            left_value=_stringify(left),
            right_value=_stringify(right),
            status=ConsistencyStatus.INCONCLUSIVE,
            evidence=" ".join(reasons),
        )

    if _normalize(left) == _normalize(right):
        return ConsistencyFinding(
            finding_id=spec.finding_id,
            field=spec.field,
            left_source=spec.left_source,
            right_source=spec.right_source,
            left_value=_stringify(left),
            right_value=_stringify(right),
            status=ConsistencyStatus.CONSISTENT,
            evidence=(
                f"{spec.field}: application value '{left}' matches "
                f"document value '{right}' after normalisation."
            ),
        )

    return ConsistencyFinding(
        finding_id=spec.finding_id,
        field=spec.field,
        left_source=spec.left_source,
        right_source=spec.right_source,
        left_value=_stringify(left),
        right_value=_stringify(right),
        status=ConsistencyStatus.MISMATCH,
        evidence=(
            f"{spec.field}: application value '{left}' does not match "
            f"document value '{right}' after normalisation."
        ),
    )


def evaluate_consistency(app: Application) -> ConsistencyResult:
    """
    Compare selected application fields with fixture-authored document fields.

    Does not affect eligibility. Does not claim document authenticity.
    """
    findings = [_evaluate_comparison(app, spec) for spec in _COMPARISONS]
    mismatches = [f for f in findings if f.status == ConsistencyStatus.MISMATCH]
    inconclusive = [f for f in findings if f.status == ConsistencyStatus.INCONCLUSIVE]

    if mismatches:
        status = ConsistencyStatus.MISMATCH
        ids = ", ".join(f.finding_id for f in mismatches)
        summary = (
            "One or more compared fields differ across documents. "
            f"Mismatch finding(s): {ids}. "
            "This is a consistency result only; it is not an authenticity judgement."
        )
    elif inconclusive:
        status = ConsistencyStatus.INCONCLUSIVE
        ids = ", ".join(f.finding_id for f in inconclusive)
        summary = (
            "One or more comparisons cannot be completed from the available "
            f"fixture fields. Inconclusive finding(s): {ids}."
        )
    else:
        status = ConsistencyStatus.CONSISTENT
        summary = (
            "Compared application and document fields match after normalisation. "
            "This is a consistency result only; it is not an authenticity judgement."
        )

    return ConsistencyResult(
        application_id=app.id,
        status=status,
        findings=findings,
        summary=summary,
    )
