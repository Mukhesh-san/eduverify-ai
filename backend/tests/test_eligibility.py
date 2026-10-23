"""
Unit tests for the deterministic eligibility engine.

These tests verify that each rule produces the correct outcome for known inputs.
No network calls; no external dependencies.
"""

from __future__ import annotations

import pytest

from backend.core.eligibility import (
    evaluate_eligibility,
    rule_cgpa_or_percentage,
    rule_mandatory_documents_present,
    rule_no_active_backlogs,
    rule_relevant_undergraduate_degree,
    rule_unreadable_documents_flagged,
)
from backend.data.fixtures import APPLICATION_INDEX, APPLICATIONS
from backend.models.schemas import (
    AcademicRecord,
    Application,
    DocumentRecord,
    DocumentStatus,
    EligibilityOutcome,
    ReviewStatus,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SOURCE_NOTE = "Test fixture — synthetic data only."

def _make_app(**overrides) -> Application:
    """Build a minimal synthetic Application for testing."""
    defaults = dict(
        id="TEST-001",
        applicant_name="Test Student",
        email="test@example.invalid",
        programme_applied="M.Tech — Computer Science and Engineering",
        submitted_at="2024-01-01",
        review_status=ReviewStatus.PENDING,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="Test University",
            degree="B.Tech",
            field_of_study="Computer Science",
            graduation_year=2024,
            cgpa=8.0,
            percentage=None,
            backlogs_active=0,
            source_note=_SOURCE_NOTE,
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
        ],
    )
    defaults.update(overrides)
    return Application(**defaults)


def _make_record(**overrides) -> AcademicRecord:
    defaults = dict(
        institution="Test University",
        degree="B.Tech",
        field_of_study="Computer Science",
        graduation_year=2024,
        cgpa=8.0,
        percentage=None,
        backlogs_active=0,
        source_note=_SOURCE_NOTE,
    )
    defaults.update(overrides)
    return AcademicRecord(**defaults)


# ---------------------------------------------------------------------------
# R01: CGPA / percentage
# ---------------------------------------------------------------------------


class TestRuleCgpaOrPercentage:
    def test_cgpa_above_floor_passes(self):
        app = _make_app()
        result = rule_cgpa_or_percentage(app)
        assert result.rule_id == "R01"
        assert result.passed is True
        assert "8.0" in result.evidence

    def test_cgpa_exactly_at_floor_passes(self):
        app = _make_app(
            academic_record=_make_record(cgpa=7.5)
        )
        result = rule_cgpa_or_percentage(app)
        assert result.passed is True

    def test_cgpa_below_floor_fails(self):
        app = _make_app(
            academic_record=_make_record(cgpa=6.0)
        )
        result = rule_cgpa_or_percentage(app)
        assert result.passed is False
        assert "6.0" in result.evidence

    def test_percentage_above_floor_passes(self):
        app = _make_app(
            academic_record=_make_record(cgpa=None, percentage=75.0)
        )
        result = rule_cgpa_or_percentage(app)
        assert result.passed is True
        assert "75.0" in result.evidence

    def test_percentage_below_floor_fails(self):
        app = _make_app(
            academic_record=_make_record(cgpa=None, percentage=65.0)
        )
        result = rule_cgpa_or_percentage(app)
        assert result.passed is False

    def test_neither_cgpa_nor_percentage_is_inconclusive(self):
        app = _make_app(
            academic_record=_make_record(cgpa=None, percentage=None)
        )
        result = rule_cgpa_or_percentage(app)
        assert result.passed is False
        assert result.inconclusive is True
        assert "human review" in result.evidence.lower()

    def test_unknown_programme_is_inconclusive(self):
        app = _make_app(programme_applied="M.Tech — Quantum Alchemy")
        result = rule_cgpa_or_percentage(app)
        assert result.passed is False
        assert result.inconclusive is True
        assert "no configured" in result.evidence.lower()


# ---------------------------------------------------------------------------
# R02: Active backlogs
# ---------------------------------------------------------------------------


class TestRuleNoActiveBacklogs:
    def test_zero_backlogs_passes(self):
        app = _make_app(academic_record=_make_record(backlogs_active=0))
        result = rule_no_active_backlogs(app)
        assert result.passed is True

    def test_one_backlog_fails(self):
        app = _make_app(academic_record=_make_record(backlogs_active=1))
        result = rule_no_active_backlogs(app)
        assert result.passed is False
        assert "1" in result.evidence

    def test_three_backlogs_fails(self):
        app = _make_app(academic_record=_make_record(backlogs_active=3))
        result = rule_no_active_backlogs(app)
        assert result.passed is False


# ---------------------------------------------------------------------------
# R03: Mandatory documents
# ---------------------------------------------------------------------------


class TestRuleMandatoryDocuments:
    def test_all_present_passes(self):
        app = _make_app()
        result = rule_mandatory_documents_present(app)
        assert result.passed is True

    def test_missing_degree_certificate_fails(self):
        docs = [
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.MISSING),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
        ]
        app = _make_app(documents=docs)
        result = rule_mandatory_documents_present(app)
        assert result.passed is False
        assert "Undergraduate Degree Certificate" in result.evidence

    def test_unreadable_is_not_missing(self):
        """UNREADABLE documents do not fail R03; they are flagged by R04."""
        docs = [
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.UNREADABLE),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
        ]
        app = _make_app(documents=docs)
        result = rule_mandatory_documents_present(app)
        assert result.passed is True

    def test_omitted_mandatory_document_fails(self):
        """A mandatory document absent from the list must not pass R03."""
        docs = [
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            # Aadhar Card omitted entirely
        ]
        app = _make_app(documents=docs)
        result = rule_mandatory_documents_present(app)
        assert result.passed is False
        assert result.inconclusive is False
        assert "Aadhar Card" in result.evidence


