"""Centralized Theme, Design Tokens, and CSS for the Campus FAQ Assistant.

Provides disciplined Claude/Editorial Warm Light surface hierarchy, accessible color tokens,
literary typography (Serif display), staggered fade-in animations, and prefers-reduced-motion compliance.
"""
from __future__ import annotations

import streamlit as st

TOKENS: dict[str, str] = {
    # 3-tier Surface Hierarchy (Claude Warm Light Parchment / Ivory / Warm Sand)
    "surface_0": "#f5f4ed",  # Base page canvas (Parchment, never pure white)
    "surface_1": "#faf9f5",  # Cards, containers, elevation 1 (Ivory)
    "surface_2": "#e8e6dc",  # Inputs, elevated buttons, badges (Warm Sand)
    "surface_border": "#d6d3c4",  # Subtle warm border

    # Typography Tiers (Anthropic Near-Black and Warm Grays)
    "text_primary": "#141413",    # Primary text (Warm near-black ink)
    "text_secondary": "#5e5d59",  # Secondary metadata (Olive Gray)
    "text_muted": "#87867f",      # Helper text (Stone Gray)

    # Accent & Brand (Terracotta / Warm Amber)
    "accent_teal": "#b45309",     # Action and focus ring (WCAG AA >= 4.5:1 on #faf9f5)

    # Semantic Match Colors (WCAG 2.2 AA compliant >= 4.5:1 on light surface #faf9f5)
    "match_strong": "#166534",    # Forest green (Score >= 0.35, contrast ~6.7:1)
    "match_possible": "#b45309",  # Warm Amber (0.22 <= Score < 0.35, contrast ~4.8:1)
    "match_weak": "#5e5d59",      # Slate/Olive gray (Score < 0.22, contrast ~6.3:1)
    "status_error": "#b91c1c",    # Deep Crimson error (contrast ~6.1:1)
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


CUSTOM_CSS = """
/* ==========================================================================
   Campus Notice & FAQ Assistant — Claude/Editorial Warm Light CSS Theme
   ========================================================================== */

/* Main App Canvas Styling */
.stApp {
    background-color: #f5f4ed !important;
    color: #141413 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #e8e6dc !important;
    border-right: 1px solid #d6d3c4 !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: Georgia, "Times New Roman", serif !important;
    color: #141413 !important;
}

/* Streamlit Native Input Overrides */
.stTextInput > div > div > input {
    background-color: #faf9f5 !important;
    color: #141413 !important;
    border: 1px solid #d6d3c4 !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    padding: 0.65rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #c96442 !important;
    box-shadow: 0 0 0 2px rgba(201, 100, 66, 0.2) !important;
}

/* Streamlit Button Overrides */
.stButton > button {
    background-color: #faf9f5 !important;
    color: #141413 !important;
    border: 1px solid #d6d3c4 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 120ms ease !important;
}

.stButton > button:hover {
    background-color: #f3f2ee !important;
    border-color: #c96442 !important;
    color: #a84b2c !important;
}

/* Primary Document Card */
.orca-card {
    background-color: #faf9f5;
    border: 1px solid #e8e6dc;
    border-radius: 8px;
    padding: 1.35rem 1.5rem;
    margin-bottom: 1.15rem;
    box-shadow: 0 1px 3px rgba(20, 20, 19, 0.04);
    transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
    animation: orcaFadeIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.orca-card:hover {
    border-color: #d6d3c4;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(20, 20, 19, 0.07);
}

/* Staggered Entrance Animation for 3 Cards */
.orca-card:nth-of-type(1) { animation-delay: 50ms; }
.orca-card:nth-of-type(2) { animation-delay: 150ms; }
.orca-card:nth-of-type(3) { animation-delay: 250ms; }

@keyframes orcaFadeIn {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Card Question Title (Serif Editorial Gravitas) */
.orca-question {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #141413;
    line-height: 1.4;
    margin-bottom: 0.5rem;
}

/* Card Body Answer — Disciplined width <= 68ch, line-height 1.65 */
.orca-answer {
    font-size: 1.0rem;
    line-height: 1.65;
    color: #2d2c2a;
    max-width: 68ch;
    margin-top: 0.5rem;
    margin-bottom: 0.75rem;
}

/* Meta Tags & Rows */
.orca-meta-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: #5e5d59;
    margin-bottom: 0.5rem;
}

.orca-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.orca-badge-strong {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
}

.orca-badge-possible {
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
}

.orca-badge-weak {
    background-color: #f3f2ee;
    color: #5e5d59;
    border: 1px solid #e8e6dc;
}

.orca-badge-notice {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.orca-badge-faq {
    background-color: #f3f2ee;
    color: #44403c;
    border: 1px solid #e7e5e4;
}

/* Matched Term Highlight */
.orca-highlight {
    background-color: #fef08a;
    color: #854d0e;
    padding: 0.05rem 0.25rem;
    border-radius: 3px;
    font-weight: 600;
}

/* Academic Directory (Bento Grid) */
.orca-directory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin: 1.25rem 0;
}

.orca-directory-card {
    background-color: #faf9f5;
    border: 1px solid #e8e6dc;
    border-radius: 8px;
    padding: 1.15rem 1.25rem;
    box-shadow: 0 1px 3px rgba(20, 20, 19, 0.03);
    transition: all 140ms ease;
}

.orca-directory-card:hover {
    border-color: #c96442;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(20, 20, 19, 0.07);
}

.orca-directory-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #141413;
    margin-bottom: 0.25rem;
}

.orca-directory-office {
    font-size: 0.78rem;
    font-weight: 600;
    color: #c96442;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}

.orca-directory-desc {
    font-size: 0.875rem;
    color: #5e5d59;
    line-height: 1.45;
}

/* Recent Notice Mini-Card */
.orca-notice-card {
    background-color: #faf9f5;
    border: 1px solid #e8e6dc;
    border-radius: 6px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.65rem;
    box-shadow: 0 1px 2px rgba(20, 20, 19, 0.02);
}

.orca-notice-card:hover {
    border-color: #d6d3c4;
}

/* Abstention Escalation Box (Compliant with Anti-AI-Slop Sin #5: clean card, no left border) */
.orca-abstain-box {
    background-color: #faf9f5;
    border: 1px solid #e8e6dc;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(20, 20, 19, 0.04);
}

/* Accessible Details / Expandable */
details summary {
    cursor: pointer;
    color: #5e5d59;
    font-size: 0.8125rem;
    font-weight: 500;
    transition: color 100ms ease;
}

details summary:hover {
    color: #141413;
}

/* HTML Table Styling */
table.orca-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.75rem 0;
    font-size: 0.875rem;
    background-color: #faf9f5;
}

table.orca-table th, table.orca-table td {
    border: 1px solid #e8e6dc;
    padding: 0.55rem 0.75rem;
    text-align: left;
}

table.orca-table th {
    background-color: #e8e6dc;
    color: #141413;
    font-weight: 600;
}

table.orca-table td {
    color: #2d2c2a;
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
    """Inject centralized high-craft design tokens and CSS into the Streamlit app."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)
