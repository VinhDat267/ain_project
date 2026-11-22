import { useEffect, useState } from 'react'
import { fetchDocument, sendChat } from './api/client'
import { DocumentDialog } from './components/DocumentDialog'
import { HeaderNav } from './components/HeaderNav'
import type { ChatTurn, DocumentItem, ViewId } from './types/api'
import { AnalyticsView } from './views/AnalyticsView'
import { ArchiveView } from './views/ArchiveView'
import { AssistantView } from './views/AssistantView'
import { StressTestView } from './views/StressTestView'

const STORAGE_KEY = 'hanu_faq_chat_turns_v1'
const DEFAULT_COSINE = 0.15
const DEFAULT_INTENT = 0.34
const DEFAULT_TOP_K = 3

function readInitialView(): ViewId {
  const hash = window.location.hash.replace(/^#/, '')
  if (hash === 'stress-test' || hash === 'analytics' || hash === 'archive') {
    return hash
  }
  return 'assistant'
}

function loadStoredTurns(): ChatTurn[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? (parsed as ChatTurn[]) : []
  } catch {
    return []
  }
}

export function App() {
  const [activeView, setActiveView] = useState<ViewId>(readInitialView)
  const [turns, setTurns] = useState<ChatTurn[]>(loadStoredTurns)
  const [selectedTurnId, setSelectedTurnId] = useState<string | null>(() => {
    const initial = loadStoredTurns()
    return initial.length ? initial[initial.length - 1].id : null
  })

  const [inspectorOpen, setInspectorOpen] = useState(false)
  const [cosineThreshold, setCosineThreshold] = useState(DEFAULT_COSINE)
  const [intentThreshold, setIntentThreshold] = useState(DEFAULT_INTENT)
  const [topK, setTopK] = useState(DEFAULT_TOP_K)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [dialogDoc, setDialogDoc] = useState<DocumentItem | null>(null)

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(turns.slice(-20)))
    } catch {
      // Ignore storage quota issues
    }
  }, [turns])

  useEffect(() => {
    const onHashChange = () => setActiveView(readInitialView())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const navigate = (view: ViewId) => {
    setActiveView(view)
    if (window.location.hash !== `#${view}`) {
      window.history.replaceState(null, '', `#${view}`)
    }
  }

  const handleSubmitQuery = async (queryText: string) => {
    const cleaned = queryText.trim()
    if (!cleaned) return
    setIsSubmitting(true)
    setSubmitError(null)
    const requestPayload = {
      query: cleaned,
      top_k: topK,
      threshold: cosineThreshold,
      intent_threshold: intentThreshold,
      include_inspector: true,
    }
    try {
      const response = await sendChat(requestPayload)
      const turn: ChatTurn = {
        id: `turn_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        createdAt: new Date().toISOString(),
        request: requestPayload,
        response,
        feedbackGiven: null,
      }
      setTurns((prev) => [...prev, turn])
      setSelectedTurnId(turn.id)
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Unable to reach assistant backend.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleOpenDocumentById = async (docId: string) => {
    try {
      const doc = await fetchDocument(docId)
      setDialogDoc(doc)
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : `Unable to load ${docId}.`)
    }
  }

  const handleAskInAssistant = (query: string) => {
    navigate('assistant')
    void handleSubmitQuery(query)
  }

  return (
    <>
      <HeaderNav
        activeView={activeView}
        onNavigate={navigate}
        inspectorOpen={inspectorOpen}
        onToggleInspector={() => setInspectorOpen((prev) => !prev)}
      />

      <main id="main-content" tabIndex={-1} className="wrap main-content">
        {activeView === 'assistant' && (
          <AssistantView
            turns={turns}
            selectedTurnId={selectedTurnId}
            onSelectTurn={setSelectedTurnId}
            onSubmitQuery={handleSubmitQuery}
            onClearHistory={() => {
              setTurns([])
              setSelectedTurnId(null)
              window.localStorage.removeItem(STORAGE_KEY)
            }}
            onMarkFeedback={(turnId, helpful) => {
              setTurns((prev) =>
                prev.map((t) => (t.id === turnId ? { ...t, feedbackGiven: helpful } : t)),
              )
            }}
            onOpenDocumentById={(id) => {
              void handleOpenDocumentById(id)
            }}
            inspectorOpen={inspectorOpen}
            onToggleInspector={() => setInspectorOpen((prev) => !prev)}
            cosineThreshold={cosineThreshold}
            intentThreshold={intentThreshold}
            topK={topK}
            onChangeCosineThreshold={setCosineThreshold}
            onChangeIntentThreshold={setIntentThreshold}
            onChangeTopK={setTopK}
            onResetDefaults={() => {
              setCosineThreshold(DEFAULT_COSINE)
              setIntentThreshold(DEFAULT_INTENT)
              setTopK(DEFAULT_TOP_K)
            }}
            isSubmitting={isSubmitting}
            submitError={submitError}
          />
        )}

        {activeView === 'stress-test' && (
          <StressTestView
            defaultCosine={DEFAULT_COSINE}
            defaultIntent={DEFAULT_INTENT}
            onAskInAssistant={handleAskInAssistant}
          />
        )}

        {activeView === 'analytics' && <AnalyticsView />}

        {activeView === 'archive' && (
          <ArchiveView
            onOpenDocument={setDialogDoc}
            onOpenDocumentById={(id) => {
              void handleOpenDocumentById(id)
            }}
          />
        )}
      </main>

      <footer className="site-footer">
        <div className="wrap footer-inner">
          <span>AIN Project 12 · Synthetic HANU corpus (112 docs) · Classical TF-IDF &amp; Logistic Regression</span>
          <a className="mono link-btn" href="/docs">
            OpenAPI /docs
          </a>
        </div>
      </footer>

      <DocumentDialog
        document={dialogDoc}
        onClose={() => setDialogDoc(null)}
        onAskInAssistant={handleAskInAssistant}
      />
    </>
  )
}
