"""Re-run the comparison tables of midterm slides 6 and 7 from the repo's own code.

Both tables were copied from the team's research document
(``Project12_Nghien_cuu_thuat_toan.md``), which is not in this repository. This
script recomputes every row on the course benchmark (``data/queries_test.csv``)
and writes the slide value next to the reproduced value.

Slide 6 (retrieval, 8 methods): full MRR over the 105 in-corpus queries and
Hit@1 over the 35 paraphrase queries; documents are indexed as question/title +
answer/body and ties are broken by document order. The research document did
not record every setting, so the settings below are the closest ones we
recovered by search (the ``settings`` column states them). Paraphrase Hit@1
matches on every row; full MRR matches on five rows, differs by 0.001 for the
hybrid and stopword+sublinear rows and by about 0.005 for LSA (randomised SVD).

Slide 7 (intent, 5 models): accuracy over the 105 in-corpus queries and the
mean top posterior on those queries and on the 15 out-of-corpus queries, each
model trained on the product's 231 texts. All five rows match.

Usage:
    python experiments/slide_comparisons.py
Output:
    experiments/results/midterm-sample/slide6_comparison.csv
    experiments/results/midterm-sample/slide7_intent_comparison.csv
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import normalize

from starter.intent import build_training_data
from starter.student_core import load_documents

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results" / "midterm-sample"
WORD_TOKENS_1CHAR = r"(?u)\b\w+\b"


# ----------------------------------------------------------------- slide 6
def _cosine(vectorizer, doc_texts: list[str], queries: list[str]) -> np.ndarray:
    doc_matrix = vectorizer.fit_transform(doc_texts)
    query_matrix = vectorizer.transform(queries)
    return (normalize(query_matrix) @ normalize(doc_matrix).T).toarray()


def _bm25(doc_texts: list[str], queries: list[str], k1: float = 1.5, b: float = 0.75) -> np.ndarray:
    counter = CountVectorizer(token_pattern=WORD_TOKENS_1CHAR)
    tf = counter.fit_transform(doc_texts).toarray().astype(float)
    n_docs = tf.shape[0]
    df = (tf > 0).sum(axis=0)
    idf = np.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
    doc_len = tf.sum(axis=1)
    weights = idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len[:, None] / doc_len.mean()))
    query_tf = counter.transform(queries).toarray().astype(float)
    return query_tf @ weights.T


def _lsa(doc_texts: list[str], queries: list[str], dims: int = 60) -> np.ndarray:
    tfidf = TfidfVectorizer(stop_words="english")
    doc_matrix = tfidf.fit_transform(doc_texts)
    svd = TruncatedSVD(dims, random_state=42)
    doc_latent = normalize(svd.fit_transform(doc_matrix))
    query_latent = normalize(svd.transform(tfidf.transform(queries)))
    return query_latent @ doc_latent.T


def _char35(sublinear: bool = True) -> TfidfVectorizer:
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=sublinear)


# (slide label, slide full MRR, slide paraphrase Hit@1, settings, scorer)
RETRIEVAL_METHODS = [
    ("TF-IDF char 3-5-grams", 0.943, 0.714,
     "char_wb (3,5), sublinear TF, smooth IDF, L2 (product retrieval)",
     lambda d, q: _cosine(_char35(), d, q)),
    ("Hybrid: 0.5 word + 0.5 char", 0.936, 0.714,
     "0.5 x cosine(word TF-IDF) + 0.5 x cosine(char_wb 3-5 TF-IDF, raw TF)",
     lambda d, q: 0.5 * _cosine(TfidfVectorizer(), d, q) + 0.5 * _cosine(_char35(False), d, q)),
    ("TF-IDF words", 0.927, 0.657,
     "sklearn TfidfVectorizer defaults",
     lambda d, q: _cosine(TfidfVectorizer(), d, q)),
    ("BM25 (k1 = 1.5, b = 0.75)", 0.912, 0.600,
     "Lucene IDF log(1 + (N-df+0.5)/(df+0.5)), query term counts, 1-char tokens kept",
     _bm25),
    ("TF-IDF words, 1-2-grams", 0.905, 0.600,
     "word (1,2)-grams, English stopwords removed, sublinear TF",
     lambda d, q: _cosine(TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True), d, q)),
    ("TF-IDF words, no stopwords + sublinear", 0.896, 0.629,
     "word TF-IDF, English stopwords removed, sublinear TF",
     lambda d, q: _cosine(TfidfVectorizer(stop_words="english", sublinear_tf=True), d, q)),
    ("Bag-of-Words + cosine (baseline)", 0.893, 0.571,
     "raw term counts (CountVectorizer), cosine",
     lambda d, q: _cosine(CountVectorizer(), d, q)),
    ("LSA (TF-IDF + 60-dim SVD)", 0.873, 0.600,
     "word TF-IDF without English stopwords, TruncatedSVD(60, random_state=42)",
     _lsa),
]


def _rank_metrics(scores: np.ndarray, frame: pd.DataFrame, doc_ids: list[str]) -> tuple[float, float]:
    """Return (full MRR over all rows, Hit@1 over the paraphrase rows)."""
    reciprocal, paraphrase_hits = [], []
    for row_scores, (_, row) in zip(scores, frame.iterrows()):
        ranking = [doc_ids[j] for j in np.argsort(-row_scores, kind="stable")]
        rank = ranking.index(row.expected_doc_id) + 1
        reciprocal.append(1.0 / rank)
        if row.type == "paraphrase":
            paraphrase_hits.append(rank == 1)
    return float(np.mean(reciprocal)), float(np.mean(paraphrase_hits))


def compare_retrieval() -> pd.DataFrame:
    """One row per slide-6 method with the slide and reproduced metrics."""
    documents = load_documents()
    doc_ids = [doc["id"] for doc in documents]
    doc_texts = [doc["text"] for doc in documents]
    queries = pd.read_csv(PROJECT_ROOT / "data" / "queries_test.csv")
    in_corpus = queries[queries.type != "out_of_corpus"].reset_index(drop=True)

    rows = []
    for label, slide_mrr, slide_p1, settings, scorer in RETRIEVAL_METHODS:
        mrr, p1 = _rank_metrics(scorer(doc_texts, in_corpus["query"].tolist()), in_corpus, doc_ids)
        rows.append({
            "method": label,
            "slide_mrr": slide_mrr,
            "repo_mrr": round(mrr, 3),
            "slide_paraphrase_hit1": slide_p1,
            "repo_paraphrase_hit1": round(p1, 3),
            "mrr_diff": round(round(mrr, 3) - slide_mrr, 3),
            "settings": settings,
        })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- slide 7
# (slide label, slide accuracy, slide mean confidence in-scope, out-of-corpus, settings, model factory)
INTENT_MODELS = [
    ("TF-IDF + Logistic Regression", 0.971, 0.74, 0.26,
     "word TF-IDF, sublinear TF, LogisticRegression(C=10) (product intent model)",
     lambda: make_pipeline(TfidfVectorizer(sublinear_tf=True), LogisticRegression(C=10, max_iter=2000))),
    ("TF-IDF char + Logistic Regression", 0.971, 0.76, 0.30,
     "char_wb (3,5) TF-IDF, sublinear TF, LogisticRegression(C=10)",
     lambda: make_pipeline(_char35(), LogisticRegression(C=10, max_iter=2000))),
    ("TF-IDF char + Naive Bayes", 0.962, 0.96, 0.59,
     "char_wb (3,5) TF-IDF, sublinear TF, MultinomialNB(alpha=0.1)",
     lambda: make_pipeline(_char35(), MultinomialNB(alpha=0.1))),
    ("BoW + Naive Bayes (baseline)", 0.943, 0.97, 0.45,
     "raw term counts, MultinomialNB(alpha=0.5)",
     lambda: make_pipeline(CountVectorizer(), MultinomialNB(alpha=0.5))),
    ("kNN (k = 5, cosine)", 0.876, 0.72, 0.47,
     "word TF-IDF, sublinear TF, KNeighborsClassifier(5, metric='cosine')",
     lambda: make_pipeline(TfidfVectorizer(sublinear_tf=True), KNeighborsClassifier(5, metric="cosine"))),
]


def compare_intent() -> pd.DataFrame:
    """One row per slide-7 model with the slide and reproduced metrics."""
    texts, labels = build_training_data(load_documents(), include_descriptions=True, include_questions=True)
    queries = pd.read_csv(PROJECT_ROOT / "data" / "queries_test.csv")
    in_corpus = queries[queries.type != "out_of_corpus"]
    ooc = queries[queries.type == "out_of_corpus"]

    rows = []
    for label, slide_acc, slide_in, slide_out, settings, factory in INTENT_MODELS:
        model = factory()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(texts, labels)
            accuracy = float((model.predict(in_corpus["query"]) == in_corpus["expected_intent"]).mean())
            conf_in = float(model.predict_proba(in_corpus["query"]).max(axis=1).mean())
            conf_out = float(model.predict_proba(ooc["query"]).max(axis=1).mean())
        rows.append({
            "model": label,
            "slide_accuracy": slide_acc,
            "repo_accuracy": round(accuracy, 3),
            "slide_conf_in_scope": slide_in,
            "repo_conf_in_scope": round(conf_in, 2),
            "slide_conf_ooc": slide_out,
            "repo_conf_ooc": round(conf_out, 2),
            "train_texts": len(texts),
            "settings": settings,
        })
    return pd.DataFrame(rows)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in (("slide6_comparison.csv", compare_retrieval()),
                        ("slide7_intent_comparison.csv", compare_intent())):
        frame.to_csv(RESULTS_DIR / name, index=False)
        with pd.option_context("display.width", 200):
            print(frame.drop(columns="settings").to_string(index=False))
        print(f"Wrote {(RESULTS_DIR / name).relative_to(PROJECT_ROOT)}\n")


if __name__ == "__main__":
    main()
