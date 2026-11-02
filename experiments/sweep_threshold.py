"""E6: sweep the abstention threshold for the selected retrieval config (dev split).

Owner: Vinh (V15). Contract: INTERFACE.md section 7.5, step 2.
Reads a dev ``per_query.csv``; a query abstains when ``top1_score < th`` or
``top1_score == 0``. Picks the threshold with the highest Balanced E2E
(mean of the four per-type E2E Acc@1), ties going to the smaller threshold.

Usage:
    python experiments/sweep_threshold.py experiments/results/dev/<run_name>/per_query.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402

from experiments.evaluate import OOC, RESULTS_DIR, TYPES  # noqa: E402

THRESHOLDS = [round(i * 0.01, 2) for i in range(101)]


def sweep(per_query: pd.DataFrame, thresholds: list[float] = THRESHOLDS) -> pd.DataFrame:
    """One row per threshold: OOC rejection, false abstention, per-type E2E, Balanced E2E."""
    is_ooc = per_query["type"] == OOC
    top1 = per_query["top1_score"].astype(float)
    hit1 = per_query["hit1"].fillna(0).astype(float) == 1
    present = [t for t in TYPES if (per_query["type"] == t).any()]
    rows = []
    for th in thresholds:
        abstain = (top1 < th) | (top1 <= 0.0)
        correct = (is_ooc & abstain) | (~is_ooc & hit1 & ~abstain)
        row = {"threshold": th}
        for t in present:
            row[f"e2e_{t}"] = correct[per_query["type"] == t].mean()
        row["ooc_rejection"] = abstain[is_ooc].mean() if is_ooc.any() else float("nan")
        row["false_abstention"] = abstain[~is_ooc].mean() if (~is_ooc).any() else float("nan")
        row["balanced_e2e"] = sum(row[f"e2e_{t}"] for t in present) / len(present)
        rows.append(row)
    return pd.DataFrame(rows)


def best_threshold(table: pd.DataFrame) -> pd.Series:
    """Row with the highest Balanced E2E; ties go to the smallest threshold."""
    best = table["balanced_e2e"].max()
    return table[table["balanced_e2e"] >= best - 1e-12].sort_values("threshold").iloc[0]


def plot(table: pd.DataFrame, chosen: float, title: str, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(table["threshold"], table["ooc_rejection"], label="OOC rejection")
    ax.plot(table["threshold"], table["false_abstention"], label="False abstention")
    ax.plot(table["threshold"], table["balanced_e2e"], label="Balanced E2E", linewidth=2.2)
    ax.axvline(chosen, color="0.4", linestyle="--", linewidth=1)
    ax.annotate(f"chosen = {chosen:.2f}", (chosen, 0.04), xytext=(6, 0), textcoords="offset points", color="0.3")
    ax.set_xlabel("Threshold on top-1 cosine score")
    ax.set_ylabel("Rate")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc="center right")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv: Optional[list[str]] = None) -> int:
    """Write threshold_sweep.csv next to the input and figures/threshold_sweep_<run>.png."""
    parser = argparse.ArgumentParser(description="Sweep the abstention threshold on a dev per_query.csv.")
    parser.add_argument("per_query_csv", type=Path)
    args = parser.parse_args(argv)
    args.per_query_csv = args.per_query_csv.resolve()

    if "test" in args.per_query_csv.parts:
        print("Thresholds are chosen on the dev split only (INTERFACE.md 7.5).", file=sys.stderr)
        return 2
    per_query = pd.read_csv(args.per_query_csv)
    table = sweep(per_query)
    chosen = best_threshold(table)
    run_name = args.per_query_csv.parent.name
    table.to_csv(args.per_query_csv.parent / "threshold_sweep.csv", index=False)
    figure = RESULTS_DIR / "figures" / f"threshold_sweep_{run_name}.png"
    plot(table, float(chosen["threshold"]), f"Threshold sweep — {run_name} (dev)", figure)
    print(chosen.to_string(float_format=lambda v: f"{v:.3f}"))
    print(f"\nWrote {(args.per_query_csv.parent / 'threshold_sweep.csv').relative_to(PROJECT_ROOT)} and {figure.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
