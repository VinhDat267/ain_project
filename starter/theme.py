"""Centralized Theme, Design Tokens, and CSS for the Campus FAQ Assistant.

Provides disciplined Linear/Vercel dark surface hierarchy, accessible color tokens,
fluid typography, staggered fade-in animations, and prefers-reduced-motion compliance.
"""
from __future__ import annotations

import streamlit as st

TOKENS: dict[str, str] = {
    # 3-tier Surface Hierarchy (Dark Charcoal / Slate, never pure #000000)
    "surface_0": "#0d0f12",  # Base page background
    "surface_1": "#16191f",  # Cards, containers, elevation 1
    "surface_2": "#1e222a",  # Inputs, elevated buttons, badges
    "surface_border": "#2a2f3a",  # Subtle borders

    # Typography Tiers
    "text_primary": "#f1f5f9",    # Primary text (Slate-100)
    "text_secondary": "#94a3b8",  # Secondary metadata (Slate-400)
    "text_muted": "#64748b",      # Helper text (Slate-500)

    # Accent & Brand (Teal/Cyan)
    "accent_teal": "#0ea5e9",     # Action and focus ring

    # Semantic Match Colors (WCAG 2.2 AA compliant >= 4.5:1)
    "match_strong": "#10b981",    # Emerald green (Score >= 0.35)
    "match_possible": "#f59e0b",  # Amber gold (0.22 <= Score < 0.35)
    "match_weak": "#94a3b8",      # Slate gray (Score < 0.22)
    "status_error": "#ef4444",    # Error and abstention
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
   Campus Notice & FAQ Assistant — Linear/Vercel High-Craft CSS Theme
   ========================================================================== */

/* Main App Container Styling */
.stApp {
    background-color: #0d0f12 !important;
    color: #f1f5f9 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #13161c !important;
    border-right: 1px solid #2a2f3a !important;
}

/* Card Container */
.orca-card {
    background-color: #16191f;
    border: 1px solid #2a2f3a;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
    animation: orcaFadeIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.orca-card:hover {
    border-color: #3b4252;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
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

/* Card Question Title */
.orca-question {
    font-size: 1.0625rem;
    font-weight: 600;
    color: #f1f5f9;
    line-height: 1.45;
    margin-bottom: 0.5rem;
}

/* Card Body Answer — Disciplined width <= 68ch, line-height 1.6 */
.orca-answer {
    font-size: 1.0rem;
    line-height: 1.6;
    color: #e2e8f0;
    max-width: 68ch;
    margin-top: 0.5rem;
    margin-bottom: 0.75rem;
}

/* Subtle Meta Tags */
.orca-meta-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}

.orca-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}

.orca-badge-strong {
    background-color: rgba(16, 185, 129, 0.12);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.25);
}

.orca-badge-possible {
    background-color: rgba(245, 158, 11, 0.12);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.25);
}

.orca-badge-weak {
    background-color: rgba(148, 163, 184, 0.12);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.25);
}

.orca-badge-notice {
    background-color: rgba(14, 165, 233, 0.12);
    color: #38bdf8;
    border: 1px solid rgba(14, 165, 233, 0.25);
}

.orca-badge-faq {
    background-color: rgba(100, 116, 139, 0.15);
    color: #cbd5e1;
    border: 1px solid rgba(100, 116, 139, 0.25);
}

/* Abstention Escalation Box (Neutral frame, no screaming red banner) */
.orca-abstain-box {
    background-color: #16191f;
    border: 1px solid #2a2f3a;
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

/* Accessible Details / Expandable */
details summary {
    cursor: pointer;
    color: #94a3b8;
    font-size: 0.8125rem;
    font-weight: 500;
    transition: color 100ms ease;
}

details summary:hover {
    color: #f1f5f9;
}

/* HTML Table Styling */
table.orca-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.75rem 0;
    font-size: 0.875rem;
}

table.orca-table th, table.orca-table td {
    border: 1px solid #2a2f3a;
    padding: 0.5rem 0.75rem;
    text-align: left;
}

table.orca-table th {
    background-color: #1e222a;
    color: #f1f5f9;
    font-weight: 600;
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
