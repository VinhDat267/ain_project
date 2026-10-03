"""E6: sweep the abstention threshold for the selected retrieval config (dev split).

Owner: Vinh (V15). Contract: INTERFACE.md section 7.5, step 2.
Reads a dev ``per_query.csv``; a query abstains when ``top1_score < th`` or
``top1_score == 0``. Picks the threshold with the highest Balanced E2E
(mean of the four per-type E2E Acc@1), ties going to the smaller threshold.

Usage:
    python experiments/sweep_threshold.py experiments/results/dev/<run_name>/per_query.csv
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

THRESHOLDS = [round(i * 0.01, 2) for i in range(101)]


def sweep(per_query_csv: Path) -> "pandas.DataFrame":  # noqa: F821
    """One row per threshold: OOC rejection, false abstention, per-type E2E, Balanced E2E."""
    raise NotImplementedError("Implement sweep()")


def main(argv: Optional[list[str]] = None) -> int:
    """Write threshold_sweep.csv next to the input and figures/threshold_sweep.png."""
    raise NotImplementedError("Implement main()")


if __name__ == "__main__":
    raise SystemExit(main())
