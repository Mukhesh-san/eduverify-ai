# EduVerify AI — Project Status

## Current milestone

Milestone 1 hardening: documentation aligned with the implemented stack, and eligibility outcomes corrected for missing or unknown fields.

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

## Not yet implemented

- Database integration.
- Document upload and private storage.
- OCR and field extraction.
- Cross-document consistency checks.
- Technical document-anomaly checks.
- Trusted-source authenticity verification.
- Reviewer actions (approve / reject / defer).
- Verification reports and audit trails.
- Authentication and access control.

## Architecture

- Frontend: React, Vite, TypeScript (`frontend/`). Dev server proxies `/api` to `http://localhost:8000`.
- Backend: Python, FastAPI (`backend/`). In-memory fixtures; GET-only CORS for the Vite origin.
- Eligibility: `backend/core/eligibility.py`, schemas in `backend/models/schemas.py`.
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

After approval: add a small, fixture-based **cross-document consistency** check, kept separate from eligibility and without OCR, uploads, a database, or authenticity claims.

## Latest verification

- Backend: `python -m pytest` from the repository root using `.venv` — **46 passed**, 2 warnings, 0.73s (2026-10-24).
- Frontend: `npm run build` in `frontend/` — **succeeded** (`tsc -b && vite build`, Vite 8.3.5).
- No commit or push was made in this session.
