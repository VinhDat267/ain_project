"""Design tokens and CSS for the Campus FAQ Assistant.

Style: an achromatic ledger. The chrome is ink and greys on a neutral ground; the one
data hue (#1d5fbf) marks the screen's main data element, the cosine relevance bar of
each answer card; status colours appear only as pale pairs on the refusal and on the
match label. One typeface (Source Sans Pro, bundled with Streamlit so the app runs
offline), Source Code Pro for document IDs only, tabular figures on every number.
"""
from __future__ import annotations

import streamlit as st

TOKENS: dict[str, str] = {
    # Surfaces: page ground, card surface, raised fill (pills, the sidebar's active rows)
    "surface_0": "#f8f8f8",
    "surface_1": "#ffffff",
    "surface_2": "#eeeeee",
    "surface_border": "#e6e6e6",

    # Text in three tiers, each at 4.5:1 or more on every surface above
    "text_primary": "#0a0a0a",
    "text_secondary": "#5f5f5f",
    "text_muted": "#6b6b6b",

    # The one data hue: the cosine bar on each answer card (5.9:1 on white)
    "accent_teal": "#1d5fbf",

    # Match labels and status (text colours; pills use the pale pairs in the CSS)
    "match_strong": "#2e7d32",
    "match_possible": "#92400e",
    "match_weak": "#5f5f5f",
    "status_error": "#c4242a",
}


def relative_luminance(hex_color: str) -> float:
    """Calculate WCAG 2.2 relative luminance for a given hex color."""
    color = hex_color.lstrip("#")
    r, g, b = [int(color[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def channel_luminance(val: float) -> float:
        return val / 12.92 if val <= 0.03928 else ((val + 0.055) / 1.055) ** 2.4

    r_lum = channel_luminance(r)
    g_lum = channel_luminance(g)
    b_lum = channel_luminance(b)
    return 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG 2.2 contrast ratio between two hex colors."""
    lum1 = relative_luminance(hex1)
    lum2 = relative_luminance(hex2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


# Type scale: 12 / 13 / 14 / 16 / 18 / 24, KPI figures 30. One gap value: 12px.
CUSTOM_CSS = """
:root {
    --ground: #f8f8f8;
    --surface: #ffffff;
    --raised: #eeeeee;
    --border: #e6e6e6;
    --rule: #f0f0f0;
    --control: #d4d4d4;
    --text: #0a0a0a;
    --muted: #5f5f5f;
    --data: #1d5fbf;
    --pill-positive-bg: #dcfae5; --pill-positive-ink: #04250e;
    --pill-negative-bg: #ffedea; --pill-negative-ink: #831c1e;
    --pill-warning-bg: #fffbeb; --pill-warning-ink: #92400e;
    --pill-neutral-bg: #eeeeee; --pill-neutral-ink: #3d3d3d;
    --radius-card: 8px;
    --radius-control: 6px;
    --gap: 12px;
}

/* Streamlit chrome that is not part of this product */
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { background: var(--ground); }
/* Streamlit fades an overflowing tab bar with a gradient; the two tabs fit, so drop the fade. */
.stTabs::after { display: none; }

.stApp { font-variant-numeric: tabular-nums; }
/* The canvas starts under the (empty) header instead of 6rem below it */
.block-container, [data-testid="stMainBlockContainer"] { padding-top: 2.5rem; }
/* Narrow canvases (a tablet beside the open sidebar) keep 24px gutters instead of 80px */
@media (max-width: 1024px) {
    .block-container, [data-testid="stMainBlockContainer"] { padding-left: 1.5rem; padding-right: 1.5rem; }
}
/* Button rows size each column to its button and wrap when the canvas is narrow */
[data-testid="stHorizontalBlock"]:has(.stButton) { flex-wrap: wrap; gap: 0.5rem; }
[data-testid="stHorizontalBlock"]:has(.stButton) > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"]:has(.stButton) > [data-testid="column"] {
    flex: 0 0 auto;
    width: auto !important;
    min-width: 0;
}
code, kbd { font-size: 0.8125rem; }

/* Sidebar on the page ground, split from the canvas by one hairline */
[data-testid="stSidebar"] {
    background: var(--ground);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h3 { font-size: 1.125rem; font-weight: 600; }
/* A folded sidebar is off screen: keep its text out of view and out of the tab order. */
[data-testid="stSidebar"][aria-expanded="false"] { visibility: hidden; }
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] { display: none; }
/* Streamlit opens the sidebar at exactly 768px ("auto" folds it only below 768) but lays the canvas
   under it there; at that one width put the canvas beside the sidebar, as it is from 769px up. */
@media (min-width: 768px) and (max-width: 768.98px) {
    [data-testid="stSidebar"][aria-expanded="true"] { position: relative; box-shadow: none; }
    [data-testid="stMain"] { position: relative; }
}

/* Inline code (document IDs, intents) in the ink on the raised fill, not Streamlit's green */
[data-testid="stMarkdownContainer"] code, [data-testid="stCaptionContainer"] code, .orca-provenance code,
.orca-ticket-row code, .orca-ticket-text code {
    color: #3d3d3d;
    background: var(--raised);
    border-radius: 4px;
    padding: 0 0.25em;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] { color: var(--muted); font-size: 0.8125rem; }

/* Slider figures in the text face, not the code face */
[data-testid="stSliderThumbValue"],
[data-testid="stSliderTickBarMin"],
[data-testid="stSliderTickBarMax"] {
    font-family: inherit;
    font-variant-numeric: tabular-nums;
}

/* Title row */
.orca-title-row { margin: 0 0 1.25rem 0; }
.orca-title {
    font-size: 1.5rem;
    line-height: 1.25;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 0.25rem 0;
    padding: 0;
}
.orca-subtitle { font-size: 0.875rem; color: var(--muted); margin: 0; line-height: 1.45; }
.orca-section-title { font-size: 1.125rem; font-weight: 600; color: var(--text); margin: 0 0 0.25rem 0; }
.orca-section-note { font-size: 0.875rem; color: var(--muted); margin: 0 0 0.75rem 0; }

/* Controls: white fields with a control border; buttons follow the theme (primary is near-black) */
.stTextInput input {
    background: var(--surface);
    border-radius: var(--radius-control);
}
.stButton > button { border-radius: var(--radius-control); min-height: 36px; }

/* Alerts: the refusal keeps the pale negative pair; the rest sit on the card surface */
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]),
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
}
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentInfo"] { color: var(--text); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {
    background: var(--pill-negative-bg);
    color: var(--pill-negative-ink);
}
[data-testid="stAlertContentError"] { color: var(--pill-negative-ink); }

