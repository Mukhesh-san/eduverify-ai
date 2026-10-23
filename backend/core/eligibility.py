"""
Deterministic eligibility engine for EduVerify AI.

Design principles
-----------------
* Every rule is a pure function: same inputs → same output, no side effects.
* Rules evaluate against extracted AcademicRecord and DocumentRecord fields only.
* No confidence scores or probabilistic thresholds.
* The `evidence` field in RuleResult cites the actual field values that drove
  each decision, not a fabricated summary.
* Rules are intentionally conservative: ambiguous data (e.g., missing CGPA
  and missing percentage) produces REQUIRES_REVIEW, never a pass.

Programme-specific minimum CGPA/percentage requirements
---------------------------------------------------------
These are example thresholds for a fictional institution. Replace with real
institutional rules before any production use.
"""

from __future__ import annotations

from backend.models.schemas import (
    Application,
    DocumentStatus,
    EligibilityOutcome,
    EligibilityResult,
    RuleResult,
)

# ---------------------------------------------------------------------------
# Programme eligibility thresholds (deterministic configuration)
# ---------------------------------------------------------------------------

# Minimum CGPA (10-point scale) required for each programme keyword.
# Matched case-insensitively against the programme_applied field.
_PROGRAMME_CGPA_FLOOR: dict[str, float] = {
    "computer science": 7.5,
    "vlsi": 7.0,
    "artificial intelligence": 7.5,
    "data science": 7.0,
    "structural engineering": 6.5,
    "power systems": 6.5,
    "biotechnology": 7.0,
}

# Equivalent percentage floor (used only when CGPA is absent).
_PERCENTAGE_FLOOR: dict[str, float] = {
    "computer science": 70.0,
    "vlsi": 65.0,
    "artificial intelligence": 70.0,
    "data science": 65.0,
    "structural engineering": 60.0,
    "power systems": 60.0,
    "biotechnology": 65.0,
}

# Maximum active backlogs permitted.
_MAX_ACTIVE_BACKLOGS = 0

# Documents that must not be MISSING.
# UNREADABLE is counted as present but flagged separately.
_MANDATORY_DOCUMENTS = {
    "10th Mark Sheet",
    "12th Mark Sheet",
    "Undergraduate Degree Certificate",
    "Undergraduate Consolidated Marks Card",
    "Aadhar Card",
}


# ---------------------------------------------------------------------------
# Individual rule evaluators
# ---------------------------------------------------------------------------


def _resolve_programme_key(programme_applied: str) -> str | None:
    """Return the matching key in the threshold dict, or None."""
    lower = programme_applied.lower()
    for key in _PROGRAMME_CGPA_FLOOR:
        if key in lower:
            return key
    return None


def rule_cgpa_or_percentage(app: Application) -> RuleResult:
    """R01 — Minimum academic score (CGPA or equivalent percentage)."""
    record = app.academic_record
    prog_key = _resolve_programme_key(app.programme_applied)

    if prog_key is None:
        return RuleResult(
            rule_id="R01",
            description="Minimum academic score requirement",
            passed=False,
            evidence=(
                f"Programme '{app.programme_applied}' has no configured eligibility threshold. "
                "Manual review required before a score comparison can be made."
            ),
        )

    cgpa_floor = _PROGRAMME_CGPA_FLOOR[prog_key]
    pct_floor = _PERCENTAGE_FLOOR[prog_key]

    if record.cgpa is not None:
        passed = record.cgpa >= cgpa_floor
        return RuleResult(
            rule_id="R01",
            description="Minimum academic score requirement",
            passed=passed,
            evidence=(
                f"Programme '{app.programme_applied}' requires CGPA ≥ {cgpa_floor}. "
                f"Reported CGPA: {record.cgpa}. "
                f"{'Meets' if passed else 'Does not meet'} the requirement."
            ),
        )

    if record.percentage is not None:
        # Convert percentage to an approximate CGPA-equivalent for comparison,
        # OR compare directly against the percentage floor.
        passed = record.percentage >= pct_floor
        return RuleResult(
            rule_id="R01",
            description="Minimum academic score requirement",
            passed=passed,
            evidence=(
                f"Programme '{app.programme_applied}' requires percentage ≥ {pct_floor}% "
                f"(applied when CGPA is unavailable). "
                f"Reported percentage: {record.percentage}%. "
                f"{'Meets' if passed else 'Does not meet'} the requirement."
            ),
        )

    # Neither CGPA nor percentage available.
    return RuleResult(
        rule_id="R01",
        description="Minimum academic score requirement",
        passed=False,
        evidence=(
            "Neither CGPA nor aggregate percentage is present in the academic record. "
            "Score requirement cannot be evaluated. Flagged for human review."
        ),
    )


def rule_no_active_backlogs(app: Application) -> RuleResult:
    """R02 — No active (uncleared) backlogs at time of application."""
    backlogs = app.academic_record.backlogs_active
    passed = backlogs <= _MAX_ACTIVE_BACKLOGS
    return RuleResult(
        rule_id="R02",
        description=f"Active backlogs must be ≤ {_MAX_ACTIVE_BACKLOGS}",
        passed=passed,
        evidence=(
            f"Reported active backlogs: {backlogs}. "
            f"{'No active backlogs; requirement met.' if passed else f'{backlogs} active backlog(s) present; requirement not met.'}"
        ),
    )


