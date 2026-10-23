"""
Synthetic application fixtures for EduVerify AI.

IMPORTANT: All data here is fictional and was manually authored for
development and demonstration purposes. It has NOT been produced by OCR,
external APIs, or any form of document scanning. The `data_source` field on
every record is set to "fixture" to make this explicit.

Do not use this data to make real admissions decisions.
"""

from backend.models.schemas import (
    AcademicRecord,
    Application,
    DocumentExtractedFields,
    DocumentRecord,
    DocumentStatus,
    ReviewStatus,
)

# ---------------------------------------------------------------------------
# Synthetic applications
# ---------------------------------------------------------------------------

APPLICATIONS: list[Application] = [
    Application(
        id="APP-2024-001",
        applicant_name="Priya Rajan",
        email="priya.rajan@example.invalid",
        programme_applied="M.Tech — Computer Science and Engineering",
        submitted_at="2024-11-05",
        review_status=ReviewStatus.PENDING,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="National Institute of Technology, Trichy",
            degree="B.Tech",
            field_of_study="Computer Science and Engineering",
            graduation_year=2024,
            cgpa=8.7,
            percentage=None,
            backlogs_active=0,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(
                name="Undergraduate Degree Certificate",
                status=DocumentStatus.PRESENT,
                extracted_fields=DocumentExtractedFields(
                    applicant_name="Priya Rajan",
                    institution="National Institute of Technology, Trichy",
                ),
            ),
            DocumentRecord(
                name="Undergraduate Consolidated Marks Card",
                status=DocumentStatus.PRESENT,
                extracted_fields=DocumentExtractedFields(cgpa=8.7),
            ),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(
                name="Aadhar Card",
                status=DocumentStatus.PRESENT,
                extracted_fields=DocumentExtractedFields(
                    applicant_name="  PRIYA   Rajan ",
                ),
            ),
            DocumentRecord(name="Category Certificate", status=DocumentStatus.MISSING, note="Applicant indicated General category; no certificate required."),
        ],
    ),
    Application(
        id="APP-2024-002",
        applicant_name="Arjun Menon",
        email="arjun.menon@example.invalid",
        programme_applied="M.Tech — VLSI Design",
        submitted_at="2024-11-06",
        review_status=ReviewStatus.UNDER_REVIEW,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="College of Engineering, Trivandrum",
            degree="B.Tech",
            field_of_study="Electronics and Communication Engineering",
            graduation_year=2024,
            cgpa=7.2,
            percentage=None,
            backlogs_active=1,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.MISSING, note="Degree award pending; provisional certificate submitted instead."),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(
                name="Aadhar Card",
                status=DocumentStatus.PRESENT,
                extracted_fields=DocumentExtractedFields(
                    applicant_name="Arjun Nair",
                ),
            ),
            DocumentRecord(name="OBC Certificate", status=DocumentStatus.PRESENT),
        ],
    ),
    Application(
        id="APP-2024-003",
        applicant_name="Sneha Kulkarni",
        email="sneha.kulkarni@example.invalid",
        programme_applied="M.Tech — Artificial Intelligence",
        submitted_at="2024-11-07",
        review_status=ReviewStatus.APPROVED,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="Pune Institute of Computer Technology",
            degree="B.E.",
            field_of_study="Information Technology",
            graduation_year=2023,
            cgpa=9.1,
            percentage=None,
            backlogs_active=0,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Category Certificate", status=DocumentStatus.MISSING, note="Applicant indicated General category; no certificate required."),
        ],
    ),
    Application(
        id="APP-2024-004",
        applicant_name="Rahul Desai",
        email="rahul.desai@example.invalid",
        programme_applied="M.Tech — Structural Engineering",
        submitted_at="2024-11-08",
        review_status=ReviewStatus.REJECTED,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="Government Engineering College, Aurangabad",
            degree="B.E.",
            field_of_study="Civil Engineering",
            graduation_year=2024,
            cgpa=5.8,
            percentage=None,
            backlogs_active=3,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.UNREADABLE, note="Uploaded file appears corrupted; re-submission requested."),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.MISSING),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="SC Certificate", status=DocumentStatus.PRESENT),
        ],
    ),
    Application(
        id="APP-2024-005",
        applicant_name="Fatima Ansari",
        email="fatima.ansari@example.invalid",
        programme_applied="M.Tech — Data Science",
        submitted_at="2024-11-09",
        review_status=ReviewStatus.DEFERRED,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="Jamia Millia Islamia",
            degree="B.Tech",
            field_of_study="Computer Science",
            graduation_year=2024,
            cgpa=None,
            percentage=71.5,
            backlogs_active=0,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed. "
                "Institution uses percentage grading; CGPA field is absent."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(
                name="Undergraduate Consolidated Marks Card",
                status=DocumentStatus.PRESENT,
            ),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.MISSING, note="Transfer certificate from institution pending."),
            DocumentRecord(
                name="Aadhar Card",
                status=DocumentStatus.PRESENT,
                extracted_fields=DocumentExtractedFields(
                    applicant_name="Fatima Ansari",
                ),
            ),
            DocumentRecord(name="EWS Certificate", status=DocumentStatus.PRESENT),
        ],
    ),
    Application(
        id="APP-2024-006",
        applicant_name="Vikram Nair",
        email="vikram.nair@example.invalid",
        programme_applied="M.Tech — Power Systems",
        submitted_at="2024-11-10",
        review_status=ReviewStatus.PENDING,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="Kerala Technological University",
            degree="B.Tech",
            field_of_study="Electrical and Electronics Engineering",
            graduation_year=2024,
            cgpa=6.5,
            percentage=None,
            backlogs_active=0,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="OBC-NCL Certificate", status=DocumentStatus.PRESENT),
        ],
    ),
    Application(
        id="APP-2024-007",
        applicant_name="Ananya Sharma",
        email="ananya.sharma@example.invalid",
        programme_applied="M.Tech — Biotechnology",
        submitted_at="2024-11-11",
        review_status=ReviewStatus.UNDER_REVIEW,
        data_source="fixture",
        academic_record=AcademicRecord(
            institution="Delhi Technological University",
            degree="B.Tech",
            field_of_study="Biotechnology",
            graduation_year=2024,
            cgpa=8.2,
            percentage=None,
            backlogs_active=0,
            source_note=(
                "Fixture data. Fields were authored manually for development. "
                "No OCR or trusted-source verification has been performed."
            ),
        ),
        documents=[
            DocumentRecord(name="10th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="12th Mark Sheet", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Degree Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Undergraduate Consolidated Marks Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Transfer Certificate", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Aadhar Card", status=DocumentStatus.PRESENT),
            DocumentRecord(name="Category Certificate", status=DocumentStatus.MISSING, note="Applicant indicated General category; no certificate required."),
        ],
    ),
]

# Indexed for O(1) lookup
APPLICATION_INDEX: dict[str, Application] = {app.id: app for app in APPLICATIONS}
