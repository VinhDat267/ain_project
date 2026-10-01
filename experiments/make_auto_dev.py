"""Generate experiments/dev/queries_dev_auto.csv: 49 normal + 49 typo dev queries.

Owner: Vinh (V05). Contract: INTERFACE.md section 8.
Uses only the FAQ entries that are NOT expected documents of the test split;
from data/queries_test.csv it reads the ``expected_doc_id`` column and nothing
else. Typos come from the lecturer's own ``_make_typo`` in
scripts/generate_corpus.py, so dev typos follow the same recipe as test typos.

Usage:
    python experiments/make_auto_dev.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT = PROJECT_ROOT / "experiments" / "dev" / "queries_dev_auto.csv"
TYPO_SEED_BASE = 42000  # typo for the i-th FAQ (sorted by id) uses random.Random(TYPO_SEED_BASE + i)


def main() -> int:
    """Write ``OUTPUT`` with ids ``dev_auto_n_XX`` (normal) and ``dev_auto_t_XX`` (typo)."""
    raise NotImplementedError("Implement make_auto_dev.main()")


if __name__ == "__main__":
    raise SystemExit(main())
