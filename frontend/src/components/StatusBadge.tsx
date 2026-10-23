import type { ReviewStatus, EligibilityOutcome, DocumentStatus } from '../types'
import './StatusBadge.css'

// ---------------------------------------------------------------------------
// Review status badge
// ---------------------------------------------------------------------------

const REVIEW_LABELS: Record<ReviewStatus, string> = {
  pending: 'Pending',
  under_review: 'Under Review',
  approved: 'Approved',
  rejected: 'Rejected',
  deferred: 'Deferred',
}

interface ReviewStatusBadgeProps {
  status: ReviewStatus
}

export function ReviewStatusBadge({ status }: ReviewStatusBadgeProps) {
  return (
    <span className={`badge badge--review badge--review-${status}`} aria-label={`Review status: ${REVIEW_LABELS[status]}`}>
      {REVIEW_LABELS[status]}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Eligibility outcome badge
// ---------------------------------------------------------------------------

const ELIGIBILITY_LABELS: Record<EligibilityOutcome, string> = {
  eligible: 'Eligible',
  ineligible: 'Ineligible',
  requires_review: 'Requires Review',
}

interface EligibilityBadgeProps {
  outcome: EligibilityOutcome | null
}

export function EligibilityBadge({ outcome }: EligibilityBadgeProps) {
  if (outcome === null) {
    return <span className="badge badge--neutral">—</span>
  }
  return (
    <span
      className={`badge badge--eligibility badge--eligibility-${outcome.replace('_', '-')}`}
      aria-label={`Eligibility: ${ELIGIBILITY_LABELS[outcome]}`}
    >
      {ELIGIBILITY_LABELS[outcome]}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Document status badge
// ---------------------------------------------------------------------------

const DOCUMENT_LABELS: Record<DocumentStatus, string> = {
  present: 'Present',
  missing: 'Missing',
  unreadable: 'Unreadable',
}

interface DocumentStatusBadgeProps {
  status: DocumentStatus
}

export function DocumentStatusBadge({ status }: DocumentStatusBadgeProps) {
  return (
    <span
      className={`badge badge--doc badge--doc-${status}`}
      aria-label={`Document status: ${DOCUMENT_LABELS[status]}`}
    >
      {DOCUMENT_LABELS[status]}
    </span>
  )
}
