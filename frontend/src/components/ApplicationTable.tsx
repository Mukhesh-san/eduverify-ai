import type { ApplicationSummary } from '../types'
import { ReviewStatusBadge, EligibilityBadge } from './StatusBadge'
import './ApplicationTable.css'

interface ApplicationTableProps {
  applications: ApplicationSummary[]
  selectedId: string | null
  onSelect: (id: string) => void
  loading: boolean
  error: string | null
}

export function ApplicationTable({
  applications,
  selectedId,
  onSelect,
  loading,
  error,
}: ApplicationTableProps) {
  if (loading) {
    return (
      <div className="app-table__state" role="status" aria-live="polite">
        <p className="app-table__state-text">Loading applications…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-table__state app-table__state--error" role="alert">
        <p className="app-table__state-heading">Could not load applications</p>
        <p className="app-table__state-text">{error}</p>
      </div>
    )
  }

  if (applications.length === 0) {
    return (
      <div className="app-table__state" role="status">
        <p className="app-table__state-text">No applications found.</p>
      </div>
    )
  }

  return (
    <div className="app-table__wrapper">
      <table
        className="app-table"
        aria-label="Applications"
        aria-rowcount={applications.length}
      >
        <thead>
          <tr>
            <th scope="col" className="app-table__th">Application ID</th>
            <th scope="col" className="app-table__th">Applicant</th>
            <th scope="col" className="app-table__th">Programme</th>
            <th scope="col" className="app-table__th">Submitted</th>
            <th scope="col" className="app-table__th">Review Status</th>
            <th scope="col" className="app-table__th">Eligibility</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app, index) => (
            <tr
              key={app.id}
              className={`app-table__row${selectedId === app.id ? ' app-table__row--selected' : ''}`}
              onClick={() => onSelect(app.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onSelect(app.id)
                }
              }}
              tabIndex={0}
              aria-selected={selectedId === app.id}
              aria-rowindex={index + 1}
              role="row"
            >
              <td className="app-table__td app-table__td--id">
                <span className="app-table__app-id">{app.id}</span>
              </td>
              <td className="app-table__td app-table__td--name">
                {app.applicant_name}
              </td>
              <td className="app-table__td app-table__td--programme">
                {app.programme_applied}
              </td>
              <td className="app-table__td app-table__td--date">
                {app.submitted_at}
              </td>
              <td className="app-table__td">
                <ReviewStatusBadge status={app.review_status} />
              </td>
              <td className="app-table__td">
                <EligibilityBadge outcome={app.eligibility_outcome} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