/* Answer cards: one surface, one quiet border, no shadow */
.orca-card, .orca-card-featured {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 1rem 1.25rem;
    margin: 0 0 var(--gap) 0;
}
.orca-card-featured { border-color: var(--control); }
.orca-card:hover, .orca-card-featured:hover { border-color: #bdbdbd; }

.orca-meta-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.5rem;
}
.orca-badge {
    flex: none;
    white-space: nowrap;
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 500;
    line-height: 1.6;
    padding: 0 0.45rem;
    border-radius: 4px;
    background: var(--pill-neutral-bg);
    color: var(--pill-neutral-ink);
}
.orca-badge-strong { background: var(--pill-positive-bg); color: var(--pill-positive-ink); }
.orca-badge-possible { background: var(--pill-warning-bg); color: var(--pill-warning-ink); }
.orca-badge-weak, .orca-badge-faq, .orca-badge-notice { background: var(--pill-neutral-bg); color: var(--pill-neutral-ink); }

.orca-question {
    font-size: 1.125rem;
    font-weight: 600;
    line-height: 1.35;
    color: var(--text);
    margin: 0 0 0.5rem 0;
}
.orca-meter-container {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.8125rem;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.orca-meter-container strong { color: var(--text); font-weight: 600; }
.orca-meter-container span { white-space: nowrap; }
.orca-meter-track {
    width: 160px;
    height: 6px;
    border-radius: 999px;
    background: var(--raised);
    overflow: hidden;
}
.orca-meter-fill { height: 100%; border-radius: 999px; background: var(--data); }
.orca-answer { font-size: 1rem; line-height: 1.55; color: var(--text); margin-bottom: 0.5rem; }

/* Query terms found in the answer: weight, not a coloured box */
mark.orca-highlight, .orca-highlight {
    background: none;
    color: inherit;
    font-weight: 600;
    padding: 0;
}

details summary {
    font-size: 0.8125rem;
    color: var(--muted);
    cursor: pointer;
}
details summary:hover { color: var(--text); }
.orca-provenance { font-size: 0.8125rem; color: var(--muted); margin: 0.35rem 0 0 0; }

/* Intent ticket (Classify intent) */
.orca-office-ticket {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 1rem 1.25rem;
    margin: 0 0 var(--gap) 0;
}
.orca-ticket-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.orca-ticket-label { font-size: 0.8125rem; color: var(--muted); margin-bottom: 0.25rem; }
.orca-ticket-name { font-size: 1.125rem; font-weight: 600; color: var(--text); margin-bottom: 0.25rem; }
.orca-ticket-text { font-size: 0.875rem; color: var(--muted); line-height: 1.45; }
.orca-ticket-well { background: var(--ground); border-radius: 6px; padding: 0.65rem 0.85rem; margin-top: 0.75rem; }
.orca-ticket-row { display: flex; justify-content: space-between; font-size: 0.875rem; line-height: 1.8; }
.orca-ticket-row span:last-child { font-weight: 600; }
@media (max-width: 640px) { .orca-ticket-grid { grid-template-columns: 1fr; } }

/* Empty state: topic directory and recent notices */
.orca-directory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: var(--gap);
    margin-bottom: 2rem;
}
/* Seven topics: the last card takes the whole row rather than leaving an orphan cell */
.orca-directory-grid > .orca-directory-card:last-child:nth-child(3n+1) { grid-column: 1 / -1; }
.orca-directory-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.orca-directory-office { font-size: 0.8125rem; color: var(--muted); margin-bottom: 0.25rem; }
.orca-directory-title { font-size: 1rem; font-weight: 600; color: var(--text); margin-bottom: 0.25rem; }
.orca-directory-desc { font-size: 0.875rem; color: var(--muted); line-height: 1.45; }
.orca-directory-footer { font-size: 0.8125rem; color: var(--muted); margin-top: 0.75rem; }

