"""Text preprocessing shared by the retrieval module.

Owner: Viet Anh. Contract: INTERFACE.md section 5.1.
"""
from __future__ import annotations

# TODO(Viet Anh): fill in an English stopword list.
STOPWORDS: frozenset[str] = frozenset()


def tokenize(text: str, remove_stopwords: bool = False) -> list[str]:
    """Lowercase ``text`` and split it into alphanumeric word tokens.

    Return ``[]`` for empty or whitespace-only input. Never raise.
    When ``remove_stopwords`` is True, drop tokens found in ``STOPWORDS``.
    """
    raise NotImplementedError("Implement tokenize() in preprocess.py")
