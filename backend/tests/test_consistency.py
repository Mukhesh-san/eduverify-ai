"""
Unit tests for the cross-document consistency evaluator.

Independent of eligibility. No network calls.
"""

from __future__ import annotations

from backend.core.consistency import evaluate_consistency
from backend.core.eligibility import evaluate_eligibility
from backend.data.fixtures import APPLICATION_INDEX
from backend.models.schemas import (
    AcademicRecord,
    Application,
    ConsistencyStatus,
    DocumentExtractedFields,
    DocumentRecord,
    DocumentStatus,
    ReviewStatus,
)

_SOURCE_NOTE = "Test fixture — synthetic data only."


def _docs(
    *,
    aadhar_name: str | None = "Test Student",
    degree_name: str | None = "Test Student",
    degree_institution: str | None = "Test University",
    marks_cgpa: float | None = 8.0,
    aadhar_status: DocumentStatus = DocumentStatus.PRESENT,
    degree_status: DocumentStatus = DocumentStatus.PRESENT,
    marks_status: DocumentStatus = DocumentStatus.PRESENT,
    include_extracted: bool = True,
) -> list[DocumentRecord]:
    def extracted(**kwargs) -> DocumentExtractedFields | None:
        if not include_extracted:
            return None
        if all(v is None for v in kwargs.values()):
            return None
        return DocumentExtractedFields(**kwargs)

    return [
        DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
        DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
        DocumentRecord(
            name="Undergraduate Degree Certificate",
            status=degree_status,
            extracted_fields=extracted(
                applicant_name=degree_name,
                institution=degree_institution,
            )
            if degree_status == DocumentStatus.PRESENT
            else None,
        ),
        DocumentRecord(
            name="Undergraduate Consolidated Marks Card",
            status=marks_status,
            extracted_fields=extracted(cgpa=marks_cgpa)
            if marks_status == DocumentStatus.PRESENT
            else None,
        ),
        DocumentRecord(
            name="Aadhar Card",
            status=aadhar_status,
            extracted_fields=extracted(applicant_name=aadhar_name)
            if aadhar_status == DocumentStatus.PRESENT
            else None,
        ),
    ]


def _make_app(**overrides) -> Application:
    defaults = dict(
        id="TEST-CONS-001",
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
        documents=_docs(),
    )
    defaults.update(overrides)
    return Application(**defaults)


def _finding(result, finding_id: str):
    return next(f for f in result.findings if f.finding_id == finding_id)


class TestMatchingValues:
    def test_matching_fields_are_consistent(self):
        result = evaluate_consistency(_make_app())
        assert result.status == ConsistencyStatus.CONSISTENT
        assert len(result.findings) == 4
        assert all(f.status == ConsistencyStatus.CONSISTENT for f in result.findings)

    def test_fixture_priya_rajan_is_consistent(self):
        result = evaluate_consistency(APPLICATION_INDEX["APP-2024-001"])
        assert result.status == ConsistencyStatus.CONSISTENT
        assert _finding(result, "C01").status == ConsistencyStatus.CONSISTENT
        assert _finding(result, "C03").status == ConsistencyStatus.CONSISTENT


class TestMismatches:
    def test_name_mismatch(self):
        app = _make_app(documents=_docs(aadhar_name="Someone Else"))
        result = evaluate_consistency(app)
        assert result.status == ConsistencyStatus.MISMATCH
        c01 = _finding(result, "C01")
        assert c01.status == ConsistencyStatus.MISMATCH
        assert "Someone Else" in (c01.evidence + (c01.right_value or ""))

    def test_cgpa_mismatch(self):
        app = _make_app(documents=_docs(marks_cgpa=6.1))
        result = evaluate_consistency(app)
        assert _finding(result, "C03").status == ConsistencyStatus.MISMATCH
        assert result.status == ConsistencyStatus.MISMATCH

    def test_fixture_arjun_menon_has_name_mismatch(self):
        result = evaluate_consistency(APPLICATION_INDEX["APP-2024-002"])
        assert result.status == ConsistencyStatus.MISMATCH
        assert _finding(result, "C01").status == ConsistencyStatus.MISMATCH


class TestMissingData:
    def test_missing_extracted_fields_are_inconclusive(self):
        app = _make_app(documents=_docs(include_extracted=False))
        result = evaluate_consistency(app)
        assert result.status == ConsistencyStatus.INCONCLUSIVE
        assert all(f.status == ConsistencyStatus.INCONCLUSIVE for f in result.findings)

    def test_missing_application_cgpa_is_inconclusive(self):
        app = _make_app(
            academic_record=AcademicRecord(
                institution="Test University",
                degree="B.Tech",
                field_of_study="Computer Science",
                graduation_year=2024,
                cgpa=None,
                percentage=71.5,
                backlogs_active=0,
                source_note=_SOURCE_NOTE,
            )
        )
        result = evaluate_consistency(app)
        assert _finding(result, "C03").status == ConsistencyStatus.INCONCLUSIVE

    def test_missing_document_is_inconclusive(self):
        app = _make_app(documents=_docs(degree_status=DocumentStatus.MISSING))
        result = evaluate_consistency(app)
        assert _finding(result, "C02").status == ConsistencyStatus.INCONCLUSIVE
        assert _finding(result, "C04").status == ConsistencyStatus.INCONCLUSIVE

    def test_unreadable_document_is_inconclusive(self):
        app = _make_app(documents=_docs(marks_status=DocumentStatus.UNREADABLE))
        result = evaluate_consistency(app)
        assert _finding(result, "C03").status == ConsistencyStatus.INCONCLUSIVE
        assert "unreadable" in _finding(result, "C03").evidence.lower()

    def test_fixture_rahul_desai_marks_card_inconclusive(self):
        result = evaluate_consistency(APPLICATION_INDEX["APP-2024-004"])
        assert _finding(result, "C03").status == ConsistencyStatus.INCONCLUSIVE


class TestNormalisation:
    def test_capitalization_and_whitespace_match(self):
        app = _make_app(
            applicant_name="Priya Rajan",
            documents=_docs(
                aadhar_name="  PRIYA   rajan ",
                degree_name="priya rajan",
                degree_institution="  Test   University",
            ),
        )
        result = evaluate_consistency(app)
        assert _finding(result, "C01").status == ConsistencyStatus.CONSISTENT
        assert _finding(result, "C02").status == ConsistencyStatus.CONSISTENT
        assert _finding(result, "C04").status == ConsistencyStatus.CONSISTENT

    def test_fixture_priya_aadhar_uses_normalisation(self):
        result = evaluate_consistency(APPLICATION_INDEX["APP-2024-001"])
        c01 = _finding(result, "C01")
        assert c01.right_value == "  PRIYA   Rajan "
        assert c01.status == ConsistencyStatus.CONSISTENT


class TestSeparationFromEligibility:
    def test_consistency_does_not_change_eligibility_outcome(self):
        app = APPLICATION_INDEX["APP-2024-001"]
        before = evaluate_eligibility(app)
        evaluate_consistency(app)
        after = evaluate_eligibility(app)
        assert before.outcome == after.outcome
        assert before.summary == after.summary
