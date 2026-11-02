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

import csv
import importlib.util
import json
import random
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT = PROJECT_ROOT / "experiments" / "dev" / "queries_dev_auto.csv"
TYPO_SEED_BASE = 42000  # typo for the i-th FAQ (sorted by id) uses random.Random(TYPO_SEED_BASE + i)
COLUMNS = ["id", "query", "type", "expected_intent", "expected_doc_id", "notes"]


def load_make_typo() -> Callable[[str, random.Random], str]:
    """Return ``_make_typo`` from the lecturer's scripts/generate_corpus.py."""
    path = PROJECT_ROOT / "scripts" / "generate_corpus.py"
    spec = importlib.util.spec_from_file_location("ain_generate_corpus", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module._make_typo


def test_target_ids() -> set[str]:
    """Expected document ids of the test split (reads only that column)."""
    with open(DATA_DIR / "queries_test.csv", newline="", encoding="utf-8") as fh:
        return {row["expected_doc_id"] for row in csv.DictReader(fh) if row["expected_doc_id"]}


def build_rows() -> list[dict[str, str]]:
    """One normal and one typo row for every FAQ that is not a test target."""
    make_typo = load_make_typo()
    excluded = test_target_ids()
    faq = json.loads((DATA_DIR / "faq.json").read_text(encoding="utf-8"))
    pool = sorted((entry for entry in faq if entry["id"] not in excluded), key=lambda entry: entry["id"])

    normal_rows, typo_rows = [], []
    for i, entry in enumerate(pool):
        normal_rows.append({
            "id": f"dev_auto_n_{i + 1:02d}",
            "query": entry["question"],
            "type": "normal",
            "expected_intent": entry["intent"],
            "expected_doc_id": entry["id"],
            "notes": "auto: verbatim FAQ question",
        })
        typo_rows.append({
            "id": f"dev_auto_t_{i + 1:02d}",
            "query": make_typo(entry["question"], random.Random(TYPO_SEED_BASE + i)),
            "type": "typo",
            "expected_intent": entry["intent"],
            "expected_doc_id": entry["id"],
            "notes": f"auto: _make_typo, seed {TYPO_SEED_BASE + i}",
        })
    return normal_rows + typo_rows


def main() -> int:
    """Write ``OUTPUT`` with ids ``dev_auto_n_XX`` (normal) and ``dev_auto_t_XX`` (typo)."""
    rows = build_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} queries to {OUTPUT.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