# ---------------------------------------------------------------------------
# R04: Unreadable documents (informational)
# ---------------------------------------------------------------------------


class TestRuleUnreadableFlagged:
    def test_no_unreadable_passes(self):
        app = _make_app()
        result = rule_unreadable_documents_flagged(app)
        assert result.passed is True
        assert "No documents are marked unreadable" in result.evidence

    def test_unreadable_passes_but_evidence_contains_name(self):
        docs = [
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.UNREADABLE),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
        ]
        app = _make_app(documents=docs)
        result = rule_unreadable_documents_flagged(app)
        assert result.passed is True  # informational rule
        assert "Undergraduate Consolidated Marks Card" in result.evidence


# ---------------------------------------------------------------------------
# R05: Degree relevance
# ---------------------------------------------------------------------------


class TestRuleDegreeRelevance:
    def test_matching_discipline_passes(self):
        app = _make_app(academic_record=_make_record(field_of_study="Computer Science"))
        result = rule_relevant_undergraduate_degree(app)
        assert result.passed is True

    def test_non_matching_discipline_fails(self):
        app = _make_app(academic_record=_make_record(field_of_study="Mechanical Engineering"))
        result = rule_relevant_undergraduate_degree(app)
        assert result.passed is False

    def test_it_matches_cs_programme(self):
        app = _make_app(academic_record=_make_record(field_of_study="Information Technology"))
        result = rule_relevant_undergraduate_degree(app)
        assert result.passed is True

    def test_unknown_programme_is_inconclusive(self):
        app = _make_app(programme_applied="M.Tech — Quantum Alchemy")
        result = rule_relevant_undergraduate_degree(app)
        assert result.passed is False
        assert result.inconclusive is True


# ---------------------------------------------------------------------------
# Aggregate evaluate_eligibility
# ---------------------------------------------------------------------------


class TestEvaluateEligibility:
    def test_eligible_application(self):
        app = _make_app()
        result = evaluate_eligibility(app)
        assert result.application_id == "TEST-001"
        assert result.outcome == EligibilityOutcome.ELIGIBLE
        assert len(result.rules) == 5

    def test_ineligible_due_to_low_cgpa(self):
        app = _make_app(academic_record=_make_record(cgpa=4.0))
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.INELIGIBLE
        assert "R01" in result.summary

    def test_ineligible_due_to_backlogs(self):
        app = _make_app(academic_record=_make_record(backlogs_active=2))
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.INELIGIBLE
        assert "R02" in result.summary

    def test_missing_scores_requires_review(self):
        app = _make_app(academic_record=_make_record(cgpa=None, percentage=None))
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.REQUIRES_REVIEW
        r01 = next(r for r in result.rules if r.rule_id == "R01")
        assert r01.inconclusive is True

    def test_unknown_programme_requires_review(self):
        app = _make_app(programme_applied="M.Tech — Quantum Alchemy")
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.REQUIRES_REVIEW
        assert "R01" in result.summary
        assert "R05" in result.summary

    def test_omitted_mandatory_document_is_ineligible(self):
        """Omitted documents are a deterministic completeness failure, not review-only."""
        docs = [
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
        ]
        app = _make_app(documents=docs)
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.INELIGIBLE
        assert "R03" in result.summary

    def test_deterministic_failure_overrides_inconclusive_rule(self):
        """Known evidence of ineligibility still wins over missing/unknown fields."""
        app = _make_app(
            programme_applied="M.Tech — Quantum Alchemy",
            academic_record=_make_record(backlogs_active=2),
        )
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.INELIGIBLE
        assert "R02" in result.summary

    def test_requires_review_due_to_unreadable_doc(self):
        docs = [
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.UNREADABLE),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
        ]
        app = _make_app(documents=docs)
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.REQUIRES_REVIEW

    def test_deterministic_same_input_same_output(self):
        """Running evaluate_eligibility twice on the same object must return the same result."""
        app = _make_app()
        r1 = evaluate_eligibility(app)
        r2 = evaluate_eligibility(app)
        assert r1.outcome == r2.outcome
        assert r1.summary == r2.summary

    def test_fixture_priya_rajan_is_eligible(self):
        """Priya Rajan (APP-2024-001) has CGPA 8.7, no backlogs, all docs present → eligible."""
        app = APPLICATION_INDEX["APP-2024-001"]
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.ELIGIBLE

    def test_fixture_rahul_desai_is_ineligible(self):
        """Rahul Desai (APP-2024-004) has CGPA 5.8 and 3 backlogs → ineligible."""
        app = APPLICATION_INDEX["APP-2024-004"]
        result = evaluate_eligibility(app)
        assert result.outcome == EligibilityOutcome.INELIGIBLE

    def test_all_fixtures_produce_valid_outcomes(self):
        """All fixture applications must produce a valid eligibility result without raising."""
        for app in APPLICATIONS:
            result = evaluate_eligibility(app)
            assert result.outcome in list(EligibilityOutcome)
            assert result.application_id == app.id
            assert len(result.rules) == 5
