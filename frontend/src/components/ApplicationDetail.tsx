import type { ApplicationDetailResponse, ConsistencyFinding, ConsistencyStatus } from '../types'
import { ReviewStatusBadge, DocumentStatusBadge } from './StatusBadge'
import { EligibilityPanel } from './EligibilityPanel'
import './ApplicationDetail.css'

const CONSISTENCY_STATUS_LABELS: Record<ConsistencyStatus, string> = {
  consistent: 'Consistent',
  mismatch: 'Mismatch',
  inconclusive: 'Inconclusive',
}

function sourceLabel(source: string): string {
  if (source.startsWith('application.')) return 'Application record'
  return source.match(/^documents\['(.+)'\]/)?.[1] ?? source
}

function ConsistencyFindingRow({ finding }: { finding: ConsistencyFinding }) {
  return (
    <li className={`consistency-finding consistency-finding--${finding.status}`}>
      <div className="consistency-finding__header">
        <span className="consistency-finding__field">
          {finding.field.replace(/_/g, ' ')}
        </span>
        <span className={`consistency-finding__status consistency-finding__status--${finding.status}`}>
          {CONSISTENCY_STATUS_LABELS[finding.status]}
        </span>
      </div>
      <dl className="consistency-finding__values">
        <div>
          <dt>{sourceLabel(finding.left_source)}</dt>
          <dd>{finding.left_value?.trim() || 'Not available'}</dd>
        </div>
        <div>
          <dt>{sourceLabel(finding.right_source)}</dt>
          <dd>{finding.right_value?.trim() || 'Not available'}</dd>
        </div>
      </dl>
      <p className="consistency-finding__evidence">{finding.evidence}</p>
    </li>
  )
}

interface ApplicationDetailProps {
  detail: ApplicationDetailResponse | null
  loading: boolean
  error: string | null
  onClose: () => void
}

export function ApplicationDetail({
  detail,
  loading,
  error,
  onClose,
}: ApplicationDetailProps) {
  const panelId = 'application-detail-panel'

  return (
    <aside
      className="app-detail"
      aria-label="Application detail"
      aria-live="polite"
      id={panelId}
    >
      {loading && (
        <div className="app-detail__state" role="status">
          <p className="app-detail__state-text">Loading application…</p>
        </div>
      )}

      {!loading && error && (
        <div className="app-detail__state app-detail__state--error" role="alert">
          <p className="app-detail__state-heading">Could not load application</p>
          <p className="app-detail__state-text">{error}</p>
        </div>
      )}

      {!loading && !error && !detail && (
        <div className="app-detail__state" role="status">
          <p className="app-detail__state-text">
            Select an application from the table to view its details.
          </p>
        </div>
      )}

      {!loading && !error && detail && (
        <>
          <div className="app-detail__header">
            <div className="app-detail__header-main">
              <span className="app-detail__app-id">{detail.application.id}</span>
              <h2 className="app-detail__name">{detail.application.applicant_name}</h2>
              <p className="app-detail__programme">{detail.application.programme_applied}</p>
            </div>
            <div className="app-detail__header-meta">
              <ReviewStatusBadge status={detail.application.review_status} />
              <button
                className="app-detail__close"
                onClick={onClose}
                aria-label="Close detail panel"
                id="btn-close-detail"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Data source notice */}
          <div className="app-detail__source-notice">
            <strong>Data source:</strong> {detail.application.data_source === 'fixture'
              ? 'Synthetic fixture — development and demonstration data only. No OCR or external verification performed.'
              : detail.application.data_source}
          </div>

          {/* Academic record */}
          <section className="app-detail__section" aria-labelledby="academic-record-heading">
            <h3 className="app-detail__section-label" id="academic-record-heading">
              Academic Record
            </h3>
            <dl className="app-detail__kv">
              <div className="app-detail__kv-row">
                <dt>Institution</dt>
                <dd>{detail.application.academic_record.institution}</dd>
              </div>
              <div className="app-detail__kv-row">
                <dt>Degree</dt>
                <dd>{detail.application.academic_record.degree}</dd>
              </div>
              <div className="app-detail__kv-row">
                <dt>Field of Study</dt>
                <dd>{detail.application.academic_record.field_of_study}</dd>
              </div>
              <div className="app-detail__kv-row">
                <dt>Graduation Year</dt>
                <dd>{detail.application.academic_record.graduation_year}</dd>
              </div>
              <div className="app-detail__kv-row">
                <dt>CGPA (10-pt)</dt>
                <dd>
                  {detail.application.academic_record.cgpa !== null
                    ? detail.application.academic_record.cgpa.toFixed(2)
                    : <span className="app-detail__kv-absent">Not reported</span>}
                </dd>
              </div>
              <div className="app-detail__kv-row">
                <dt>Percentage</dt>
                <dd>
                  {detail.application.academic_record.percentage !== null
                    ? `${detail.application.academic_record.percentage.toFixed(1)}%`
                    : <span className="app-detail__kv-absent">Not reported</span>}
                </dd>
              </div>
              <div className="app-detail__kv-row">
                <dt>Active Backlogs</dt>
                <dd>{detail.application.academic_record.backlogs_active}</dd>
              </div>
            </dl>
            <p className="app-detail__source-note">
              {detail.application.academic_record.source_note}
            </p>
          </section>

          {/* Documents */}
          <section className="app-detail__section" aria-labelledby="documents-heading">
            <h3 className="app-detail__section-label" id="documents-heading">
              Documents
            </h3>
            <ul className="app-detail__docs" aria-label="Document checklist">
              {detail.application.documents.map((doc) => (
                <li key={doc.name} className="app-detail__doc-row">
                  <span className="app-detail__doc-name">{doc.name}</span>
                  <DocumentStatusBadge status={doc.status} />
                  {doc.note && (
                    <span className="app-detail__doc-note">{doc.note}</span>
                  )}
                </li>
              ))}
            </ul>
          </section>

          {/* Cross-document consistency */}
          <section className="consistency-panel" aria-labelledby="consistency-heading">
            <h3 className="app-detail__section-label" id="consistency-heading">
              Cross-Document Consistency
            </h3>
            {!detail.consistency ? (
              <p className="consistency-panel__empty" role="status">
                Consistency results are not available for this application.
              </p>
            ) : (
              <>
                <div
                  className={`consistency-panel__overall consistency-panel__overall--${detail.consistency.status}`}
                  role="status"
                >
                  {CONSISTENCY_STATUS_LABELS[detail.consistency.status]}
                </div>
                <p className="consistency-panel__summary">{detail.consistency.summary}</p>
                {detail.consistency.findings.length > 0 ? (
                  <ul className="consistency-panel__findings" aria-label="Consistency findings">
                    {detail.consistency.findings.map((finding) => (
                      <ConsistencyFindingRow key={finding.finding_id} finding={finding} />
                    ))}
                  </ul>
                ) : (
                  <p className="consistency-panel__empty">
                    No field comparisons are available.
                  </p>
                )}
                <p className="consistency-panel__disclaimer">
                  Based on synthetic fixture data only. This is not OCR or document authenticity verification.
                </p>
              </>
            )}
          </section>

          {/* Eligibility */}
          <EligibilityPanel eligibility={detail.eligibility} />
        </>
      )}
    </aside>
  )
}
