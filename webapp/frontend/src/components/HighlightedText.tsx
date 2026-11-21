import type { HighlightSegment } from '../types/api'

interface HighlightedTextProps {
  segments: HighlightSegment[]
  fallback: string
}

export function HighlightedText({ segments, fallback }: HighlightedTextProps) {
  if (!segments || segments.length === 0) {
    return <>{fallback}</>
  }

  return (
    <>
      {segments.map((seg, idx) =>
        seg.highlighted ? (
          <mark key={idx} className="highlight-mark">
            {seg.text}
          </mark>
        ) : (
          <span key={idx}>{seg.text}</span>
        ),
      )}
    </>
  )
}
