"""Offline sanity tests for Project 12 (campus notice/FAQ assistant).

These tests do not grade the AI core. They check that:

- the synthetic corpus is well-formed and within the spec's size ranges;
- the required experiment's query types (normal/paraphrase/typo) and the
  out-of-corpus abstain case are present in ``data/queries_test.csv``;
- no PII (emails, long digit runs) leaked into ``data/``;
- ``starter/student_core.py`` still raises ``NotImplementedError`` for the
  graded functions, while ``load_documents`` (infrastructure) works.

They must pass **offline**: nothing here crawls a website or calls a
hosted model.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_module(name: str, path: Path):
    """Load a module by explicit file path under a unique ``sys.modules`` key.

    Every project in this kit names its starter package ``starter``. Using a
    plain ``import starter.student_core`` would collide in ``sys.modules``
    when this project's tests run in the same pytest session as another
    project's tests (see the kit-wide verification command, which runs both
    Project 11 and Project 12 sanity tests together). Loading by path avoids
    that collision entirely.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


student_core = _load_module(
    "project_12_campus_faq_student_core", PROJECT_ROOT / "starter" / "student_core.py"
)

DATA_DIR = PROJECT_ROOT / "data"
PII_PATTERN = re.compile(r"@(hanu|gmail)\.|[0-9]{9,}", re.IGNORECASE)


def _load_json(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def _load_csv(name: str) -> list[dict[str, str]]:
    with open(DATA_DIR / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_intents_csv_has_5_to_10_unique_intents():
    rows = _load_csv("intents.csv")
    assert 5 <= len(rows) <= 10
    names = [row["intent"] for row in rows]
    assert len(names) == len(set(names)), "duplicate intent names in intents.csv"


def test_faq_and_notices_total_between_100_and_300():
    faq = _load_json("faq.json")
    notices = _load_json("notices.json")
    total = len(faq) + len(notices)
    assert 100 <= total <= 300, f"expected 100-300 combined FAQ/notice entries, got {total}"


def test_faq_and_notice_intents_are_known():
    known_intents = {row["intent"] for row in _load_csv("intents.csv")}
    for entry in _load_json("faq.json"):
        assert entry["intent"] in known_intents, f"unknown intent in faq.json: {entry}"
    for entry in _load_json("notices.json"):
        assert entry["intent"] in known_intents, f"unknown intent in notices.json: {entry}"


def test_faq_entries_have_required_fields_and_unique_ids():
    faq = _load_json("faq.json")
    ids = set()
    for entry in faq:
        for field in ("id", "intent", "question", "answer"):
            assert entry.get(field), f"faq entry missing {field}: {entry}"
        assert entry["id"] not in ids, f"duplicate faq id: {entry['id']}"
        ids.add(entry["id"])


def test_notices_have_required_fields_and_unique_ids():
    notices = _load_json("notices.json")
    ids = set()
    for entry in notices:
        for field in ("id", "intent", "title", "body"):
            assert entry.get(field), f"notice entry missing {field}: {entry}"
        assert entry["id"] not in ids, f"duplicate notice id: {entry['id']}"
        ids.add(entry["id"])


def test_documents_md_lists_every_document_id():
    text = (DATA_DIR / "documents.md").read_text(encoding="utf-8")
    all_ids = [e["id"] for e in _load_json("faq.json")] + [e["id"] for e in _load_json("notices.json")]
    assert all_ids, "no documents to check"
    missing = [doc_id for doc_id in all_ids if doc_id not in text]
    assert not missing, f"documents.md is missing ids: {missing[:5]}"


def test_queries_test_has_100_or_more_rows():
    rows = _load_csv("queries_test.csv")
    assert len(rows) >= 100


def test_queries_cover_normal_paraphrase_and_typo():
    rows = _load_csv("queries_test.csv")
    types = {row["type"] for row in rows}
    assert {"normal", "paraphrase", "typo"}.issubset(types), (
        "required experiment needs normal, paraphrase, and typo query types "
        f"(not Vietnamese-diacritic stripping); found: {types}"
    )
    for expected_type in ("normal", "paraphrase", "typo"):
        count = sum(1 for row in rows if row["type"] == expected_type)
        assert count >= 5, f"too few '{expected_type}' queries: {count}"


def test_queries_are_ascii_english_not_diacritic_stripping():
    rows = _load_csv("queries_test.csv")
    for row in rows:
        query = row["query"]
        assert query == query.encode("ascii", "ignore").decode("ascii"), (
            "queries_test.csv must stay ASCII English; robustness is typo/"
            f"paraphrase, not Vietnamese-diacritic stripping. Offending row: {row}"
        )


def test_queries_include_out_of_corpus_with_no_expected_document():
    rows = _load_csv("queries_test.csv")
    out_of_corpus = [row for row in rows if row["type"] == "out_of_corpus"]
    assert len(out_of_corpus) >= 5, "need several out-of-corpus queries for the abstain demo"
    for row in out_of_corpus:
        assert row["expected_doc_id"] == "", f"out-of-corpus row should not expect a document: {row}"


def test_normal_paraphrase_typo_triplets_share_expected_doc_id():
    rows = _load_csv("queries_test.csv")
    by_doc: dict[str, set[str]] = {}
    for row in rows:
        if row["type"] in ("normal", "paraphrase", "typo") and row["expected_doc_id"]:
            by_doc.setdefault(row["expected_doc_id"], set()).add(row["type"])
    triplets = [doc_id for doc_id, types in by_doc.items() if len(types) == 3]
    assert len(triplets) >= 10, (
        "expected several documents with a full normal/paraphrase/typo "
        f"triplet for the required experiment; found {len(triplets)}"
    )


def test_no_pii_in_data_files():
    for path in DATA_DIR.iterdir():
        if path.is_file() and path.suffix in (".json", ".csv", ".md"):
            text = path.read_text(encoding="utf-8")
            assert not PII_PATTERN.search(text), f"possible PII pattern found in {path}"


def test_load_documents_infrastructure_works_without_the_core():
    docs = student_core.load_documents()
    assert len(docs) == len(_load_json("faq.json")) + len(_load_json("notices.json"))
    for doc in docs:
        assert doc["id"] and doc["intent"] and doc["text"]


def test_classify_intent_is_not_implemented():
    with pytest.raises(NotImplementedError):
        student_core.classify_intent("How do I register for classes?")


def test_retrieve_is_not_implemented():
    with pytest.raises(NotImplementedError):
        student_core.retrieve("How do I register for classes?")


def test_starter_app_compiles():
    import py_compile

    py_compile.compile(str(PROJECT_ROOT / "starter" / "app.py"), doraise=True)


def test_generator_is_deterministic_for_default_seed(tmp_path):
    """Regenerating with --seed 42 must reproduce the committed data exactly."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "generate_corpus", PROJECT_ROOT / "scripts" / "generate_corpus.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    faq = module.build_faq_entries()
    notices = module.build_notice_entries()
    queries = module.build_queries(42)

    assert faq == _load_json("faq.json")
    assert notices == _load_json("notices.json")

    committed_queries = _load_csv("queries_test.csv")
    assert len(queries) == len(committed_queries)
    for generated, committed in zip(queries, committed_queries):
        assert generated["query"] == committed["query"]
        assert generated["type"] == committed["type"]
