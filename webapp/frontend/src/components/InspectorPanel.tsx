import { useState, type KeyboardEvent } from 'react'
import { topicStyle } from '../constants/topics'
import type { ChatResponse } from '../types/api'

interface InspectorPanelProps {
  cosineThreshold: number
  intentThreshold: number
  topK: number
  onChangeCosineThreshold: (val: number) => void
  onChangeIntentThreshold: (val: number) => void
  onChangeTopK: (val: number) => void
  onResetDefaults: () => void
  onReEvaluateTurn: () => void
  canReEvaluate: boolean
  isSubmitting: boolean
  activeTurnResponse: ChatResponse | null
}

type InspectorTabId = 'features' | 'intents' | 'compare'

const TABS: Array<{ id: InspectorTabId; label: string }> = [
  { id: 'features', label: 'Features' },
  { id: 'intents', label: 'Intents' },
  { id: 'compare', label: 'Compare IR' },
]

export function InspectorPanel({
  cosineThreshold,
  intentThreshold,
  topK,
  onChangeCosineThreshold,
  onChangeIntentThreshold,
  onChangeTopK,
  onResetDefaults,
  onReEvaluateTurn,
  canReEvaluate,
  isSubmitting,
  activeTurnResponse,
}: InspectorPanelProps) {
  const [activeTab, setActiveTab] = useState<InspectorTabId>('features')

  const handleTabKeyDown = (e: KeyboardEvent<HTMLButtonElement>, currentIndex: number) => {
    let nextIndex = currentIndex
    if (e.key === 'ArrowRight') nextIndex = (currentIndex + 1) % TABS.length
    else if (e.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + TABS.length) % TABS.length
    else if (e.key === 'Home') nextIndex = 0
    else if (e.key === 'End') nextIndex = TABS.length - 1
    else return

    e.preventDefault()
    const nextTab = TABS[nextIndex]
    setActiveTab(nextTab.id)
    document.getElementById(`insp-tab-${nextTab.id}`)?.focus()
  }

  const explainItems = activeTurnResponse?.explain_top1 ?? []
  const maxContrib = explainItems.length
    ? Math.max(...explainItems.map((x) => x.contribution), 0.001)
    : 1
  const explainSum = explainItems.reduce((acc, item) => acc + item.contribution, 0)

  return (
    <aside className="card inspector-panel" aria-label="Pipeline inspector">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '18px' }}>Pipeline Inspector</h2>
        {activeTurnResponse && (
          <span className="small-meta num">{activeTurnResponse.latency_ms.toFixed(1)} ms</span>
        )}
      </div>

      <div className="slider-group">
        <div className="slider-row">
          <div className="slider-head">
            <label htmlFor="insp-cosine">Cosine floor (θ_sim)</label>
            <span className="num">{cosineThreshold.toFixed(2)}</span>
          </div>
          <input
            id="insp-cosine"
            className="range-input"
            type="range"
            min="0"
            max="0.8"
            step="0.01"
            value={cosineThreshold}
            onChange={(e) => onChangeCosineThreshold(Number(e.target.value))}
          />
        </div>

        <div className="slider-row">
          <div className="slider-head">
            <label htmlFor="insp-intent">Intent gate (θ_intent)</label>
            <span className="num">{intentThreshold.toFixed(2)}</span>
          </div>
          <input
            id="insp-intent"
            className="range-input"
            type="range"
            min="0"
            max="0.95"
            step="0.01"
            value={intentThreshold}
            onChange={(e) => onChangeIntentThreshold(Number(e.target.value))}
          />
        </div>

        <div className="slider-row">
          <div className="slider-head">
            <label htmlFor="insp-topk">Top-K results</label>
            <span className="num">{topK}</span>
          </div>
          <input
            id="insp-topk"
            className="range-input"
            type="range"
            min="1"
            max="8"
            step="1"
            value={topK}
            onChange={(e) => onChangeTopK(Number(e.target.value))}
          />
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn--sm btn--primary"
            disabled={!canReEvaluate || isSubmitting}
            onClick={onReEvaluateTurn}
          >
            Apply to query
          </button>
          <button
            type="button"
            className="btn btn--sm btn--secondary"
            onClick={onResetDefaults}
          >
            Reset
          </button>
        </div>
      </div>

      {activeTurnResponse ? (
        <>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '12px',
              paddingBlock: '10px',
              borderTop: '1px solid var(--line)',
              borderBottom: '1px solid var(--line)',
            }}
          >
            <div>
              <div className="small-meta">Top-1 cosine</div>
              <div className="num" style={{ fontWeight: 500, fontSize: '15px' }}>
                {activeTurnResponse.gate_details.top1_cosine.toFixed(3)}
              </div>
              <div
                className="small-meta"
                style={{
                  color: activeTurnResponse.gate_details.cosine_passed ? 'var(--ok)' : 'var(--danger)',
                }}
              >
                {activeTurnResponse.gate_details.cosine_passed ? 'Pass' : 'Below'}{' '}
                {activeTurnResponse.gate_details.cosine_threshold.toFixed(2)}
              </div>
            </div>
            <div>
              <div className="small-meta">Intent conf</div>
              <div className="num" style={{ fontWeight: 500, fontSize: '15px' }}>
                {(activeTurnResponse.gate_details.intent_confidence * 100).toFixed(1)}%
              </div>
              <div
                className="small-meta"
                style={{
                  color: activeTurnResponse.gate_details.intent_passed ? 'var(--ok)' : 'var(--danger)',
                }}
              >
                {activeTurnResponse.gate_details.intent_passed ? 'Pass' : 'Blocked'}{' '}
                {activeTurnResponse.gate_details.intent_threshold !== null
                  ? `${(activeTurnResponse.gate_details.intent_threshold * 100).toFixed(0)}%`
                  : ''}
              </div>
            </div>
          </div>

          <div>
            <div className="tab-list" role="tablist" aria-label="Inspector trace tabs">
              {TABS.map((tab, idx) => {
                const selected = activeTab === tab.id
                return (
                  <button
                    key={tab.id}
                    id={`insp-tab-${tab.id}`}
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
              id="insp-panel-features"
              role="tabpanel"
              aria-labelledby="insp-tab-features"
              hidden={activeTab !== 'features'}
              className="tab-panel"
            >
              {explainItems.length === 0 ? (
                <p className="muted-note">No overlapping n-grams found.</p>
              ) : (
                <div className="bar-list">
                  <p className="small-meta">
                    Top-10 n-gram sum: <span className="num">{explainSum.toFixed(4)}</span>
                  </p>
                  {explainItems.map((item) => (
                    <div key={item.feature} className="bar-item">
                      <div className="bar-item__head">
                        <code className="mono">{JSON.stringify(item.feature)}</code>
                        <span className="num">+{item.contribution.toFixed(4)}</span>
                      </div>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{ width: `${Math.min(100, (item.contribution / maxContrib) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div
              id="insp-panel-intents"
              role="tabpanel"
              aria-labelledby="insp-tab-intents"
              hidden={activeTab !== 'intents'}
              className="tab-panel"
            >
              <div className="bar-list">
                {activeTurnResponse.intent_probs.map((item) => {
                  const st = topicStyle(item.intent)
                  return (
                    <div key={item.intent} className="bar-item">
                      <div className="bar-item__head">
                        <span style={{ color: st.fg, fontWeight: 500 }}>{item.label}</span>
                        <span className="num">{(item.probability * 100).toFixed(1)}%</span>
                      </div>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${Math.min(100, item.probability * 100)}%`,
                            background: st.fg,
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div
              id="insp-panel-compare"
              role="tabpanel"
              aria-labelledby="insp-tab-compare"
              hidden={activeTab !== 'compare'}
              className="tab-panel"
            >
              {activeTurnResponse.comparison ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {(
                    [
                      ['char_wb (3–5) TF-IDF', activeTurnResponse.comparison.char_wb, false],
                      ['Word TF-IDF', activeTurnResponse.comparison.word_tfidf, false],
                      ['Okapi BM25', activeTurnResponse.comparison.bm25, true],
                    ] as const
                  ).map(([heading, list, unbounded]) => (
                    <div key={heading} style={{ borderBottom: '1px solid var(--line)', paddingBottom: '10px' }}>
                      <div style={{ fontWeight: 500, fontSize: '13px', marginBottom: '6px' }}>{heading}</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {list.map((doc, idx) => (
                          <div
                            key={doc.id}
                            style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', fontSize: '13px' }}
                          >
                            <code className="mono">
                              #{idx + 1} {doc.id}
                            </code>
                            <span className="num" style={{ color: 'var(--muted)' }}>
                              {unbounded ? doc.score.toFixed(2) : doc.score.toFixed(3)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted-note">No 3-way comparison available.</p>
              )}
            </div>
          </div>
        </>
      ) : (
        <p className="muted-note">Ask a question to inspect feature weights, probabilities, and retriever rankings.</p>
      )}
    </aside>
  )
}
