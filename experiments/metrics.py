"""Ranking metrics for a single query with exactly one relevant document.

Owner: Vinh. Definitions: INTERFACE.md section 7.2.
"""
from __future__ import annotations

from collections.abc import Sequence


def reciprocal_rank(ranked_ids: Sequence[str], expected_id: str, k: int = 10) -> float:
    """``1 / rank`` of ``expected_id`` within the first ``k`` ids, else 0."""
    raise NotImplementedError("Implement reciprocal_rank()")


def hit_at_k(ranked_ids: Sequence[str], expected_id: str, k: int) -> int:
    """1 if ``expected_id`` is among the first ``k`` ids, else 0."""
    raise NotImplementedError("Implement hit_at_k()")


def precision_at_k(ranked_ids: Sequence[str], expected_id: str, k: int) -> float:
    """Relevant ids in the first ``k`` divided by ``k`` (at most 1/k here)."""
    raise NotImplementedError("Implement precision_at_k()")
