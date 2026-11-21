import { useEffect, useState, type KeyboardEvent } from 'react'
import { fetchDocuments } from '../api/client'
import { topicStyle } from '../constants/topics'
import type { DocumentItem, DomainCatalogItem } from '../types/api'

interface ArchiveViewProps {
  onOpenDocument: (doc: DocumentItem) => void
  onOpenDocumentById: (docId: string) => void
}

type ArchiveTabId = 'documents' | 'contacts'

export function ArchiveView({ onOpenDocument, onOpenDocumentById }: ArchiveViewProps) {
  const [activeTab, setActiveTab] = useState<ArchiveTabId>('documents')
  const [search, setSearch] = useState('')
  const [selectedIntent, setSelectedIntent] = useState('')
  const [selectedSource, setSelectedSource] = useState('')
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [catalog, setCatalog] = useState<DomainCatalogItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchDocuments({
      intent: selectedIntent || undefined,
      source: selectedSource || undefined,
      q: search.trim() || undefined,
    })
      .then((res) => {
        if (!cancelled) {
          setDocuments(res.documents)
          setCatalog(res.catalog)
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unable to load archive.')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [search, selectedIntent, selectedSource])

  const tabs: Array<{ id: ArchiveTabId; label: string }> = [
    { id: 'documents', label: `Documents (${documents.length})` },
    { id: 'contacts', label: `Campus Contacts (${catalog.length || 7})` },
  ]

  const handleTabKeyDown = (e: KeyboardEvent<HTMLButtonElement>, idx: number) => {
    const nextIdx = e.key === 'ArrowRight' || e.key === 'ArrowLeft' ? (idx + 1) % tabs.length : idx
    if (nextIdx === idx) return
    e.preventDefault()
    const target = tabs[nextIdx]
    setActiveTab(target.id)
    document.getElementById(`arch-tab-${target.id}`)?.focus()
  }

  return (
    <section aria-labelledby="archive-heading">
      <div className="view-head">
        <div>
          <h1 id="archive-heading">Knowledge Archive</h1>
          <p className="view-lead">
            Browse all 112 synthetic FAQs and official notices, or inspect the 7 corpus-attested contacts.
          </p>
        </div>
      </div>

      <div className="tab-list" role="tablist" aria-label="Archive sections" style={{ marginBottom: '18px' }}>
        {tabs.map((tab, idx) => {
          const selected = activeTab === tab.id
          return (
            <button
              key={tab.id}
              id={`arch-tab-${tab.id}`}
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

      {error && (
        <div className="abstention-block" style={{ marginBottom: '16px' }} role="alert">
          <div className="abstention-block__title">Archive error</div>
          <p className="muted-note">{error}</p>
        </div>
      )}

      <div
        id="arch-panel-documents"
        role="tabpanel"
        aria-labelledby="arch-tab-documents"
        hidden={activeTab !== 'documents'}
      >
        <div className="archive-filter-bar">
          <div>
            <label htmlFor="archive-search" className="field-label">
              Search keyword or document ID
            </label>
            <input
              id="archive-search"
              className="text-input"
              type="search"
              placeholder="Search transcript, tuition, Wi-Fi, notice..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="archive-topic" className="field-label">
              Topic
            </label>
            <select
              id="archive-topic"
              className="select-input"
              value={selectedIntent}
              onChange={(e) => setSelectedIntent(e.target.value)}
            >
              <option value="">All 7 topics</option>
              {catalog.map((cat) => (
                <option key={cat.intent} value={cat.intent}>
                  {cat.title} ({cat.total_count})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="archive-source" className="field-label">
              Source
            </label>
            <select
              id="archive-source"
              className="select-input"
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
            >
              <option value="">All types</option>
              <option value="faq.json">FAQs (84)</option>
              <option value="notices.json">Notices (28)</option>
            </select>
          </div>
        </div>

        {loading ? (
          <p className="muted-note">Loading archive documents...</p>
        ) : documents.length === 0 ? (
          <div className="card">
            <p className="muted-note">No documents match those filters.</p>
          </div>
        ) : (
          <div className="doc-list">
            {documents.map((doc) => {
              const st = topicStyle(doc.intent)
              return (
                <button
                  key={doc.id}
                  type="button"
                  className="doc-row"
                  onClick={() => onOpenDocument(doc)}
                >
                  <div className="doc-row__main">
                    <div className="doc-row__title">{doc.question}</div>
                    <div className="doc-row__excerpt">{doc.answer}</div>
                  </div>
                  <div className="doc-row__meta">
                    <span className="topic-tag" style={{ fontSize: '13px' }}>
                      <span className="topic-dot" style={{ background: st.fg }} aria-hidden="true" />
                      {doc.intent_label}
                    </span>
                    <span className="mono">
                      {doc.id}
                      {doc.date ? ` · ${doc.date}` : ''}
                    </span>
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>

      <div
        id="arch-panel-contacts"
        role="tabpanel"
        aria-labelledby="arch-tab-contacts"
        hidden={activeTab !== 'contacts'}
      >
        <div className="doc-list">
          {catalog.map((cat) => {
            const st = topicStyle(cat.intent)
            return (
              <div key={cat.intent} className="contact-row">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxWidth: '640px' }}>
                  <span className="topic-tag" style={{ fontSize: '13px' }}>
                    <span className="topic-dot" style={{ background: st.fg }} aria-hidden="true" />
                    {cat.title} · <span className="num">{cat.faq_count} FAQs, {cat.notice_count} Notices</span>
                  </span>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 500 }}>
                    {cat.office_name}
                  </div>
                  <p className="muted-note">
                    {cat.office_contact} — {cat.office_role}
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    className="btn btn--sm btn--secondary"
                    onClick={() => onOpenDocumentById(cat.office_evidence)}
                  >
                    Read evidence
                  </button>
                  <button
                    type="button"
                    className="btn btn--sm btn--ghost"
                    onClick={() => {
                      setSelectedIntent(cat.intent)
                      setActiveTab('documents')
                    }}
                  >
                    View topic docs
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
