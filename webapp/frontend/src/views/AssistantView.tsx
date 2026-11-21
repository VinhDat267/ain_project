import { useEffect, useRef, useState, type FormEvent } from 'react'
import { submitFeedback } from '../api/client'
import { HighlightedText } from '../components/HighlightedText'
import { InspectorPanel } from '../components/InspectorPanel'
import { STARTER_PROMPTS, topicStyle } from '../constants/topics'
import type { ChatTurn } from '../types/api'

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
                  Retrieval-only search across 112 synthetic HANU documents. Zero external LLMs.
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
                  const secondaryDocs = res.results.slice(1)
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
                                <span>{topDoc.intent_label}</span>
                                <span className="muted-note">
                                  · {topDoc.match_label} (<span className="num">{topDoc.score.toFixed(2)}</span>)
                                </span>
                              </span>

                              <span>
                                <button
                                  type="button"
                                  className="link-btn mono"
                                  onClick={() => onOpenDocumentById(topDoc.id)}
                                >
                                  {topDoc.id}
                                </button>
                                {topDoc.date ? ` · ${topDoc.date}` : ''}
                              </span>
                            </div>

                            <h2 className="answer-heading">{topDoc.question}</h2>

                            <p className="answer-body">
                              <HighlightedText
                                segments={topDoc.answer_segments}
                                fallback={topDoc.answer}
                              />
                            </p>

                            {res.office && (
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

                            {secondaryDocs.length > 0 && (
                              <details className="related-disclosure">
                                <summary>
                                  Related matches ({secondaryDocs.length})
                                </summary>
                                <div className="related-list">
                                  {secondaryDocs.map((doc) => (
                                    <div key={doc.id} className="related-item">
                                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', flexWrap: 'wrap' }}>
                                        <strong style={{ fontWeight: 500 }}>{doc.question}</strong>
                                        <button
                                          type="button"
                                          className="link-btn mono"
                                          onClick={() => onOpenDocumentById(doc.id)}
                                        >
                                          {doc.id} ({doc.score.toFixed(2)})
                                        </button>
                                      </div>
                                      <p className="muted-note">
                                        <HighlightedText
                                          segments={doc.answer_segments}
                                          fallback={doc.answer}
                                        />
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </details>
                            )}
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
                          {turn.feedbackGiven === true ? 'Helpful ✓' : 'Helpful'}
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
              <div className="composer-dock__foot">
                <span className="num">
                  Dual-gate θ_sim {cosineThreshold.toFixed(2)} / θ_intent {intentThreshold.toFixed(2)}
                </span>
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
