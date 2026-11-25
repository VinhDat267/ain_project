"""Run the product on representative, edge, stress and out-of-scope scenarios.

Each scenario calls the public core (``student_core.retrieve`` and
``classify_intent``) exactly as the Streamlit app does, with the product
thresholds, and records what a student would see. The outcome rule is fixed in
advance per scenario: ``expect`` is a document id that must be ranked first,
``"top3:<id>"`` for a document that must appear among the three cards, or
``"abstain"`` when the right behaviour is to refuse.

Writes ``experiments/results/scenarios/scenarios.csv``.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from starter import student_core as core  # noqa: E402

LONG_QUERY = " ".join(["When is tuition due for the semester and what happens if I pay late?"] * 60)

SCENARIOS: list[tuple[str, str, str, str]] = [
    ("S1", "Typical question", "How do I reset my Student Portal password?", "faq_technical_support_01"),
    ("S2", "Single-swap typo", "How do I reset my Sutdent Portal password?", "faq_technical_support_01"),
    ("S3", "Three typos in one query", "Hwo do I rseet my Sutdent Portal pasword?", "faq_technical_support_01"),
    ("S4", "Light paraphrase", "I forgot my Student Portal password - how do I reset it?", "faq_technical_support_01"),
    ("S5", "Synonym paraphrase (overlap = conflict)", "Two of my finals overlap on the same day - who do I tell?",
     "top3:faq_exam_02"),
    ("S6", "Paraphrase near a topic boundary", "Where do I go to see my current classes and times?",
     "faq_class_schedule_01"),
    ("S7", "Two questions in one", "When is tuition due and when does final exam week happen?", "top3:faq_tuition_01"),
    ("S8", "Out of scope, shares 'campus'", "Can I rent a kayak from the campus recreation center?", "abstain"),
    ("S9", "Out of scope, shares 'university'", "Are university dining halls open during Thanksgiving holiday break?",
     "abstain"),
    ("S10", "Out of scope, no campus words", "What is the capital of Australia?", "abstain"),
    ("S11", "Vietnamese input", "Học phí kỳ này hạn chót là khi nào?", "abstain"),
    ("S12", "Empty input", "   ", "abstain"),
    ("S13", "Punctuation only", "???!!!", "abstain"),
    ("S14", "Stress: 840-word query", LONG_QUERY, "top3:faq_tuition_01"),
]


def run_scenario(sid: str, name: str, query: str, expect: str) -> dict:
    started = time.perf_counter()
    results = core.retrieve(query, top_k=3)
    intent, confidence = core.classify_intent(query)
    latency_ms = (time.perf_counter() - started) * 1000.0
    ranked = core._get_retriever().rank(query)
    ids = [doc["id"] for doc, _ in results]
    if expect == "abstain":
        outcome = "Pass" if not ids else "Fail"
    elif expect.startswith("top3:"):
        target = expect.split(":", 1)[1]
        outcome = "Pass" if ids[:1] == [target] else ("Partial" if target in ids else "Fail")
    else:
        outcome = "Pass" if ids[:1] == [expect] else ("Partial" if expect in ids else "Fail")
    return {
        "id": sid, "scenario": name, "query": query if len(query) <= 120 else query[:117] + "...",
        "query_words": len(query.split()), "expected": expect, "abstained": int(not ids),
        "returned_ids": "|".join(ids), "top1_cosine": round(ranked[0][1], 4) if ranked else 0.0,
        "intent": intent, "intent_confidence": round(confidence, 4), "latency_ms": round(latency_ms, 2),
        "outcome": outcome,
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/results/scenarios/scenarios.csv")
    args = parser.parse_args(argv)
    core.retrieve("warm up", top_k=3)  # build the index once
    core.classify_intent("warm up")  # and fit the classifier once, so latency is per query
    frame = pd.DataFrame([run_scenario(*scenario) for scenario in SCENARIOS])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    for row in frame.itertuples():
        print(f"{row.id:4s} {row.outcome:8s} abstained={row.abstained} cos={row.top1_cosine:.3f} "
              f"intent={row.intent}({row.intent_confidence:.2f}) {row.latency_ms:.1f} ms  {row.returned_ids}")
    print(f"Wrote {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