.orca-notice-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 0.85rem 1.25rem;
    margin-bottom: var(--gap);
}
.orca-notice-title { font-weight: 600; font-size: 1rem; color: var(--text); margin-bottom: 0.25rem; }
.orca-notice-text { font-size: 0.875rem; color: var(--muted); line-height: 1.5; }

/* Inspector notice in the sidebar */
.orca-inspector-note { font-size: 0.8125rem; color: var(--muted); margin: 0 0 0.75rem 0; }

/* Dashboard */
.orca-dash-title { font-size: 1.5rem; font-weight: 600; color: var(--text); margin: 0 0 0.25rem 0; }
[data-testid="stMetricValue"] { font-size: 1.875rem; font-weight: 400; }
[data-testid="stMetricLabel"] p { font-size: 0.875rem; color: var(--muted); }

/* Tables: rules and alignment, no header band, numbers right-aligned in tabular figures */
.orca-table-wrap { max-width: 100%; overflow-x: auto; margin: 0.75rem 0; }
table.orca-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
    background: var(--surface);
    margin: 0;
    font-variant-numeric: tabular-nums;
}
table.orca-table th, table.orca-table td {
    border: none;
    border-bottom: 1px solid var(--rule);
    padding: 0.5rem 0.75rem;
    text-align: left;
    white-space: nowrap;
}
table.orca-table th {
    background: none;
    color: var(--muted);
    font-weight: 400;
    font-size: 0.8125rem;
    border-bottom: 1px solid var(--border);
    vertical-align: bottom;
}
table.orca-table td { color: var(--text); }
table.orca-table .num { text-align: right; }
caption.orca-table-caption {
    caption-side: top;
    font-weight: 600;
    text-align: left;
    padding: 6px 0;
    font-size: 0.875rem;
    color: var(--text);
}

/* Reduced Motion Discipline (WCAG 2.2 SC 2.3.3) */
@media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
"""


def apply_theme() -> None:
    """Inject the design tokens and CSS into the Streamlit app."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)
