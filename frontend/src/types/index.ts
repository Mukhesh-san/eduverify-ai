/**
 * TypeScript types that mirror the backend Pydantic schemas.
 * Keep in sync with backend/models/schemas.py.
 */

export type ReviewStatus =
  | 'pending'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'deferred'

export type DocumentStatus = 'present' | 'missing' | 'unreadable'

export type EligibilityOutcome = 'eligible' | 'ineligible' | 'requires_review'

export interface AcademicRecord {
  institution: string
  degree: string
  field_of_study: string
  graduation_year: number
  cgpa: number | null
  percentage: number | null
  backlogs_active: number
  source_note: string
}

export interface DocumentRecord {
  name: string
  status: DocumentStatus
  note?: string | null
}

export interface RuleResult {
  rule_id: string
  description: string
  passed: boolean
  evidence: string
}

export interface EligibilityResult {
  application_id: string
  outcome: EligibilityOutcome
  rules: RuleResult[]
  summary: string
}

export interface Application {
  id: string
  applicant_name: string
  email: string
  programme_applied: string
  academic_record: AcademicRecord
  documents: DocumentRecord[]
  review_status: ReviewStatus
  submitted_at: string
  data_source: string
}

export interface ApplicationSummary {
  id: string
  applicant_name: string
  programme_applied: string
  review_status: ReviewStatus
  submitted_at: string
  eligibility_outcome: EligibilityOutcome | null
  data_source: string
}

export interface ApplicationListResponse {
  count: number
  items: ApplicationSummary[]
}

export interface ApplicationDetailResponse {
  application: Application
  eligibility: EligibilityResult
}

export interface HealthResponse {
  status: string
  version: string
}
