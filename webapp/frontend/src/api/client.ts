import type {
  AnalyticsPayload,
  ChatRequestPayload,
  ChatResponse,
  DocumentItem,
  DocumentsResponse,
  HealthResponse,
  StressPreset,
  StressTestResponse,
} from '../types/api'

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const payload = await response.json()
      if (typeof payload?.detail === 'string') {
        detail = payload.detail
      } else if (Array.isArray(payload?.detail) && payload.detail[0]?.msg) {
        detail = String(payload.detail[0].msg)
      }
    } catch {
      // Keep status message
    }
    throw new Error(detail)
  }
  return (await response.json()) as T
}

export function fetchHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>('/api/health')
}

export function sendChat(payload: ChatRequestPayload): Promise<ChatResponse> {
  return requestJson<ChatResponse>('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function runStressTest(params: {
  preset: StressPreset
  custom_queries?: string[]
  threshold: number
  intent_threshold: number | null
  top_k: number
}): Promise<StressTestResponse> {
  return requestJson<StressTestResponse>('/api/stress-test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
}

export function fetchDocuments(filters?: {
  intent?: string
  source?: string
  q?: string
}): Promise<DocumentsResponse> {
  const sp = new URLSearchParams()
  if (filters?.intent) sp.set('intent', filters.intent)
  if (filters?.source) sp.set('source', filters.source)
  if (filters?.q) sp.set('q', filters.q)
  const qs = sp.toString()
  return requestJson<DocumentsResponse>(qs ? `/api/documents?${qs}` : '/api/documents')
}

export function fetchDocument(docId: string): Promise<DocumentItem> {
  return requestJson<DocumentItem>(`/api/documents/${encodeURIComponent(docId)}`)
}

export function fetchAnalytics(): Promise<AnalyticsPayload> {
  return requestJson<AnalyticsPayload>('/api/analytics')
}

export function submitFeedback(payload: {
  query: string
  doc_id: string
  helpful: boolean
}): Promise<{ saved: boolean; doc_id: string; helpful: boolean }> {
  return requestJson<{ saved: boolean; doc_id: string; helpful: boolean }>('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
