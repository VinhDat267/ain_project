import { useEffect, useState, type KeyboardEvent } from 'react'
import { fetchAnalytics } from '../api/client'
import {
  ConfusionMatrixChart,
  CostSensitivityChart,
  DualGateChart,
  IntentCvChart,
  NoiseCurveChart,
  PerIntentResolutionChart,
  ThresholdSweepChart,
} from '../components/SvgCharts'
import type { AnalyticsPayload } from '../types/api'

type AnalyticsTabId = 'overview' | 'cv-confusion' | 'noise-sweep' | 'business-ablations'

const ANALYTICS_TABS: Array<{ id: AnalyticsTabId; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'cv-confusion', label: 'Confusion & CV' },
  { id: 'noise-sweep', label: 'Noise & Sweep' },
  { id: 'business-ablations', label: 'Business & Ablations' },
]

function fmtPct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined) return 'n/a'
  return `${(value * 100).toFixed(digits)}%`
}

export function AnalyticsView() {
  const [data, setData] = useState<AnalyticsPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<AnalyticsTabId>('overview')
  const [selectedExp, setSelectedExp] = useState<string>('E7')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchAnalytics()
      .then((payload) => {
        if (!cancelled) {
          setData(payload)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unable to load analytics.')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  const handleTabKeyDown = (e: KeyboardEvent<HTMLButtonElement>, idx: number) => {
    let nextIdx = idx
    if (e.key === 'ArrowRight') nextIdx = (idx + 1) % ANALYTICS_TABS.length
    else if (e.key === 'ArrowLeft') nextIdx = (idx - 1 + ANALYTICS_TABS.length) % ANALYTICS_TABS.length
    else if (e.key === 'Home') nextIdx = 0
    else if (e.key === 'End') nextIdx = ANALYTICS_TABS.length - 1
    else return

    e.preventDefault()
    const target = ANALYTICS_TABS[nextIdx]
    setActiveTab(target.id)
    document.getElementById(`ana-tab-${target.id}`)?.focus()
  }

  if (loading) {
    return (
      <section aria-labelledby="analytics-heading">
        <div className="view-head">
          <h1 id="analytics-heading">Research &amp; Operational Analytics</h1>
        </div>
        <p className="muted-note">Loading live benchmark CSVs from experiments/results...</p>
      </section>
    )
  }

  if (error || !data) {
    return (
      <section aria-labelledby="analytics-heading">
        <div className="view-head">
          <h1 id="analytics-heading">Research &amp; Operational Analytics</h1>
        </div>
        <div className="abstention-block" role="alert">
          <div className="abstention-block__title">Analytics unavailable</div>
          <p className="muted-note">{error ?? 'No analytics data returned.'}</p>
        </div>
      </section>
    )
  }

  const k = data.kpis
  const inCorpusN = k.in_corpus_queries ?? 105
  const totalN = k.total_queries ?? 120
  const oocN = k.ooc_queries ?? 15

  const deliveredTop3Count =
    k.top3_rescue_rate !== null && k.in_corpus_queries !== null
      ? Math.round(k.top3_rescue_rate * k.in_corpus_queries)
      : null

  const expRows = data.dev_ablations[selectedExp] ?? []

  return (
    <section aria-labelledby="analytics-heading">
      <div className="view-head">
        <div>
          <h1 id="analytics-heading">Research &amp; Operational Analytics</h1>
          <p className="view-lead">
            Live metrics parsed from the {totalN}-query fixed benchmark and {data.threshold_sweep.length ? '146-query' : ''} dev ablations.
          </p>
        </div>
      </div>

      <div className="metric-strip">
        <div className="metric-cell">
          <div className="metric-cell__label">In-Corpus MRR</div>
          <div className="metric-cell__value num">{k.mrr !== null ? k.mrr.toFixed(3) : 'n/a'}</div>
          <div className="metric-cell__note">{inCorpusN} in-corpus queries</div>
        </div>

        <div className="metric-cell">
          <div className="metric-cell__label">Delivered Top-3</div>
          <div className="metric-cell__value num">{fmtPct(k.top3_rescue_rate)}</div>
          <div className="metric-cell__note">
            {deliveredTop3Count ?? 'n/a'}/{inCorpusN} (Raw Hit@3 {fmtPct(k.raw_hit3)})
          </div>
        </div>

        <div className="metric-cell">
          <div className="metric-cell__label">Intent Accuracy</div>
          <div className="metric-cell__value num">{fmtPct(k.intent_accuracy)}</div>
          <div className="metric-cell__note">
            {k.intent_correct ?? 'n/a'}/{inCorpusN} full-train
          </div>
        </div>

        <div className="metric-cell">
          <div className="metric-cell__label">OOC Rejection</div>
          <div className="metric-cell__value num">{fmtPct(k.ooc_rejection_rate, 0)}</div>
          <div className="metric-cell__note">
            {k.ooc_rejection_rate !== null ? Math.round(k.ooc_rejection_rate * oocN) : 'n/a'}/{oocN} dual gate
          </div>
        </div>

        <div className="metric-cell">
          <div className="metric-cell__label">Deflection Top-1</div>
          <div className="metric-cell__value num">{fmtPct(k.deflection_rate)}</div>
          <div className="metric-cell__note">False-abst {fmtPct(k.false_abstention_rate)}</div>
        </div>

        <div className="metric-cell">
          <div className="metric-cell__label">Penalty Cost</div>
          <div className="metric-cell__value num">{k.expected_cost !== null ? k.expected_cost.toFixed(3) : 'n/a'}</div>
          <div className="metric-cell__note">
            {k.w_silent_wrong ?? 5}:{k.w_ooc_leak ?? 5}:{k.w_false_abstain ?? 1} assumption
          </div>
        </div>
      </div>

      <div className="tab-list" role="tablist" aria-label="Analytics sections" style={{ marginBottom: '20px' }}>
        {ANALYTICS_TABS.map((tab, idx) => {
          const selected = activeTab === tab.id
          return (
            <button
              key={tab.id}
              id={`ana-tab-${tab.id}`}
              type="button"
              role="tab"
              className="tab-btn"
              aria-selected={selected}
              tabIndex={selected ? 0 : -1}
              onClick={() => setActiveTab(tab.id)}
              onKeyDown={(e) => handleTabKeyDown(e, idx)}
            >
              {tab.label}
            </button>
          )
        })}
      </div>

      <div
        id="ana-panel-overview"
        role="tabpanel"
        aria-labelledby="ana-tab-overview"
        hidden={activeTab !== 'overview'}
      >
        <div className="two-col-grid">
          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>Dual-Gate Abstention Impact</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              Removing the intent gate drops OOC rejection from 15/15 (100%) to 1/15 (6.7%) at θ_sim = 0.15.
            </p>
            <DualGateChart rows={data.dual_gate_ablation} />
          </div>

          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>120-Query Breakdown by Type</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              Includes 35 verbatim normal questions alongside paraphrase, typo, and out-of-corpus queries.
            </p>
            <div className="table-wrapper" tabIndex={0} role="region" aria-label="120-query summary by type">
              <table className="data-table">
                <thead>
                  <tr>
                    <th scope="col">Subset</th>
                    <th scope="col">N</th>
                    <th scope="col">MRR</th>
                    <th scope="col">Hit@1</th>
                    <th scope="col">Intent Acc</th>
                    <th scope="col">E2E Acc@1</th>
                  </tr>
                </thead>
                <tbody>
                  {data.midterm_summary.map((row) => (
                    <tr key={String(row.type)}>
                      <th scope="row" data-label="Subset" className="mono">
                        {String(row.type)}
                      </th>
                      <td data-label="N" className="num">
                        {String(row.n)}
                      </td>
                      <td data-label="MRR" className="num">
                        {row.mrr !== null ? Number(row.mrr).toFixed(3) : 'n/a'}
                      </td>
                      <td data-label="Hit@1" className="num">
                        {row.hit1 !== null ? fmtPct(Number(row.hit1)) : 'n/a'}
                      </td>
                      <td data-label="Intent Acc" className="num">
                        {row.intent_acc !== null ? fmtPct(Number(row.intent_acc)) : 'n/a'}
                      </td>
                      <td data-label="E2E Acc@1" className="num">
                        {row.e2e_acc1 !== null ? fmtPct(Number(row.e2e_acc1)) : 'n/a'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div
        id="ana-panel-cv-confusion"
        role="tabpanel"
        aria-labelledby="ana-tab-cv-confusion"
        hidden={activeTab !== 'cv-confusion'}
      >
        <div className="two-col-grid">
          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>7×7 Intent Confusion Matrix</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              105 in-corpus queries; all 3 errors occur on paraphrases.
            </p>
            <ConfusionMatrixChart data={data.confusion_matrix} />
          </div>

          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>E5b Stratified 5-Fold Cross-Validation</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              Held-out document generalization across 9 classical models (mean ± std).
            </p>
            <IntentCvChart rows={data.intent_cv} />
          </div>
        </div>

        {data.confusion_matrix && data.confusion_matrix.misclassified.length > 0 && (
          <div className="card" style={{ marginTop: '16px' }}>
            <h3 style={{ fontSize: '17px', marginBottom: '10px' }}>Three Misclassified In-Corpus Paraphrases</h3>
            <div className="table-wrapper" tabIndex={0} role="region" aria-label="Misclassified queries">
              <table className="data-table">
                <thead>
                  <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Query</th>
                    <th scope="col">Expected intent</th>
                    <th scope="col">Predicted intent</th>
                    <th scope="col">Posterior</th>
                  </tr>
                </thead>
                <tbody>
                  {data.confusion_matrix.misclassified.map((m) => (
                    <tr key={m.query_id}>
                      <th scope="row" data-label="ID" className="mono">
                        {m.query_id}
                      </th>
                      <td data-label="Query">{m.query}</td>
                      <td data-label="Expected">{m.expected_label}</td>
                      <td data-label="Predicted">{m.pred_label}</td>
                      <td data-label="Posterior" className="num">
                        {(m.intent_conf * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <div
        id="ana-panel-noise-sweep"
        role="tabpanel"
        aria-labelledby="ana-tab-noise-sweep"
        hidden={activeTab !== 'noise-sweep'}
      >
        <div className="two-col-grid">
          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>E3b Synthetic Typo Noise Curve</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              Hit@1 degradation across k = 0..3 character swaps per query.
            </p>
            <NoiseCurveChart rows={data.noise_curve} />
          </div>

          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>E6 Cosine-Only Threshold Sweep</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              146 dev queries without intent gate; shows why cosine alone incurs high false abstention.
            </p>
            <ThresholdSweepChart
              rows={data.threshold_sweep}
              chosenThreshold={data.chosen_threshold}
            />
          </div>
        </div>
      </div>

      <div
        id="ana-panel-business-ablations"
        role="tabpanel"
        aria-labelledby="ana-tab-business-ablations"
        hidden={activeTab !== 'business-ablations'}
      >
        <div className="two-col-grid" style={{ marginBottom: '16px' }}>
          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>Penalty Ratio Cost Sensitivity</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              Penalty units per 1,000 queries across four wrong-answer cost ratios.
            </p>
            <CostSensitivityChart rows={data.cost_sensitivity} />
          </div>

          <div className="card">
            <h2 style={{ fontSize: '19px', marginBottom: '6px' }}>Per-Topic Top-1 vs Delivered Top-3</h2>
            <p className="muted-note" style={{ marginBottom: '12px' }}>
              Excluding abstained queries, Delivered Top-3 reaches 100% on 5 of 7 topics.
            </p>
            <PerIntentResolutionChart rows={data.per_intent_business} />
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '19px' }}>Dev-Set Ablation Tables (146 Queries)</h2>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {Object.keys(data.dev_ablations).map((expKey) => (
                <button
                  key={expKey}
                  type="button"
                  className={`btn btn--sm ${selectedExp === expKey ? 'btn--primary' : 'btn--secondary'}`}
                  onClick={() => setSelectedExp(expKey)}
                >
                  {expKey}
                </button>
              ))}
            </div>
          </div>

          {expRows.length === 0 ? (
            <p className="muted-note">No rows found for {selectedExp}.</p>
          ) : (
            <div className="table-wrapper" tabIndex={0} role="region" aria-label={`Dev ablation ${selectedExp}`}>
              <table className="data-table">
                <thead>
                  <tr>
                    {Object.keys(expRows[0]).map((col) => (
                      <th key={col} scope="col">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {expRows.map((row, idx) => (
                    <tr key={idx}>
                      {Object.entries(row).map(([col, val], colIdx) => {
                        const formatted =
                          typeof val === 'number' && col !== 'run' ? val.toFixed(4) : String(val ?? 'n/a')
                        return colIdx === 0 ? (
                          <th key={col} scope="row" data-label={col} className="mono">
                            {formatted}
                          </th>
                        ) : (
                          <td key={col} data-label={col} className="num">
                            {formatted}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
