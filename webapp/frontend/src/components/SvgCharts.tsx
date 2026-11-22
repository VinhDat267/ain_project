import { useState } from 'react'
import type { AnalyticsPayload, ConfusionMatrixData } from '../types/api'

const RULE_LABELS: Record<string, string> = {
  no_gate: 'No gate',
  cosine_only: 'Cosine >= 0.15',
  intent_only: 'Intent >= 0.34',
  dual: 'Dual gate (0.15 / 0.34)',
}

const METHOD_STYLE: Record<string, { label: string; color: string; dash?: string }> = {
  char: { label: 'char_wb TF-IDF', color: '#0d7480' },
  hybrid: { label: 'Hybrid (alpha 0.5)', color: '#1d4ed8', dash: '6 4' },
  word: { label: 'Word TF-IDF', color: '#b45309', dash: '3 3' },
  jaccard: { label: 'Jaccard overlap', color: '#5d6b72', dash: '8 4 2 4' },
}

export function DualGateChart({
  rows,
}: {
  rows: AnalyticsPayload['dual_gate_ablation']
}) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null)
  if (!rows.length) return <p className="muted-note">Dual-gate ablation data unavailable.</p>

  const W = 560
  const H = 260
  const margin = { top: 20, right: 20, bottom: 48, left: 48 }
  const plotW = W - margin.left - margin.right
  const plotH = H - margin.top - margin.bottom
  const groupW = plotW / rows.length
  const barW = Math.min(34, groupW * 0.28)
  const yOf = (rate: number) => margin.top + plotH * (1 - rate)

  const activeRow = hoverIdx !== null ? rows[hoverIdx] : rows[rows.length - 1]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
        <div style={{ display: 'flex', gap: '14px', fontSize: '13px', alignItems: 'center' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: 12, height: 12, background: '#0d7480', borderRadius: 2, display: 'inline-block' }} />
            E2E Accuracy (120q)
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: 12, height: 12, background: '#1f3038', borderRadius: 2, display: 'inline-block' }} />
            OOC Rejection (15q)
          </span>
        </div>
        {activeRow && (
          <div className="small-meta num" aria-live="polite">
            {RULE_LABELS[activeRow.rule] ?? activeRow.rule}:{' '}
            {activeRow.correct}/{activeRow.total} E2E, {activeRow.ooc_rejected}/{activeRow.ooc_total} OOC
          </div>
        )}
      </div>

      <div className="chart-box">
        <svg
          className="chart-svg"
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Grouped bar chart comparing End-to-End Accuracy and Out-of-Corpus Rejection across four gate rules"
        >
          <title>Dual-Gate Ablation on 120 Queries</title>
          {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
            const y = yOf(tick)
            return (
              <g key={tick}>
                <line x1={margin.left} y1={y} x2={W - margin.right} y2={y} stroke="#dbe2e6" strokeDasharray={tick === 0 ? undefined : '4 4'} />
                <text x={margin.left - 8} y={y + 4} textAnchor="end" fontSize="11" fill="#5d6b72" fontFamily="var(--font-mono)">
                  {Math.round(tick * 100)}%
                </text>
              </g>
            )
          })}

          {rows.map((row, i) => {
            const e2e = row.total ? row.correct / row.total : 0
            const ooc = row.ooc_total ? row.ooc_rejected / row.ooc_total : 0
            const cx = margin.left + groupW * (i + 0.5)
            const x1 = cx - barW - 3
            const x2 = cx + 3
            const y1 = yOf(e2e)
            const y2 = yOf(ooc)
            const h1 = margin.top + plotH - y1
            const h2 = margin.top + plotH - y2
            return (
              <g
                key={row.rule}
                tabIndex={0}
                onMouseEnter={() => setHoverIdx(i)}
                onFocus={() => setHoverIdx(i)}
                onMouseLeave={() => setHoverIdx(null)}
                style={{ cursor: 'pointer' }}
              >
                <rect x={x1} y={y1} width={barW} height={h1} rx={3} fill="#0d7480" />
                <text x={x1 + barW / 2} y={y1 - 6} textAnchor="middle" fontSize="11" fill="#1f3038" fontFamily="var(--font-mono)">
                  {(e2e * 100).toFixed(1)}%
                </text>
                <rect x={x2} y={y2} width={barW} height={h2} rx={3} fill="#1f3038" />
                <text x={x2 + barW / 2} y={y2 - 6} textAnchor="middle" fontSize="11" fill="#1f3038" fontFamily="var(--font-mono)">
                  {Math.round(ooc * 100)}%
                </text>
                <text x={cx} y={H - 18} textAnchor="middle" fontSize="12" fill="#1f3038">
                  {RULE_LABELS[row.rule] ?? row.rule}
                </text>
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}

export function ConfusionMatrixChart({ data }: { data: ConfusionMatrixData | null }) {
  const [selectedCell, setSelectedCell] = useState<{ r: number; c: number } | null>(null)
  if (!data) return <p className="muted-note">Confusion matrix unavailable.</p>

  const n = data.labels.length
  const cell = 44
  const left = 112
  const top = 26
  const right = 24
  const bottom = 92
  const W = left + n * cell + right
  const H = top + n * cell + bottom
  const maxVal = Math.max(...data.matrix.flat(), 1)

  const cellText = (() => {
    if (!selectedCell) return `${data.correct}/${data.total} in-corpus correct (${(data.accuracy * 100).toFixed(1)}%)`
    const val = data.matrix[selectedCell.r][selectedCell.c]
    return `True: ${data.display_labels[selectedCell.r]} -> Pred: ${data.display_labels[selectedCell.c]} (${val} queries)`
  })()

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
        <span className="small-meta">Hover or focus any cell to inspect counts</span>
        <span className="badge num" aria-live="polite">
          {cellText}
        </span>
      </div>

      <div className="chart-box">
        <svg
          className="chart-svg"
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label={`7 by 7 intent confusion matrix showing ${data.correct} correct predictions out of ${data.total} in-corpus queries`}
        >
          <title>7x7 Intent Confusion Matrix</title>
          {data.matrix.map((row, r) => (
            <g key={data.labels[r]}>
              <text
                x={left - 10}
                y={top + r * cell + cell / 2 + 4}
                textAnchor="end"
                fontSize="12"
                fill="#1f3038"
              >
                {data.display_labels[r]}
              </text>
              {row.map((val, c) => {
                const x = left + c * cell
                const y = top + r * cell
                const isDiag = r === c
                const ratio = val / maxVal
                let fill = '#f2f5f7'
                let textFill = '#9ea7ab'
                if (val > 0 && isDiag) {
                  fill = ratio > 0.65 ? '#0d7480' : '#4a98a2'
                  textFill = '#ffffff'
                } else if (val > 0) {
                  fill = '#f6b8c7'
                  textFill = '#881337'
                }
                const isFocused = selectedCell?.r === r && selectedCell?.c === c
                return (
                  <g
                    key={`${r}-${c}`}
                    tabIndex={0}
                    onMouseEnter={() => setSelectedCell({ r, c })}
                    onFocus={() => setSelectedCell({ r, c })}
                    onMouseLeave={() => setSelectedCell(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    <rect
                      x={x + 1.5}
                      y={y + 1.5}
                      width={cell - 3}
                      height={cell - 3}
                      rx={4}
                      fill={fill}
                      stroke={isFocused ? '#1f3038' : '#e2e8ec'}
                      strokeWidth={isFocused ? 2 : 1}
                    />
                    <text
                      x={x + cell / 2}
                      y={y + cell / 2 + 5}
                      textAnchor="middle"
                      fontSize="13"
                      fontWeight={val > 0 ? 500 : 400}
                      fontFamily="var(--font-mono)"
                      fill={textFill}
                    >
                      {val}
                    </text>
                  </g>
                )
              })}
            </g>
          ))}

          {data.display_labels.map((label, c) => {
            const tx = left + c * cell + cell / 2
            const ty = top + n * cell + 14
            return (
              <text
                key={label}
                x={tx}
                y={ty}
                transform={`rotate(-32 ${tx} ${ty})`}
                textAnchor="end"
                fontSize="12"
                fill="#1f3038"
              >
                {label}
              </text>
            )
          })}
          <text
            x={left + (n * cell) / 2}
            y={H - 8}
            textAnchor="middle"
            fontSize="12"
            fontWeight={500}
            fill="#5d6b72"
          >
            Predicted intent
          </text>
        </svg>
      </div>
    </div>
  )
}

export function IntentCvChart({ rows }: { rows: AnalyticsPayload['intent_cv'] }) {
  if (!rows.length) return <p className="muted-note">Cross-validation results unavailable.</p>

  const sorted = [...rows].sort((a, b) => b.acc_mean - a.acc_mean)
  const W = 560
  const rowH = 34
  const margin = { top: 20, right: 90, bottom: 36, left: 118 }
  const H = margin.top + sorted.length * rowH + margin.bottom
  const plotW = W - margin.left - margin.right
  const xOf = (val: number) => margin.left + Math.max(0, Math.min(1, val)) * plotW

  return (
    <div className="chart-box">
      <svg
        className="chart-svg"
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label="5-fold cross-validation accuracy with standard deviation error bars for 9 classical classifiers"
      >
        <title>5-Fold Cross-Validation Accuracy Across 9 Models</title>
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
          const x = xOf(tick)
          return (
            <g key={tick}>
              <line x1={x} y1={margin.top} x2={x} y2={H - margin.bottom} stroke="#dbe2e6" strokeDasharray="4 4" />
              <text x={x} y={H - 12} textAnchor="middle" fontSize="11" fill="#5d6b72" fontFamily="var(--font-mono)">
                {Math.round(tick * 100)}%
              </text>
            </g>
          )
        })}

        {sorted.map((row, idx) => {
          const cy = margin.top + idx * rowH + rowH / 2
          const isBest = row.model === 'logreg_tfidf'
          const xMean = xOf(row.acc_mean)
          const xLow = xOf(row.acc_mean - row.acc_std)
          const xHigh = xOf(row.acc_mean + row.acc_std)
          const barColor = isBest ? '#0d7480' : '#3d515b'
          return (
            <g key={row.model}>
              <text
                x={margin.left - 10}
                y={cy + 4}
                textAnchor="end"
                fontSize="12"
                fontWeight={isBest ? 600 : 400}
                fontFamily="var(--font-mono)"
                fill={isBest ? '#0d7480' : '#1f3038'}
              >
                {row.model}
              </text>
              <line x1={xOf(0)} y1={cy} x2={xMean} y2={cy} stroke={barColor} strokeWidth={isBest ? 6 : 4} strokeLinecap="round" opacity={isBest ? 0.35 : 0.2} />
              <line x1={xLow} y1={cy} x2={xHigh} y2={cy} stroke={barColor} strokeWidth={2} />
              <line x1={xLow} y1={cy - 5} x2={xLow} y2={cy + 5} stroke={barColor} strokeWidth={2} />
              <line x1={xHigh} y1={cy - 5} x2={xHigh} y2={cy + 5} stroke={barColor} strokeWidth={2} />
              <circle cx={xMean} cy={cy} r={isBest ? 5.5 : 4.5} fill={barColor} />
              <text
                x={W - 6}
                y={cy + 4}
                textAnchor="end"
                fontSize="11"
                fontFamily="var(--font-mono)"
                fill={isBest ? '#0d7480' : '#5d6b72'}
              >
                {(row.acc_mean * 100).toFixed(1)}% ± {(row.acc_std * 100).toFixed(1)}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

export function NoiseCurveChart({ rows }: { rows: AnalyticsPayload['noise_curve'] }) {
  const [selectedK, setSelectedK] = useState<number>(3)
  if (!rows.length) return <p className="muted-note">Noise curve data unavailable.</p>

  const methods = ['char', 'hybrid', 'word', 'jaccard']
  const ks = [0, 1, 2, 3]
  const W = 560
  const H = 260
  const margin = { top: 20, right: 44, bottom: 44, left: 50 }
  const plotW = W - margin.left - margin.right
  const plotH = H - margin.top - margin.bottom

  const xOf = (k: number) => margin.left + (k / 3) * plotW
  const yOf = (hit1: number) => margin.top + plotH * (1 - Math.max(0, Math.min(1, (hit1 - 0.75) / 0.27)))

  const lookup = (method: string, k: number) =>
    rows.find((r) => r.method === method && Number(r.k) === k)?.hit1 ?? 0

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', fontSize: '12px' }}>
          {methods.map((m) => (
            <span key={m} style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ width: 14, height: 3, background: METHOD_STYLE[m].color, display: 'inline-block' }} />
              {METHOD_STYLE[m].label}
            </span>
          ))}
        </div>
        <span className="small-meta num" aria-live="polite">
          k={selectedK}: char {(lookup('char', selectedK) * 100).toFixed(1)}% | word {(lookup('word', selectedK) * 100).toFixed(1)}%
        </span>
      </div>

      <div className="chart-box">
        <svg
          className="chart-svg"
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Hit at 1 robustness under 0 to 3 character swaps per query for 4 retrieval methods"
        >
          <title>Retrieval Robustness Under Synthetic Character Noise (E3b)</title>
          {[0.8, 0.85, 0.9, 0.95, 1.0].map((tick) => {
            const y = yOf(tick)
            return (
              <g key={tick}>
                <line x1={margin.left} y1={y} x2={W - margin.right} y2={y} stroke="#dbe2e6" strokeDasharray="4 4" />
                <text x={margin.left - 8} y={y + 4} textAnchor="end" fontSize="11" fill="#5d6b72" fontFamily="var(--font-mono)">
                  {Math.round(tick * 100)}%
                </text>
              </g>
            )
          })}

          {ks.map((k) => {
            const x = xOf(k)
            const active = selectedK === k
            return (
              <g key={k} style={{ cursor: 'pointer' }} tabIndex={0} onClick={() => setSelectedK(k)} onFocus={() => setSelectedK(k)} onMouseEnter={() => setSelectedK(k)}>
                <line x1={x} y1={margin.top} x2={x} y2={H - margin.bottom} stroke={active ? '#0d7480' : '#ecf0f2'} strokeWidth={active ? 2 : 1} />
                <text x={x} y={H - 16} textAnchor="middle" fontSize="12" fontFamily="var(--font-mono)" fill={active ? '#0d7480' : '#1f3038'}>
                  k={k} swaps
                </text>
              </g>
            )
          })}

          {methods.map((m) => {
            const pts = ks.map((k) => `${xOf(k)},${yOf(lookup(m, k))}`).join(' ')
            const st = METHOD_STYLE[m]
            return (
              <g key={m}>
                <polyline fill="none" stroke={st.color} strokeWidth={m === 'char' ? 3 : 2} strokeDasharray={st.dash} points={pts} />
                {ks.map((k) => (
                  <circle key={`${m}-${k}`} cx={xOf(k)} cy={yOf(lookup(m, k))} r={4} fill={st.color} stroke="#ffffff" strokeWidth={1.5} />
                ))}
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}

export function ThresholdSweepChart({
  rows,
  chosenThreshold,
}: {
  rows: AnalyticsPayload['threshold_sweep']
  chosenThreshold: number | null
}) {
  const [inspectTheta, setInspectTheta] = useState<number>(chosenThreshold ?? 0.33)
  if (!rows.length) return <p className="muted-note">Threshold sweep data unavailable.</p>

  const W = 560
  const H = 260
  const margin = { top: 20, right: 20, bottom: 44, left: 48 }
  const plotW = W - margin.left - margin.right
  const plotH = H - margin.top - margin.bottom

  const xOf = (t: number) => margin.left + t * plotW
  const yOf = (v: number) => margin.top + plotH * (1 - v)

  const currentRow =
    rows.reduce((prev, curr) =>
      Math.abs(curr.threshold - inspectTheta) < Math.abs(prev.threshold - inspectTheta) ? curr : prev,
    )

  const series = [
    { key: 'balanced_e2e' as const, label: 'Balanced E2E', color: '#0d7480' },
    { key: 'ooc_rejection' as const, label: 'OOC rejection', color: '#047857' },
    { key: 'false_abstention' as const, label: 'False abstention', color: '#be123c' },
  ]

  const chosenX = xOf(chosenThreshold ?? 0.33)

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', fontSize: '12px' }}>
          {series.map((s) => (
            <span key={s.key} style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ width: 12, height: 3, background: s.color, display: 'inline-block' }} />
              {s.label}
            </span>
          ))}
        </div>
        <span className="small-meta num" aria-live="polite">
          θ={currentRow.threshold.toFixed(2)}: Bal {(currentRow.balanced_e2e * 100).toFixed(1)}% | OOC{' '}
          {(currentRow.ooc_rejection * 100).toFixed(1)}% | False-Abst{' '}
          {(currentRow.false_abstention * 100).toFixed(1)}%
        </span>
      </div>

      <div className="chart-box">
        <svg
          className="chart-svg"
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Cosine-only threshold sweep from 0.00 to 1.00 across 146 dev queries showing peak balanced end-to-end accuracy at 0.33"
        >
          <title>Cosine-Only Threshold Sweep on 146 Dev Queries (E6)</title>
          {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
            const y = yOf(tick)
            return (
              <g key={tick}>
                <line x1={margin.left} y1={y} x2={W - margin.right} y2={y} stroke="#dbe2e6" strokeDasharray="4 4" />
                <text x={margin.left - 8} y={y + 4} textAnchor="end" fontSize="11" fill="#5d6b72" fontFamily="var(--font-mono)">
                  {Math.round(tick * 100)}%
                </text>
              </g>
            )
          })}

          {[0, 0.2, 0.4, 0.6, 0.8, 1.0].map((tick) => (
            <text
              key={tick}
              x={xOf(tick)}
              y={H - 16}
              textAnchor="middle"
              fontSize="11"
              fill="#5d6b72"
              fontFamily="var(--font-mono)"
            >
              {tick.toFixed(1)}
            </text>
          ))}

          <line x1={chosenX} y1={margin.top} x2={chosenX} y2={H - margin.bottom} stroke="#1f3038" strokeDasharray="5 4" strokeWidth={1.5} />
          <text
            x={chosenX + 6}
            y={margin.top + plotH * 0.48}
            fontSize="11"
            fontFamily="var(--font-mono)"
            fill="#1f3038"
            style={{ paintOrder: 'stroke', stroke: '#ffffff', strokeWidth: 4, strokeLinejoin: 'round' }}
          >
            dev opt θ={(chosenThreshold ?? 0.33).toFixed(2)}
          </text>

          {series.map((s) => {
            const pts = rows.map((r) => `${xOf(r.threshold)},${yOf(r[s.key])}`).join(' ')
            return <polyline key={s.key} fill="none" stroke={s.color} strokeWidth={2.5} points={pts} />
          })}
        </svg>
      </div>

      <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label htmlFor="sweep-scrubber" className="small-meta" style={{ whiteSpace: 'nowrap' }}>
          Inspect θ:
        </label>
        <input
          id="sweep-scrubber"
          className="range-input"
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={inspectTheta}
          onChange={(e) => setInspectTheta(Number(e.target.value))}
        />
      </div>
    </div>
  )
}

export function CostSensitivityChart({ rows }: { rows: AnalyticsPayload['cost_sensitivity'] }) {
  if (!rows.length) return <p className="muted-note">Cost sensitivity data unavailable.</p>

  const W = 520
  const H = 220
  const margin = { top: 20, right: 20, bottom: 40, left: 52 }
  const plotW = W - margin.left - margin.right
  const plotH = H - margin.top - margin.bottom
  const maxCost = Math.max(...rows.map((r) => r.cost_per_1000_queries), 100)
  const barW = Math.min(48, (plotW / rows.length) * 0.45)

  return (
    <div className="chart-box">
      <svg
        className="chart-svg"
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label="Penalty units per 1000 queries under four wrong-answer cost ratios"
      >
        <title>Business Penalty Cost Sensitivity (Units per 1,000 Queries)</title>
        {[0, 0.5, 1].map((f) => {
          const y = margin.top + plotH * (1 - f)
          return (
            <g key={f}>
              <line x1={margin.left} y1={y} x2={W - margin.right} y2={y} stroke="#dbe2e6" strokeDasharray="4 4" />
              <text x={margin.left - 8} y={y + 4} textAnchor="end" fontSize="11" fill="#5d6b72" fontFamily="var(--font-mono)">
                {Math.round(maxCost * f)}
              </text>
            </g>
          )
        })}

        {rows.map((row, idx) => {
          const cx = margin.left + (plotW / rows.length) * (idx + 0.5)
          const h = (row.cost_per_1000_queries / maxCost) * plotH
          const y = margin.top + plotH - h
          return (
            <g key={row.penalty_ratio}>
              <rect
                x={cx - barW / 2}
                y={y}
                width={barW}
                height={h}
                rx={4}
                fill={row.penalty_ratio === '5:1' ? '#0d7480' : '#3d515b'}
              />
              <text x={cx} y={y - 6} textAnchor="middle" fontSize="11" fill="#1f3038" fontFamily="var(--font-mono)">
                {row.cost_per_1000_queries.toFixed(0)}
              </text>
              <text x={cx} y={H - 16} textAnchor="middle" fontSize="12" fill="#1f3038" fontFamily="var(--font-mono)">
                {row.penalty_ratio}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

export function PerIntentResolutionChart({
  rows,
}: {
  rows: AnalyticsPayload['per_intent_business']
}) {
  const intents = rows.filter((r) => r.segment_type === 'intent')
  if (!intents.length) return <p className="muted-note">Per-intent metrics unavailable.</p>

  const W = 580
  const rowH = 34
  const margin = { top: 20, right: 92, bottom: 28, left: 158 }
  const H = margin.top + intents.length * rowH + margin.bottom
  const plotW = W - margin.left - margin.right

  return (
    <div>
      <div style={{ display: 'flex', gap: '14px', fontSize: '12px', marginBottom: '10px' }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ width: 12, height: 8, background: '#1f3038', borderRadius: 2, display: 'inline-block' }} />
          Top-1 resolution
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ width: 12, height: 8, background: '#0d7480', borderRadius: 2, display: 'inline-block' }} />
          Delivered Top-3
        </span>
      </div>
      <div className="chart-box">
        <svg
          className="chart-svg"
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Top-1 resolution versus Delivered Top-3 rate across the 7 campus topics"
        >
          <title>Per-Intent Resolution Rates</title>
          {intents.map((item, idx) => {
            const yBase = margin.top + idx * rowH + 6
            const w1 = item.resolution_rate_top1 * plotW
            const w3 = item.top3_rescue_rate * plotW
            return (
              <g key={item.segment_name}>
                <text x={margin.left - 10} y={yBase + 16} textAnchor="end" fontSize="12" fontFamily="var(--font-mono)" fill="#1f3038">
                  {item.segment_name}
                </text>
                <rect x={margin.left} y={yBase} width={w1} height={9} rx={2} fill="#1f3038" />
                <rect x={margin.left} y={yBase + 11} width={w3} height={9} rx={2} fill="#0d7480" />
                <text x={W - 6} y={yBase + 17} textAnchor="end" fontSize="11" fontFamily="var(--font-mono)" fill="#1f3038">
                  {(item.resolution_rate_top1 * 100).toFixed(0)}% / {(item.top3_rescue_rate * 100).toFixed(0)}%
                </text>
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}
