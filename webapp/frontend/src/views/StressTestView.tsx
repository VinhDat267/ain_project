import { useEffect, useState } from 'react'
import { runStressTest } from '../api/client'
import type { StressPreset, StressTestResponse } from '../types/api'

interface StressTestViewProps {
  defaultCosine: number
  defaultIntent: number
  onAskInAssistant: (query: string) => void
}

const PRESET_OPTIONS: Array<{ id: StressPreset; label: string }> = [
  { id: 'demo_6', label: 'Defense 6' },
  { id: 'balanced_16', label: 'Balanced 16' },
  { id: 'benchmark_120', label: 'Benchmark 120' },
  { id: 'custom', label: 'Custom batch' },
]

function statusBadgeClass(status: string): string {
  if (status === 'top1_pass' || status === 'ooc_rejected' || status === 'answered') {
    return 'badge badge--ok'
  }
  if (status === 'top3_rescue' || status === 'false_abstain') {
    return 'badge badge--warn'
  }
  if (status === 'wrong_answer' || status === 'ooc_leaked') {
    return 'badge badge--danger'
  }
  return 'badge'
}

export function StressTestView({
  defaultCosine,
  defaultIntent,
  onAskInAssistant,
}: StressTestViewProps) {
  const [preset, setPreset] = useState<StressPreset>('demo_6')
  const [cosine, setCosine] = useState(defaultCosine)
  const [intentGate, setIntentGate] = useState(defaultIntent)
  const [customText, setCustomText] = useState(
    'Can I rent a kayak from the campus recreation center?\nWhere do I go to see my current classes and times?\nHow do I reset my Sutdent Portal password?',
  )
  const [result, setResult] = useState<StressTestResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const executeBatch = async (chosenPreset: StressPreset, cVal = cosine, iVal = intentGate) => {
    setLoading(true)
    setError(null)
    setPreset(chosenPreset)
    try {
      const data = await runStressTest({
        preset: chosenPreset,
        custom_queries:
          chosenPreset === 'custom'
            ? customText
                .split('\n')
                .map((s) => s.trim())
                .filter(Boolean)
            : [],
        threshold: cVal,
        intent_threshold: iVal,
        top_k: 3,
      })
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Stress-test request failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void executeBatch('demo_6', defaultCosine, defaultIntent)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <section aria-labelledby="stress-heading">
      <div className="view-head">
        <div>
          <h1 id="stress-heading">Stress-Test Lab</h1>
          <p className="view-lead">
            Evaluate fixed presets or custom prompts live against both abstention gates.
          </p>
        </div>
      </div>

      <div className="card toolbar-card">
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {PRESET_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`btn btn--sm ${preset === opt.id ? 'btn--primary' : 'btn--secondary'}`}
              disabled={loading}
              onClick={() => {
                if (opt.id === 'custom') {
                  setPreset('custom')
                } else {
                  void executeBatch(opt.id)
                }
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div className="inline-sliders">
          <div className="inline-slider-item">
            <div className="slider-head">
              <label htmlFor="stress-cosine">θ_sim</label>
              <span className="num">{cosine.toFixed(2)}</span>
            </div>
            <input
              id="stress-cosine"
              className="range-input"
              type="range"
              min="0"
              max="0.8"
              step="0.01"
              value={cosine}
              onChange={(e) => setCosine(Number(e.target.value))}
            />
          </div>

          <div className="inline-slider-item">
            <div className="slider-head">
              <label htmlFor="stress-intent">θ_intent</label>
              <span className="num">{intentGate.toFixed(2)}</span>
            </div>
            <input
              id="stress-intent"
              className="range-input"
              type="range"
              min="0"
              max="0.95"
              step="0.01"
              value={intentGate}
              onChange={(e) => setIntentGate(Number(e.target.value))}
            />
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn--sm btn--primary"
              disabled={loading}
              onClick={() => {
                void executeBatch(preset)
              }}
            >
              Apply
            </button>
            <button
              type="button"
              className="btn btn--sm btn--ghost"
              disabled={loading}
              onClick={() => {
                setCosine(defaultCosine)
                setIntentGate(defaultIntent)
                if (preset !== 'custom') {
                  void executeBatch(preset, defaultCosine, defaultIntent)
                }
              }}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {preset === 'custom' && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <label htmlFor="custom-stress-queries" className="field-label">
            Custom questions (one per line, up to 50)
          </label>
          <textarea
            id="custom-stress-queries"
            className="text-area"
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
            <button
              type="button"
              className="btn btn--sm btn--primary"
              disabled={loading || !customText.trim()}
              onClick={() => {
                void executeBatch('custom')
              }}
            >
              Run custom batch
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="abstention-block" style={{ marginBottom: '20px' }} role="alert">
          <div className="abstention-block__title">Batch run failed</div>
          <p className="muted-note">{error}</p>
        </div>
      )}

      {result && (
        <>
          <div className="metric-strip" aria-live="polite">
            <div className="metric-cell">
              <div className="metric-cell__label">Evaluated</div>
              <div className="metric-cell__value num">{result.summary.total}</div>
              <div className="metric-cell__note">
                {result.summary.answered} answered · {result.summary.abstained} abstained
              </div>
            </div>
            <div className="metric-cell">
              <div className="metric-cell__label">Delivered Top-3</div>
              <div className="metric-cell__value num">
                {result.summary.in_corpus_total > 0
                  ? `${result.summary.top3_delivered}/${result.summary.in_corpus_total}`
                  : 'n/a'}
              </div>
              <div className="metric-cell__note">
                Top-1: {result.summary.top1_correct} · False-abst: {result.summary.false_abstentions}
              </div>
            </div>
            <div className="metric-cell">
              <div className="metric-cell__label">OOC Rejected</div>
              <div className="metric-cell__value num">
                {result.summary.ooc_total > 0
                  ? `${result.summary.ooc_rejected}/${result.summary.ooc_total}`
                  : `${result.summary.abstained}`}
              </div>
              <div className="metric-cell__note">Leaked: {result.summary.ooc_leaked}</div>
            </div>
            <div className="metric-cell">
              <div className="metric-cell__label">Mean Latency</div>
              <div className="metric-cell__value num">{result.summary.mean_latency_ms.toFixed(2)} ms</div>
              <div className="metric-cell__note">
                θ_sim {result.threshold.toFixed(2)} / θ_intent {result.intent_threshold?.toFixed(2) ?? 'off'}
              </div>
            </div>
          </div>

          <div className="table-wrapper" tabIndex={0} role="region" aria-label="Stress-test evaluation results">
            <table className="data-table">
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th scope="col">Type</th>
                  <th scope="col">Query</th>
                  <th scope="col">Outcome</th>
                  <th scope="col">Cosine</th>
                  <th scope="col">Intent</th>
                  <th scope="col">Top-1 / Expected</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row) => (
                  <tr key={row.query_id}>
                    <th scope="row" data-label="ID" className="mono">
                      {row.query_id}
                    </th>
                    <td data-label="Type">{row.query_type}</td>
                    <td data-label="Query">{row.query}</td>
                    <td data-label="Outcome">
                      <span className={statusBadgeClass(row.status)}>{row.status}</span>
                    </td>
                    <td data-label="Cosine" className="num">
                      {row.top1_cosine.toFixed(3)}
                    </td>
                    <td data-label="Intent" className="num">
                      {(row.intent_confidence * 100).toFixed(0)}%
                    </td>
                    <td data-label="Top-1 / Expected" className="mono">
                      {row.top1_doc_id ?? 'abstained'}
                      {row.expected_doc_id ? ` / ${row.expected_doc_id}` : ''}
                    </td>
                    <td data-label="Action">
                      <button
                        type="button"
                        className="link-btn"
                        onClick={() => onAskInAssistant(row.query)}
                      >
                        Try in assistant
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  )
}
