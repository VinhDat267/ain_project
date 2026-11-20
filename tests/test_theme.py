"""Unit tests for theme, design tokens, contrast ratios, and accessibility rules."""
from pathlib import Path

import pytest

from starter.theme import CUSTOM_CSS, TOKENS, contrast_ratio, relative_luminance

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_contrast_ratio_primary_text_on_surfaces():
    """Verify that primary text meets WCAG 2.2 AA (>= 4.5:1) on all 3 surface tiers."""
    text_color = TOKENS["text_primary"]  # #f1f5f9

    ratio_surf0 = contrast_ratio(text_color, TOKENS["surface_0"])  # on #0d0f12
    ratio_surf1 = contrast_ratio(text_color, TOKENS["surface_1"])  # on #16191f
    ratio_surf2 = contrast_ratio(text_color, TOKENS["surface_2"])  # on #1e222a

    assert ratio_surf0 >= 14.0, f"Surface 0 contrast too low: {ratio_surf0}"
    assert ratio_surf1 >= 12.0, f"Surface 1 contrast too low: {ratio_surf1}"
    assert ratio_surf2 >= 9.0, f"Surface 2 contrast too low: {ratio_surf2}"


def test_contrast_ratio_semantic_match_colors():
    """Verify that semantic match badges meet WCAG 2.2 AA contrast on card surface."""
    card_bg = TOKENS["surface_1"]  # #16191f

    # Strong match (#10b981) on card
    ratio_strong = contrast_ratio(TOKENS["match_strong"], card_bg)
    assert ratio_strong >= 4.5, f"Strong match contrast too low: {ratio_strong}"

    # Possible match (#f59e0b) on card
    ratio_possible = contrast_ratio(TOKENS["match_possible"], card_bg)
    assert ratio_possible >= 4.5, f"Possible match contrast too low: {ratio_possible}"

    # Secondary text (#94a3b8) on card
    ratio_secondary = contrast_ratio(TOKENS["text_secondary"], card_bg)
    assert ratio_secondary >= 4.5, f"Secondary text contrast too low: {ratio_secondary}"

    # Accent teal (#0ea5e9) on card
    ratio_accent = contrast_ratio(TOKENS["accent_teal"], card_bg)
    assert ratio_accent >= 4.5, f"Accent teal contrast too low: {ratio_accent}"


def test_reduced_motion_rule_present():
    """Verify that CUSTOM_CSS includes prefers-reduced-motion media query (WCAG SC 2.3.3)."""
    assert "@media (prefers-reduced-motion: reduce)" in CUSTOM_CSS
    assert "animation-duration: 0.01ms !important" in CUSTOM_CSS


def test_tokens_structure():
    """Verify all required token keys are defined and are valid hex strings."""
    required_keys = [
        "surface_0", "surface_1", "surface_2", "surface_border",
        "text_primary", "text_secondary", "text_muted",
        "accent_teal", "match_strong", "match_possible", "match_weak",
        "status_error",
    ]
    for key in required_keys:
        assert key in TOKENS, f"Missing token key: {key}"
        hex_val = TOKENS[key]
        assert hex_val.startswith("#")
        assert len(hex_val) == 7
