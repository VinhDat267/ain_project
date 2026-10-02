"""Unit tests for starter.preprocess (task A03)."""
from __future__ import annotations

import pytest
from starter.preprocess import STOPWORDS, tokenize


def test_tokenize_basic():
    text = "When is tuition due for the semester?"
    tokens = tokenize(text)
    assert tokens == ["when", "is", "tuition", "due", "for", "the", "semester"]


def test_tokenize_stopwords_removal():
    text = "When is tuition due for the semester?"
    tokens = tokenize(text, remove_stopwords=True)
    # 'when', 'is', 'due', 'for', 'the' are in STOPWORDS; 'tuition', 'semester' should remain
    assert "tuition" in tokens
    assert "semester" in tokens
    assert "due" not in tokens
    assert "is" not in tokens
    assert "the" not in tokens
    assert "when" not in tokens


def test_tokenize_empty_and_whitespace():
    assert tokenize("") == []
    assert tokenize("   ") == []
    assert tokenize("\t\n\r") == []


def test_tokenize_non_string_never_raises():
    assert tokenize(None) == []  # type: ignore[arg-type]
    assert tokenize(12345) == []  # type: ignore[arg-type]
    assert tokenize([]) == []  # type: ignore[arg-type]


def test_tokenize_punctuation_and_numbers():
    assert tokenize("Hello, world! 2026.") == ["hello", "world", "2026"]
    assert tokenize("...---...") == []
    assert tokenize("user@example.com") == ["user", "example", "com"]


def test_stopwords_structure():
    assert isinstance(STOPWORDS, frozenset)
    assert len(STOPWORDS) > 100
    assert "the" in STOPWORDS
    assert "and" in STOPWORDS
    assert "university" not in STOPWORDS
