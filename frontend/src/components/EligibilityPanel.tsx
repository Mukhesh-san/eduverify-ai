import type { EligibilityResult, RuleResult } from '../types'
import './EligibilityPanel.css'

interface EligibilityPanelProps {
  eligibility: EligibilityResult
}

const OUTCOME_LABELS: Record<string, string> = {
  eligible: 'Eligible',
  ineligible: 'Ineligible',
  requires_review: 'Requires Review',
}

function rulePresentation(rule: RuleResult): {
  rowClass: string
  verdictClass: string
  verdictLabel: string
} {
  if (rule.inconclusive) {
    return {
      rowClass: 'elig-rule elig-rule--review',
      verdictClass: 'elig-rule__verdict elig-rule__verdict--review',
      verdictLabel: 'Review',
    }
  }
  if (rule.passed) {
    return {
      rowClass: 'elig-rule elig-rule--pass',
      verdictClass: 'elig-rule__verdict elig-rule__verdict--pass',
      verdictLabel: 'Pass',
    }
  }
  return {
    rowClass: 'elig-rule elig-rule--fail',
    verdictClass: 'elig-rule__verdict elig-rule__verdict--fail',
    verdictLabel: 'Fail',
  }
}

function RuleRow({ rule }: { rule: RuleResult }) {
  const presentation = rulePresentation(rule)
  return (
    <li className={presentation.rowClass}>
      <div className="elig-rule__header">
        <span className="elig-rule__id">{rule.rule_id}</span>
        <span className={presentation.verdictClass}>
          {presentation.verdictLabel}
        </span>
        <span className="elig-rule__desc">{rule.description}</span>
      </div>
      <p className="elig-rule__evidence">{rule.evidence}</p>
    </li>
  )
}

export function EligibilityPanel({ eligibility }: EligibilityPanelProps) {
  const outcome = eligibility.outcome

  return (
    <section className="elig-panel" aria-labelledby="elig-panel-heading">
      <h3 className="elig-panel__section-label" id="elig-panel-heading">
        Eligibility Assessment
      </h3>

      <div className={`elig-panel__outcome elig-panel__outcome--${outcome.replace('_', '-')}`}>
        <span className="elig-panel__outcome-label">
          {OUTCOME_LABELS[outcome] ?? outcome}
        </span>
        <p className="elig-panel__summary">{eligibility.summary}</p>
      </div>

      <h4 className="elig-panel__rules-heading">Rule Evaluation</h4>
      <ul className="elig-panel__rules" aria-label="Eligibility rules">
        {eligibility.rules.map((rule) => (
          <RuleRow key={rule.rule_id} rule={rule} />
        ))}
      </ul>

      <p className="elig-panel__disclaimer">
        This assessment is based on data marked as <strong>fixture</strong> (synthetic test data).
        No OCR extraction or trusted-source verification has been performed.
        Final admissions decisions require human review.
      </p>
    </section>
  )
}
