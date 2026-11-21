import type { ViewId } from '../types/api'

interface HeaderNavProps {
  activeView: ViewId
  onNavigate: (view: ViewId) => void
  inspectorOpen: boolean
  onToggleInspector: () => void
}

const NAV_ITEMS: Array<{ id: ViewId; label: string }> = [
  { id: 'assistant', label: 'Assistant' },
  { id: 'stress-test', label: 'Stress-Test' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'archive', label: 'Archive' },
]

export function HeaderNav({
  activeView,
  onNavigate,
  inspectorOpen,
  onToggleInspector,
}: HeaderNavProps) {
  return (
    <header className="site-header">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <div className="wrap header-inner">
        <a
          className="brand"
          href="#assistant"
          onClick={(e) => {
            e.preventDefault()
            onNavigate('assistant')
          }}
        >
          <svg
            className="brand-mark"
            viewBox="0 0 32 32"
            width="28"
            height="28"
            aria-hidden="true"
          >
            <rect width="32" height="32" rx="8" fill="#1f3038" />
            <rect x="7" y="8" width="8" height="16" rx="2" fill="#f7f9fa" />
            <rect x="17" y="8" width="8" height="7" rx="2" fill="#0d7480" />
            <rect x="17" y="17" width="8" height="7" rx="2" fill="#9ea7ab" />
          </svg>
          <span className="brand-title">HANU Assistant</span>
        </a>

        <nav className="primary-nav" aria-label="Primary">
          {NAV_ITEMS.map((item) => {
            const current = activeView === item.id
            return (
              <button
                key={item.id}
                type="button"
                className="nav-link"
                aria-current={current ? 'page' : undefined}
                onClick={() => onNavigate(item.id)}
              >
                {item.label}
              </button>
            )
          })}
        </nav>

        <div className="header-actions">
          {activeView === 'assistant' && (
            <button
              type="button"
              className={`btn btn--sm ${inspectorOpen ? 'btn--active' : 'btn--secondary'}`}
              aria-pressed={inspectorOpen}
              onClick={onToggleInspector}
            >
              {inspectorOpen ? 'Close inspector' : 'Inspector'}
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
