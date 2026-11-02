"""The documented command must work in Windows pipes and save real results."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path


def test_sample_cli_reproduces_results_with_a_unicode_output_path(tmp_path):
    root = Path(__file__).resolve().parent.parent
    destination = tmp_path / "kết-quả"
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "ascii"
    environment["OPENBLAS_NUM_THREADS"] = "1"
    result = subprocess.run(
        [sys.executable, "-B", "scripts/evaluate.py", "--output-dir", str(destination)],
        cwd=root, env=environment, capture_output=True, timeout=90,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert "End-to-end: 108/120" in result.stdout.decode("utf-8")
    config = json.loads((destination / "config.json").read_text(encoding="utf-8"))
    assert config["intent_threshold"] == 0.34
    assert "not cross-validation" in config["evaluation"]
    with (destination / "per_query.csv").open(encoding="utf-8", newline="") as source:
        records = list(csv.DictReader(source))
    assert len(records) == 120
    assert sum(int(row["abstained"]) for row in records if row["type"] == "out_of_corpus") == 15
    with (destination / "ablation.csv").open(encoding="utf-8", newline="") as source:
        ablation = {row["rule"]: row for row in csv.DictReader(source)}
    assert [(int(ablation[key]["correct"]), int(ablation[key]["ooc_rejected"]))
            for key in ("no_gate", "cosine_only", "intent_only", "dual")] == [
                (95, 0), (96, 1), (108, 15), (108, 15),
            ]