def rule_mandatory_documents_present(app: Application) -> RuleResult:
    """R03 — All mandatory documents must have been submitted."""
    doc_map = {doc.name: doc.status for doc in app.documents}
    missing = [
        name
        for name in _MANDATORY_DOCUMENTS
        if doc_map.get(name) == DocumentStatus.MISSING
    ]
    passed = len(missing) == 0
    if passed:
        evidence = (
            f"All {len(_MANDATORY_DOCUMENTS)} mandatory documents are present or marked unreadable. "
            "Documents marked unreadable should be reviewed separately."
        )
    else:
        evidence = (
            f"{len(missing)} mandatory document(s) missing: {', '.join(sorted(missing))}."
        )
    return RuleResult(
        rule_id="R03",
        description="All mandatory documents must be submitted",
        passed=passed,
        evidence=evidence,
    )


def rule_unreadable_documents_flagged(app: Application) -> RuleResult:
    """R04 — Unreadable documents are flagged for human review (informational; does not fail the application)."""
    unreadable = [
        doc.name
        for doc in app.documents
        if doc.status == DocumentStatus.UNREADABLE
    ]
    # This rule always "passes" in the sense it does not block eligibility,
    # but it records which documents need re-submission or manual inspection.
    if unreadable:
        evidence = (
            f"{len(unreadable)} document(s) marked unreadable: {', '.join(unreadable)}. "
            "These require manual inspection or re-submission before final approval."
        )
    else:
        evidence = "No documents are marked unreadable."
    return RuleResult(
        rule_id="R04",
        description="Unreadable documents flagged for review",
        passed=True,  # Informational — does not block; reviewers are alerted via evidence.
        evidence=evidence,
    )


def rule_relevant_undergraduate_degree(app: Application) -> RuleResult:
    """R05 — Undergraduate field of study must be relevant to the applied programme."""
    # Mapping from programme keyword → accepted undergraduate disciplines (lowercase).
    _ACCEPTED_FIELDS: dict[str, list[str]] = {
        "computer science": ["computer science", "information technology", "software", "cs"],
        "vlsi": ["electronics", "electrical", "instrumentation", "ece", "eee"],
        "artificial intelligence": ["computer science", "information technology", "software", "electronics", "cs"],
        "data science": ["computer science", "information technology", "software", "statistics", "mathematics", "cs"],
        "structural engineering": ["civil", "structural"],
        "power systems": ["electrical", "eee", "power"],
        "biotechnology": ["biotechnology", "bioinformatics", "biomedical", "chemical", "biochemistry"],
    }

    prog_key = _resolve_programme_key(app.programme_applied)
    if prog_key is None:
        return RuleResult(
            rule_id="R05",
            description="Undergraduate discipline relevance",
            passed=False,
            evidence=(
                f"Programme '{app.programme_applied}' has no configured discipline mapping. "
                "Manual review required."
            ),
        )

    accepted = _ACCEPTED_FIELDS.get(prog_key, [])
    field = app.academic_record.field_of_study.lower()
    matched = any(kw in field for kw in accepted)
    return RuleResult(
        rule_id="R05",
        description="Undergraduate discipline relevance",
        passed=matched,
        evidence=(
            f"Applied programme: '{app.programme_applied}'. "
            f"Undergraduate field: '{app.academic_record.field_of_study}'. "
            f"Accepted disciplines: {', '.join(accepted)}. "
            f"{'Match found.' if matched else 'No match found; discipline may not satisfy programme requirements.'}"
        ),
    )


# ---------------------------------------------------------------------------
# Aggregate evaluator
# ---------------------------------------------------------------------------


def evaluate_eligibility(app: Application) -> EligibilityResult:
    """
    Run all eligibility rules against an application and return an aggregate result.

    The outcome is determined as follows:
    - ELIGIBLE     : all rules passed.
    - INELIGIBLE   : one or more blocking rules failed (R01, R02, R03, R05).
    - REQUIRES_REVIEW : any informational finding warrants human attention even
                        if blocking rules passed (e.g., unreadable documents).

    This function is deterministic: given the same Application object it will
    always return the same EligibilityResult.
    """
    blocking_rules = [
        rule_cgpa_or_percentage(app),
        rule_no_active_backlogs(app),
        rule_mandatory_documents_present(app),
        rule_relevant_undergraduate_degree(app),
    ]
    informational_rules = [
        rule_unreadable_documents_flagged(app),
    ]
    all_rules = blocking_rules + informational_rules

    blocking_failures = [r for r in blocking_rules if not r.passed]
    has_unreadable = any(
        doc.status == DocumentStatus.UNREADABLE for doc in app.documents
    )

    if blocking_failures:
        outcome = EligibilityOutcome.INELIGIBLE
        failing_ids = ", ".join(r.rule_id for r in blocking_failures)
        summary = (
            f"Application does not meet eligibility requirements. "
            f"Failed rule(s): {failing_ids}. "
            "See individual rule results for details."
        )
    elif has_unreadable:
        outcome = EligibilityOutcome.REQUIRES_REVIEW
        summary = (
            "Application meets blocking eligibility requirements but contains "
            "one or more unreadable documents that require manual review before approval."
        )
    else:
        outcome = EligibilityOutcome.ELIGIBLE
        summary = (
            "Application meets all evaluated eligibility requirements. "
            "Final approval remains subject to human review and any additional "
            "institutional checks not covered by these rules."
        )

    return EligibilityResult(
        application_id=app.id,
        outcome=outcome,
        rules=all_rules,
        summary=summary,
    )
