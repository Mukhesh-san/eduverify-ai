\# EduVerify AI — Agent Instructions



\## Project



EduVerify AI is a hackathon prototype for SIH26261. It helps university admissions teams validate student applications, extract academic information, compare documents, apply eligibility rules, and review verification findings.



\## Development principles



\- Inspect existing files before making changes.

\- Read this file, README.md, and docs/PROJECT\_STATUS.md before starting substantial work.

\- Implement one milestone at a time.

\- Preserve existing functionality and avoid unnecessary rewrites.

\- Keep frontend, backend, database, and business logic modular.

\- Prefer readable, maintainable code over clever abstractions.

\- Reuse existing dependencies where possible.

\- Never claim tests passed unless they were actually run.

\- Update docs/PROJECT\_STATUS.md after each substantial milestone.



\## Design requirements



Build professional university admissions software, not a generic AI-generated dashboard.



\- Use restrained colours, consistent typography, and deliberate spacing.

\- Prioritize application tables, document review, evidence comparison, and clear workflows.

\- Avoid gratuitous gradients, excessive rounded cards, decorative charts, and unnecessary animations.

\- Every visible button must work or be clearly marked as unavailable.

\- Do not use fake analytics or fabricated verification results.



\## Verification requirements



Keep these concepts separate:

1\. OCR and field extraction.

2\. Cross-document consistency.

3\. Admission eligibility.

4\. Technical document-anomaly checks.

5\. Trusted-source authenticity verification.



Use deterministic code for exact comparisons and eligibility rules. Preserve evidence for findings. Treat uncertain extraction as requiring review.



Never claim that a document is genuine without appropriate verification evidence. A hash, visual inspection, or AI prediction is not proof of authenticity.



\## Security



\- Never commit API keys, credentials, or real student documents.

\- Keep secrets out of frontend code.

\- Validate uploads and API inputs.

\- Use private document storage and appropriate access controls.

\- Use synthetic student data for development and demos.



\## Multi-agent compatibility



The Git repository is the source of truth, not the coding agent's conversation history.



Before handing off work:

\- Update docs/PROJECT\_STATUS.md.

\- Record completed work, known issues, and the next task.

\- Update documentation when architecture or API contracts change.

\- Inspect Git changes before committing.

\- Never delete or overwrite existing work without permission.

