import { useEffect, useRef, useState, type FormEvent } from 'react'
import { fetchDocuments, submitFeedback } from '../api/client'
import { HighlightedText } from '../components/HighlightedText'
import { InspectorPanel } from '../components/InspectorPanel'
import { STARTER_PROMPTS, topicStyle } from '../constants/topics'
import type { ChatTurn, DomainCatalogItem } from '../types/api'

interface AssistantViewProps {
  turns: ChatTurn[]
  selectedTurnId: string | null
  onSelectTurn: (turnId: string) => void
  onSubmitQuery: (queryText: string) => Promise<void>
  onClearHistory: () => void
  onMarkFeedback: (turnId: string, helpful: boolean) => void
  onOpenDocumentById: (docId: string) => void
  inspectorOpen: boolean
  onToggleInspector: () => void
  cosineThreshold: number
  intentThreshold: number
  topK: number
  onChangeCosineThreshold: (val: number) => void
  onChangeIntentThreshold: (val: number) => void
  onChangeTopK: (val: number) => void
  onResetDefaults: () => void
  isSubmitting: boolean
  submitError: string | null
}

export function AssistantView({
  turns,
  selectedTurnId,
  onSelectTurn,
  onSubmitQuery,
  onClearHistory,
  onMarkFeedback,
  onOpenDocumentById,
  inspectorOpen,
  onToggleInspector,
  cosineThreshold,
  intentThreshold,
  topK,
  onChangeCosineThreshold,
  onChangeIntentThreshold,
  onChangeTopK,
  onResetDefaults,
  isSubmitting,
  submitError,
}: AssistantViewProps) {
  const [draftQuery, setDraftQuery] = useState('')
  const [feedbackNotice, setFeedbackNotice] = useState<string>('')
  const prevTurnCountRef = useRef(turns.length)
  const latestTurnRef = useRef<HTMLElement | null>(null)
  const [catalog, setCatalog] = useState<DomainCatalogItem[]>([])

  useEffect(() => {
    let cancelled = false
    fetchDocuments()
      .then((res) => {
        if (!cancelled) setCatalog(res.catalog)
      })
      .catch(() => {
        if (!cancelled) setCatalog([])
      })
    return () => {
      cancelled = true
    }
  }, [])

  // The cosine floor sits beside the question box, as the assignment asks; it applies to the next question.
  const thresholdControl = (
    <div className="threshold-row">
      <label htmlFor="cosine-threshold-input" className="field-label">
        Cosine threshold
      </label>
      <input
        id="cosine-threshold-input"
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={cosineThreshold}
        onChange={(e) => onChangeCosineThreshold(Number(e.target.value))}
      />
      <span className="num threshold-row__value">{cosineThreshold.toFixed(2)}</span>
      <span className="small-meta">intent gate {Math.round(intentThreshold * 100)}% · applies to the next question</span>
    </div>
  )

  useEffect(() => {
    if (turns.length > prevTurnCountRef.current) {
      latestTurnRef.current?.scrollIntoView({ behavior: 'auto', block: 'start' })
    }
    prevTurnCountRef.current = turns.length
  }, [turns.length])

  const activeTurn =
    turns.find((t) => t.id === selectedTurnId) ?? turns[turns.length - 1] ?? null

  const handleFormSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const trimmed = draftQuery.trim()
    if (!trimmed || isSubmitting) return
    setDraftQuery('')
    await onSubmitQuery(trimmed)
  }

  const handleFeedback = async (turn: ChatTurn, helpful: boolean) => {
    const targetDocId = turn.response.results[0]?.id ?? 'abstained'
    try {
      await submitFeedback({
        query: turn.response.query,
        doc_id: targetDocId,
        helpful,
      })
      onMarkFeedback(turn.id, helpful)
      setFeedbackNotice(
        helpful ? `Marked ${targetDocId} as helpful.` : `Logged issue for ${targetDocId}.`,
      )
    } catch (err) {
      setFeedbackNotice(err instanceof Error ? err.message : 'Unable to save feedback.')
    }
  }

  return (
    <section aria-labelledby="assistant-heading">
      <div className={`assistant-layout ${inspectorOpen ? 'assistant-layout--inspector' : ''}`}>
        <div className="chat-column">
          {turns.length === 0 ? (
            <div className="empty-hero">
              <div>
                <h1 id="assistant-heading">Ask campus notices &amp; FAQs</h1>
                <p className="empty-hero__sub" style={{ marginTop: '8px' }}>
                  Answers from 112 synthetic HANU FAQs and notices, each with its source file and cosine; other
                  questions are refused.
                </p>
              </div>

              <form onSubmit={handleFormSubmit}>
                <label htmlFor="assistant-query-input" className="field-label">
                  Campus policy or FAQ question
                </label>
                <div className="composer-box">
                  <input
                    id="assistant-query-input"
                    className="composer-input"
                    type="text"
                    placeholder="Ask about tuition deadlines, exams, schedules, advising, or Wi-Fi..."
                    value={draftQuery}
                    onChange={(e) => setDraftQuery(e.target.value)}
                    disabled={isSubmitting}
                  />
                  <button
                    type="submit"
                    className="btn btn--primary"
                    disabled={isSubmitting || !draftQuery.trim()}
                  >
                    {isSubmitting ? 'Searching...' : 'Ask'}
                  </button>
                </div>
              </form>

              <div className="suggestion-row" aria-label="Sample questions">
                {STARTER_PROMPTS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className="suggestion-chip"
                    disabled={isSubmitting}
                    onClick={() => {
                      void onSubmitQuery(item.query)
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              {thresholdControl}

              {catalog.length > 0 && (
                <div className="topic-section">
                  <h2 className="section-title">Topics and contacts</h2>
                  <div className="topic-grid">
                    {catalog.map((cat) => (
                      <div key={cat.intent} className="topic-card">
                        <div className="small-meta">{cat.office_name}</div>
                        <div className="topic-card__title">{cat.title}</div>
                        <div className="small-meta">
                          <span className="num">{cat.faq_count}</span> FAQs · <span className="num">{cat.notice_count}</span> notices
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              <h1 id="assistant-heading" style={{ fontSize: '24px', marginBottom: '18px' }}>
                Campus Q&amp;A Session
              </h1>

              <div className="chat-stream" aria-live="polite">
                {turns.map((turn, idx) => {
                  const res = turn.response
                  const isSelected = activeTurn?.id === turn.id
                  const isLatest = idx === turns.length - 1
                  const topDoc = res.results[0]
                  const intentTheme = topicStyle(res.intent)

                  return (
                    <article
                      key={turn.id}
                      ref={isLatest ? latestTurnRef : undefined}
                      className="chat-turn"
                      aria-label={`Turn ${idx + 1}`}
                    >
                      <div className="user-bubble-row">
                        <div className="user-bubble">{res.query}</div>
                      </div>

                      {res.is_non_english && (
                        <div className="advisory-banner" role="note">
                          <strong>Language advisory:</strong> Corpus documents are indexed in English.{' '}
                          <span lang="vi">
                            (Quý sinh viên vui lòng đặt câu hỏi bằng tiếng Anh để đạt độ chính xác cao nhất.)
                          </span>
                        </div>
                      )}

                      {res.abstained ? (
                        <div className="abstention-block" role="status">
                          <div className="abstention-block__title">{res.abstention_message}</div>
                          <p className="muted-note">
                            Abstained safely because the dual gate did not clear: cosine{' '}
                            <span className="num">{res.gate_details.top1_cosine.toFixed(3)}</span> (min{' '}
                            <span className="num">{res.gate_details.cosine_threshold.toFixed(2)}</span>) · intent{' '}
                            <span className="num">{(res.gate_details.intent_confidence * 100).toFixed(1)}%</span> (min{' '}
                            <span className="num">
                              {res.gate_details.intent_threshold !== null
                                ? `${(res.gate_details.intent_threshold * 100).toFixed(0)}%`
                                : 'off'}
                            </span>
                            ). Office routing is withheld.
                          </p>
                        </div>
                      ) : (
                        topDoc && (
                          <div className="answer-flow">
                            <div className="answer-meta">
                              <span className="topic-tag">
                                <span
                                  className="topic-dot"
                                  style={{ background: intentTheme.fg }}
                                  aria-hidden="true"
                                />
                                <span>Intent: {res.intent_label}</span>
                                <span className="muted-note">
                                  · confidence <span className="num">{Math.round(res.intent_confidence * 100)}%</span>
                                </span>
                              </span>
                              <span className="small-meta">
                                {res.results.length} matching document{res.results.length === 1 ? '' : 's'}
                              </span>
                            </div>

                            {res.results.map((doc, docIdx) => (
                              <div key={doc.id} className={`result-card ${docIdx === 0 ? 'result-card--top' : ''}`}>
                                <div className="result-card__meta">
                                  <span className="source-pill">
                                    {doc.source === 'notices.json' ? 'Notice' : 'FAQ'} ({doc.source})
                                    {doc.date ? ` · ${doc.date}` : ''}
                                  </span>
                                  <span className="small-meta">
                                    {doc.match_label} · cosine <span className="num">{doc.score.toFixed(3)}</span>
                                  </span>
                                  <button
                                    type="button"
                                    className="link-btn mono result-card__id"
                                    onClick={() => onOpenDocumentById(doc.id)}
                                  >
                                    {doc.id}
                                  </button>
                                </div>
                                {docIdx === 0 ? (
                                  <h2 className="answer-heading">{doc.question}</h2>
                                ) : (
                                  <h3 className="result-card__title">{doc.question}</h3>
                                )}
                                <p className={docIdx === 0 ? 'answer-body' : 'result-card__body'}>
                                  <HighlightedText segments={doc.answer_segments} fallback={doc.answer} />
                                </p>
                                {docIdx === 0 && res.office && (
                                  <p className="contact-line">
                                    <strong>{res.office.name}</strong> — {res.office.contact} (
                                    <button
                                      type="button"
                                      className="link-btn mono"
                                      onClick={() => onOpenDocumentById(res.office!.evidence)}
                                    >
                                      {res.office.evidence}
                                    </button>
                                    )
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        )
                      )}

                      <div className="turn-actions">
                        <button
                          type="button"
                          className={`link-btn ${turn.feedbackGiven === true ? 'link-btn--active' : ''}`}
                          aria-pressed={turn.feedbackGiven === true}
                          onClick={() => {
                            void handleFeedback(turn, true)
                          }}
                        >
                          {turn.feedbackGiven === true ? 'Marked helpful' : 'Helpful'}
                        </button>
                        <button
                          type="button"
                          className={`link-btn ${turn.feedbackGiven === false ? 'link-btn--active' : ''}`}
                          aria-pressed={turn.feedbackGiven === false}
                          onClick={() => {
                            void handleFeedback(turn, false)
                          }}
                        >
                          {turn.feedbackGiven === false ? 'Issue reported' : 'Not helpful'}
                        </button>
                        <button
                          type="button"
                          className={`link-btn ${isSelected && inspectorOpen ? 'link-btn--active' : ''}`}
                          onClick={() => {
                            onSelectTurn(turn.id)
                            if (!inspectorOpen) onToggleInspector()
                          }}
                        >
                          {isSelected && inspectorOpen ? 'Inspecting trace' : 'Inspect trace'}
                        </button>
                        <span className="small-meta num" style={{ marginLeft: 'auto' }}>
                          {res.latency_ms.toFixed(1)} ms
                        </span>
                      </div>
                    </article>
                  )
                })}
              </div>

              {feedbackNotice && (
                <p className="small-meta" style={{ marginTop: '10px' }} aria-live="polite">
                  {feedbackNotice}
                </p>
              )}
            </>
          )}

          {submitError && (
            <div className="abstention-block" style={{ marginTop: '16px' }} role="alert">
              <div className="abstention-block__title">Request failed</div>
              <p className="muted-note">{submitError}</p>
            </div>
          )}

          {turns.length > 0 && (
            <form className="composer-dock" onSubmit={handleFormSubmit}>
              <label htmlFor="assistant-query-input" className="field-label">
                Follow-up question
              </label>
              <div className="composer-box">
                <input
                  id="assistant-query-input"
                  className="composer-input"
                  type="text"
                  placeholder="Ask another campus question..."
                  value={draftQuery}
                  onChange={(e) => setDraftQuery(e.target.value)}
                  disabled={isSubmitting}
                />
                <button
                  type="submit"
                  className="btn btn--primary"
                  disabled={isSubmitting || !draftQuery.trim()}
                >
                  {isSubmitting ? 'Searching...' : 'Ask'}
                </button>
              </div>
              {thresholdControl}
              <div className="composer-dock__foot">
                <span />
                <button
                  type="button"
                  className="link-btn"
                  onClick={() => {
                    setFeedbackNotice('')
                    onClearHistory()
                  }}
                >
                  New chat
                </button>
              </div>
            </form>
          )}
        </div>

        {inspectorOpen && (
          <InspectorPanel
            cosineThreshold={cosineThreshold}
            intentThreshold={intentThreshold}
            topK={topK}
            onChangeCosineThreshold={onChangeCosineThreshold}
            onChangeIntentThreshold={onChangeIntentThreshold}
            onChangeTopK={onChangeTopK}
            onResetDefaults={onResetDefaults}
            onReEvaluateTurn={() => {
              if (activeTurn) {
                void onSubmitQuery(activeTurn.response.query)
              }
            }}
            canReEvaluate={Boolean(activeTurn)}
            isSubmitting={isSubmitting}
            activeTurnResponse={activeTurn?.response ?? null}
          />
        )}
      </div>
    </section>
  )
}
