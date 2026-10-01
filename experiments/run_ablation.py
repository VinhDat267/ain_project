"""Run named experiment groups on the dev split, or the frozen batch on the test split.

Owner: Vinh (V11); Viet Anh adds the E3/E4 groups. Contract: INTERFACE.md 7.4 and 7.8.

Usage:
    python experiments/run_ablation.py --split dev --group E3
    python experiments/run_ablation.py --split test --final                       # ONCE, 15/10 21:00
    python experiments/run_ablation.py --split test --final --rerun-reason "..."  # evaluation-bug fix only
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.intent import IntentConfig  # noqa: E402
from starter.retrieval import RetrievalConfig  # noqa: E402

# (retrieval, intent, intent_mode); retrieval may be "jaccard",
# intent may be "majority", "knn1" or "knn5", intent_mode is "full" or "lodo".
Run = tuple[Union[RetrievalConfig, str], Union[IntentConfig, str], str]

# Group name ("E1".."E5") -> run name -> Run. Each owner adds their group by PR.
EXPERIMENTS: dict[str, dict[str, Run]] = {}

# Frozen at V16 (14/10). Must contain a run named "final" (the DEFAULT configs).
FROZEN_COMPARISONS: dict[str, Run] = {}

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
TEST_LOCK = RESULTS_DIR / "test" / "LOCK"
RERUN_LOG = RESULTS_DIR / "test" / "RERUN_LOG.md"


def run_group(group: str) -> "pandas.DataFrame":  # noqa: F821
    """Evaluate every run of ``EXPERIMENTS[group]`` on dev; write ablation_<group>.csv."""
    raise NotImplementedError("Implement run_group()")


def run_frozen_on_test(rerun_reason: Optional[str] = None) -> None:
    """Evaluate ``FROZEN_COMPARISONS`` on the test split in one batch.

    Write ``TEST_LOCK`` only after the whole batch succeeds. If the lock exists,
    refuse unless ``rerun_reason`` is given and the hash of
    ``FROZEN_COMPARISONS`` matches the one stored in the lock; then append to
    ``RERUN_LOG``.
    """
    raise NotImplementedError("Implement run_frozen_on_test()")


def main(argv: Optional[list[str]] = None) -> int:
    """Parse ``--split``, ``--group``, ``--final`` and ``--rerun-reason``."""
    raise NotImplementedError("Implement main()")


if __name__ == "__main__":
    raise SystemExit(main())
