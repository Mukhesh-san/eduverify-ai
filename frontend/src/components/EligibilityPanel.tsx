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

function RuleRow({ rule }: { rule: RuleResult }) {
  return (
    <li className={`elig-rule${rule.passed ? ' elig-rule--pass' : ' elig-rule--fail'}`}>
      <div className="elig-rule__header">
        <span className="elig-rule__id">{rule.rule_id}</span>
        <span className={`elig-rule__verdict${rule.passed ? ' elig-rule__verdict--pass' : ' elig-rule__verdict--fail'}`}>
          {rule.passed ? 'Pass' : 'Fail'}
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
