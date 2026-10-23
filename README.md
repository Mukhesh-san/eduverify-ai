# EduVerify AI

AI-powered educational application validation, document authentication, and regulatory compliance verification.

**Project ID:** SIH26261
**Domain:** Educational certificates, admissions, and student applications

**Status:** Milestone 2C — admissions review UI with synthetic fixtures, deterministic eligibility, and cross-document consistency findings.

## Problem

Admissions teams manually review academic documents, compare student details, check application completeness, and apply eligibility requirements. This can be slow and prone to inconsistencies.

## Proposed solution

EduVerify AI aims to provide:

- Academic document text extraction.
- Cross-document consistency checks.
- Configurable eligibility validation.
- Document-anomaly indicators.
- Evidence-backed verification reports.
- Human review and audit trails.

The current review surface uses synthetic application data and provides deterministic eligibility assessment and cross-document consistency findings. Extraction, anomaly detection, and trusted-source verification are not implemented.

## Current implementation

- **Frontend:** React, Vite, TypeScript. Application table, detail panel, eligibility evidence, and cross-document consistency findings. Upload and Settings are visible but disabled.
- **Backend:** Python, FastAPI. Read-only JSON API over in-memory fixtures, including consistency results on application details.
- **Eligibility engine:** Deterministic rules (R01–R05) with cited field evidence. Missing or unknown fields produce `requires_review`. Deterministic failures (score below floor, backlogs, missing or omitted mandatory documents, unmatched discipline) produce `ineligible`.
- **Data:** Seven synthetic applications in `backend/data/fixtures.py`. Every record is marked `data_source: fixture`.
- **Consistency:** Application and fixture-authored document values are compared deterministically; findings are independent of eligibility and do not verify document authenticity.

## Important limitations

- Fixture data is not OCR output and is not a trusted-source verification.
- AI extraction does not establish document authenticity. Trusted-source verification requires an authorized source or a verifiable credential.
- Ambiguous findings are routed to human review.
- There is no database, document upload, authentication, or persistence.

## Technology stack

**Implemented**

- Frontend: React, Vite, TypeScript
- Backend: Python, FastAPI, Pydantic
- Tests: pytest (backend), `tsc` + Vite production build (frontend)

**Planned, not implemented**

- Database: PostgreSQL / Supabase
- OCR: to be selected and tested
- Document storage: private storage

## Development

Consult `AGENTS.md` for engineering guidelines and `docs/PROJECT_STATUS.md` for current progress.

Use synthetic documents and data during development. Do not commit API keys, credentials, or real student documents.

### Backend

From the repository root (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/api/docs

```powershell
python -m pytest
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server (http://localhost:5173) proxies `/api` to `http://localhost:8000`. Start the backend first.

```powershell
cd frontend
npm run build
```

## License

Not yet selected.
