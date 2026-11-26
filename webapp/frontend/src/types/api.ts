export type ViewId = 'assistant' | 'stress-test' | 'analytics' | 'archive'

export interface HighlightSegment {
  text: string
  highlighted: boolean
}

export interface ExplainFeature {
  feature: string
  contribution: number
}

export interface IntentProb {
  intent: string
  label: string
  probability: number
}

export interface OfficeContact {
  name: string
  role: string
  contact: string
  evidence: string
}

export interface RetrievedDocCard {
  id: string
  intent: string
  intent_label: string
  question: string
  answer: string
  answer_segments: HighlightSegment[]
  source: string
  date: string | null
  score: number
  match_label: 'Strong match' | 'Possible match' | 'Weak match' | string
}

export interface ComparisonItem {
  id: string
  question: string
  intent: string
  score: number
}

export interface ComparisonResult {
  char_wb: ComparisonItem[]
  word_tfidf: ComparisonItem[]
  bm25: ComparisonItem[]
}

export interface GateDetails {
  top1_cosine: number
  cosine_threshold: number
  cosine_passed: boolean
  intent_confidence: number
  intent_threshold: number | null
  intent_passed: boolean
}

export interface ChatRequestPayload {
  query: string
  top_k: number
  threshold: number
  intent_threshold: number | null
  include_inspector: boolean
}

export interface ChatResponse {
  query: string
  abstained: boolean
  abstention_message: string | null
  is_non_english: boolean
  intent: string
  intent_label: string
  intent_confidence: number
  latency_ms: number
  gate_details: GateDetails
  office: OfficeContact | null
  results: RetrievedDocCard[]
  explain_top1: ExplainFeature[]
  intent_probs: IntentProb[]
  comparison: ComparisonResult | null
}

export interface ChatTurn {
  id: string
  createdAt: string
  request: ChatRequestPayload
  response: ChatResponse
  feedbackGiven?: boolean | null
}

export type StressPreset = 'demo_6' | 'balanced_16' | 'benchmark_120' | 'custom'

export interface StressTestRow {
  query_id: string
  query_type: string
  query: string
  expected_doc_id: string | null
  expected_intent: string | null
  pred_intent: string
  intent_confidence: number
  top1_doc_id: string | null
  top1_cosine: number
  abstained: boolean
  status: string
  latency_ms: number
}

export interface StressTestSummary {
  total: number
  answered: number
  abstained: number
  in_corpus_total: number
  ooc_total: number
  top1_correct: number
  top3_delivered: number
  ooc_rejected: number
  ooc_leaked: number
  false_abstentions: number
  mean_latency_ms: number
}

export interface StressTestResponse {
  preset: StressPreset
  threshold: number
  intent_threshold: number | null
  summary: StressTestSummary
  rows: StressTestRow[]
}

export interface DocumentItem {
  id: string
  intent: string
  intent_label: string
  question: string
  answer: string
  source: string
  date: string | null
  office: OfficeContact
}

export interface DomainCatalogItem {
  intent: string
  title: string
  desc: string
  office_name: string
  office_contact: string
  office_role: string
  office_evidence: string
  total_count: number
  faq_count: number
  notice_count: number
}

export interface DocumentsResponse {
  total: number
  documents: DocumentItem[]
  catalog: DomainCatalogItem[]
}

export interface HealthResponse {
  status: string
  documents_loaded: number
  faqs: number
  notices: number
  intents: number
  defaults: {
    top_k: number
    cosine_threshold: number
    intent_threshold: number
  }
}

export interface ConfusionMatrixData {
  labels: string[]
  display_labels: string[]
  matrix: number[][]
  correct: number
  total: number
  accuracy: number
  misclassified: Array<{
    query_id: string
    query_type: string
    query: string
    expected_intent: string
    expected_label: string
    pred_intent: string
    pred_label: string
    intent_conf: number
  }>
}

export interface DevSplitSummary {
  total_queries: number
  e2e_count: number
  balanced_e2e: number
  ooc_queries: number
  ooc_refused: number
  paraphrase_queries: number
  paraphrase_hit1: number
}

export interface AnalyticsPayload {
  dev_split?: DevSplitSummary | null
  kpis: {
    mrr: number | null
    intent_accuracy: number | null
    intent_correct: number | null
    top3_rescue_rate: number | null
    raw_hit3: number | null
    ooc_rejection_rate: number | null
    total_queries: number | null
    in_corpus_queries: number | null
    ooc_queries: number | null
    deflection_rate: number | null
    safe_escalation_rate: number | null
    false_abstention_rate: number | null
    expected_cost: number | null
    w_silent_wrong: number | null
    w_false_abstain: number | null
    w_ooc_leak: number | null
  }
  manifest: {
    metadata?: {
      total_documents: number
      total_faq: number
      total_notices: number
      total_queries: number
      total_intents: number
    }
    vocabulary_sizes?: Record<string, number>
    ooc_score_distribution?: Record<string, number>
    match_calibration?: Record<string, unknown>
  }
  midterm_summary: Array<Record<string, string | number | null>>
  dual_gate_ablation: Array<{
    rule: string
    cosine_threshold: number | null
    intent_threshold: number | null
    correct: number
    total: number
    ooc_rejected: number
    ooc_total: number
  }>
  confusion_matrix: ConfusionMatrixData | null
  business_summary: Array<{
    metric: string
    value: number
    description: string
  }>
  cost_sensitivity: Array<{
    penalty_ratio: string
    w_silent_wrong: number
    w_false_abstain: number
    n_silent_wrong: number
    n_ooc_leaked: number
    n_false_abstentions: number
    total_penalty_units: number
    expected_cost_per_query: number
    cost_per_1000_queries: number
    silent_wrong_share_pct: number
  }>
  per_intent_business: Array<{
    segment_type: string
    segment_name: string
    total_queries: number
    top1_correct: number
    top3_correct: number
    abstained: number
    silent_wrong: number
    resolution_rate_top1: number
    top3_rescue_rate: number
  }>
  noise_curve: Array<{
    k: number
    method: string
    hit1: number
    mrr10: number
  }>
  intent_cv: Array<{
    model: string
    acc_mean: number
    acc_std: number
    f1_mean: number
    f1_std: number
  }>
  threshold_sweep: Array<{
    threshold: number
    e2e_normal: number
    e2e_paraphrase: number
    e2e_typo: number
    e2e_out_of_corpus: number
    ooc_rejection: number
    false_abstention: number
    balanced_e2e: number
  }>
  chosen_threshold: number | null
  dev_ablations: Record<string, Array<Record<string, string | number | null>>>
}
