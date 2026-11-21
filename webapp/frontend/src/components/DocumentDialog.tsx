import { useEffect, useRef } from 'react'
import { topicStyle } from '../constants/topics'
import type { DocumentItem } from '../types/api'

interface DocumentDialogProps {
  document: DocumentItem | null
  onClose: () => void
  onAskInAssistant: (query: string) => void
}

export function DocumentDialog({
  document,
  onClose,
  onAskInAssistant,
}: DocumentDialogProps) {
  const dialogRef = useRef<HTMLDialogElement | null>(null)
  const pointerDownTargetRef = useRef<EventTarget | null>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    dialog.setAttribute('closedby', 'any')
    if (document && !dialog.open) {
      dialog.showModal()
    } else if (!document && dialog.open) {
      dialog.close()
    }
  }, [document])

  const topic = document ? topicStyle(document.intent) : null

  return (
    <dialog
      ref={dialogRef}
      className="doc-dialog"
      aria-labelledby={document ? 'doc-dialog-title' : undefined}
      onClose={onClose}
      onPointerDown={(e) => {
        pointerDownTargetRef.current = e.target
      }}
      onPointerUp={(e) => {
        const dialog = dialogRef.current
        if (
          dialog &&
          e.target === dialog &&
          pointerDownTargetRef.current === dialog
        ) {
          dialog.close()
        }
        pointerDownTargetRef.current = null
      }}
    >
      {document && topic && (
        <>
          <div className="doc-dialog__head">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                <span
                  className="badge"
                  style={{
                    color: topic.fg,
                    background: topic.bg,
                    borderColor: topic.border,
                  }}
                >
                  {topic.label}
                </span>
                <span className="badge mono">{document.id}</span>
                <span className="badge">{document.source}</span>
                {document.date && <span className="badge">Published {document.date}</span>}
              </div>
              <h2 id="doc-dialog-title" style={{ fontSize: '22px' }}>
                {document.question}
              </h2>
            </div>
            <button
              type="button"
              className="btn btn--sm btn--ghost"
              aria-label="Close document dialog"
              onClick={() => dialogRef.current?.close()}
            >
              Close
            </button>
          </div>

          <div className="doc-dialog__body">
            <div>
              <p className="field-label">Full document text</p>
              <p style={{ lineHeight: 1.65 }}>{document.answer}</p>
            </div>

            <div
              className="card card--surface"
              style={{ display: 'flex', flexDirection: 'column', gap: '6px', padding: '16px' }}
            >
              <p className="field-label" style={{ marginBottom: 0 }}>
                Corpus-attested contact point
              </p>
              <p style={{ fontWeight: 500 }}>{document.office.name}</p>
              <p className="muted-note">{document.office.contact}</p>
              <p className="small-meta">
                {document.office.role} Evidence: <code className="mono">{document.office.evidence}</code>.
              </p>
            </div>
          </div>

          <div className="doc-dialog__foot">
            <button
              type="button"
              className="btn btn--secondary"
              onClick={() => dialogRef.current?.close()}
            >
              Close viewer
            </button>
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => {
                const q = document.question
                dialogRef.current?.close()
                onAskInAssistant(q)
              }}
            >
              Ask in assistant
            </button>
          </div>
        </>
      )}
    </dialog>
  )
}
