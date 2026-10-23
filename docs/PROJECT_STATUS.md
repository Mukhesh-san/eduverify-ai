# EduVerify AI — Project Status

## Current milestone

Milestone 2C: cross-document consistency findings displayed in the application detail view.

## Completed

- Local Git repository initialized, `main` created, GitHub remote configured.
- React + Vite + TypeScript frontend: applications table, detail panel, eligibility evidence, API health indicator.
- FastAPI backend: `GET /api/health`, `GET /api/applications`, `GET /api/applications/{id}`.
- Seven synthetic fixture applications (`data_source: fixture`).
- Deterministic eligibility engine (R01–R05) with field-cited evidence.
- Inconclusive blocking rules (missing CGPA and percentage, unknown programme) produce `requires_review` rather than `ineligible`.
- Mandatory documents omitted from the document list fail R03 (treated as missing).
- Deterministic failures still produce `ineligible` (score below floor, active backlogs, missing/omitted documents, unmatched discipline).
- Unreadable documents still produce `requires_review` when blocking rules pass.
- Eligibility panel shows Pass / Fail / Review per rule.
- Upload Application and Settings remain visible and disabled.
- Cross-document consistency engine (`backend/core/consistency.py`): compares applicant name, CGPA, and institution with optional fixture-authored `extracted_fields` on documents. Statuses: `consistent`, `mismatch`, `inconclusive`. Independent of eligibility.
- A few fixtures include extracted fields (Priya: consistent including whitespace/case; Arjun: name mismatch; Rahul: unreadable marks card; Fatima: missing CGPA extraction).
- Application detail UI displays the overall consistency status and field-level source values and evidence. Missing results and empty findings have explicit fallback states.

## Not yet implemented

- Database integration.
- Document upload and private storage.
- OCR and field extraction.
- Technical document-anomaly checks.
- Trusted-source authenticity verification.
- Reviewer actions (approve / reject / defer).
- Verification reports and audit trails.
- Authentication and access control.

## Architecture

- Frontend: React, Vite, TypeScript (`frontend/`). Dev server proxies `/api` to `http://localhost:8000`.
- Backend: Python, FastAPI (`backend/`). In-memory fixtures; GET-only CORS for the Vite origin.
- Eligibility: `backend/core/eligibility.py`, schemas in `backend/models/schemas.py`.
- Consistency: `backend/core/consistency.py`, returned on application detail.
- Planned later: PostgreSQL / Supabase, OCR, private document storage.

## Product constraints

- Use synthetic academic documents.
- Keep eligibility rules configurable.
- Separate consistency checks from authenticity verification.
- Preserve evidence for important findings.
- Route ambiguous cases to human review.
- Never fabricate trusted-source verification.

## Current known issues

- Live UI against a running backend was not exercised in a browser during this hardening pass.
- FastAPI TestClient emits a Starlette/httpx deprecation warning; tests still pass.
- Unused Vite template assets remain under `frontend/src/assets/`.
- R03 still treats unreadable mandatory documents as present; R04 flags them for review.

## Next task

Next: continue with a separately scoped milestone; consistency UI is limited to synthetic fixture evidence and does not affect eligibility.

## Latest verification

- Frontend production build: `npm run build` passed after installing the locked frontend dependencies.
- Backend: `.venv\Scripts\python.exe -m pytest` — 63 passed, 2 dependency deprecation warnings.
- Frontend: `npm run build` — passed after installing the locked frontend dependencies.
