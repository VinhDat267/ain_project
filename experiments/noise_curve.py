"""E3b: retrieval quality as the number of typos per query grows (k = 0..3).

Owner: Viet Anh (A09). Contract: INTERFACE.md section 7.9.
Input: the 49 ``normal`` queries of experiments/dev/queries_dev_auto.csv.
For level k, apply the lecturer's ``_make_typo`` k times; the j-th call on the
i-th query uses ``random.Random(1000 * k + 100 * j + i)``.

Usage:
    python experiments/noise_curve.py
"""
from __future__ import annotations

from typing import Optional

LEVELS = (0, 1, 2, 3)


def noisy_query(text: str, k: int, i: int) -> str:
    """Return ``text`` with ``k`` adjacent-letter-swap typos (seeded as above)."""
    raise NotImplementedError("Implement noisy_query()")


def main(argv: Optional[list[str]] = None) -> int:
    """Hit@1 and MRR@10 per level for Jaccard, word, char and hybrid retrieval.

    Write experiments/results/dev/noise_curve.csv and figures/noise_curve.png.
    """
    raise NotImplementedError("Implement main()")


if __name__ == "__main__":
    raise SystemExit(main())
