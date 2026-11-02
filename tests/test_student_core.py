import sys
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starter.student_core import classify_intent, load_documents, retrieve


def test_load_documents_structure():
    docs = load_documents()
    assert len(docs) == 112
    for doc in docs:
        assert "id" in doc
        assert "intent" in doc
        assert "question" in doc
        assert "answer" in doc
        assert "text" in doc
        assert "source" in doc
        assert doc["source"] in ("faq.json", "notices.json")


def test_retrieve_basic_query():
    results = retrieve("When is tuition due for the semester?", top_k=3)
    assert len(results) > 0
    top_doc, top_score = results[0]
    assert top_doc["intent"] == "tuition"
    assert top_score > 0.3


def test_retrieve_out_of_corpus_abstains():
    results = retrieve("Which bus goes to the city zoo on Sundays?")
    # No documents about zoo/bus in FAQ/notices -> abstains with []
    assert results == []


def test_retrieve_empty_query():
    assert retrieve("") == []
    assert retrieve("   ") == []


def test_classify_intent_basic():
    intent, conf = classify_intent("When is tuition due for the semester?")
    assert intent == "tuition"
    assert 0.0 <= conf <= 1.0


def test_classify_intent_empty_never_raises():
    intent, conf = classify_intent("")
    assert isinstance(intent, str)
    assert isinstance(conf, float)


@pytest.mark.parametrize("foreign_starter", [False, True])
def test_document_loader_works_without_ml_dependencies_or_owning_the_starter_namespace(foreign_starter):
    # The lecturer can load this file by path alongside other projects' starters.
    script = f"""
import importlib.util, sys, types
from pathlib import Path
if {foreign_starter!r}:
    other = types.ModuleType('starter')
    other.__path__ = []
    sys.modules['starter'] = other
path = Path('starter/student_core.py').resolve()
spec = importlib.util.spec_from_file_location('campus_core', path)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
print(len(core.load_documents()))
"""
    result = subprocess.run(
        [sys.executable, "-B", "-S", "-c", script], cwd=PROJECT_ROOT,
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "112"
