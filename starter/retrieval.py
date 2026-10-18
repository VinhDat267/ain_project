"""Retrieval module: TF-IDF vectors + cosine similarity over FAQ/notice documents.

Owner: Viet Anh. Contract: INTERFACE.md section 5.
Write TF-IDF and cosine yourself (Python/numpy). scikit-learn may only be
used to cross-check scores in tests or notebooks, never in this module.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from .preprocess import tokenize

Document = dict[str, Any]
Ranked = list[tuple[Document, float]]


@dataclass(frozen=True)
class RetrievalConfig:
    """Every knob the experiments are allowed to turn (INTERFACE.md 5.2)."""

    analyzer: Literal["word", "char", "hybrid"] = "word"
    index_field: Literal["question", "text"] = "text"
    word_ngram_range: tuple[int, int] = (1, 1)
    char_ngram_range: tuple[int, int] = (3, 5)
    remove_stopwords: bool = True
    sublinear_tf: bool = False
    hybrid_alpha: float = 0.5
    threshold: float = 0.0


class Retriever:
    """Index ``documents`` once in ``__init__``, then answer queries."""

    def __init__(
        self,
        documents: list[Document],
        config: RetrievalConfig = RetrievalConfig(),
    ) -> None:
        self.documents = list(documents)
        self.config = config
        self._doc_id_to_idx = {doc["id"]: i for i, doc in enumerate(self.documents)}

        if self.config.analyzer == "word":
            self._init_word_index()
        elif self.config.analyzer == "char":
            self._init_char_index()
        elif self.config.analyzer == "hybrid":
            self._init_hybrid_index()
        else:
            raise ValueError(f"Unknown analyzer: {self.config.analyzer}")

    def _extract_word_tokens(self, text: str) -> list[str]:
        base_tokens = tokenize(text, remove_stopwords=self.config.remove_stopwords)
        min_n, max_n = self.config.word_ngram_range
        if min_n == 1 and max_n == 1:
            return base_tokens
        tokens: list[str] = []
        n_tokens = len(base_tokens)
        for n in range(min_n, max_n + 1):
            for i in range(n_tokens - n + 1):
                tokens.append(" ".join(base_tokens[i : i + n]))
        return tokens

    def _extract_char_tokens(self, text: str) -> list[str]:
        words = tokenize(text, remove_stopwords=False)
        min_n, max_n = self.config.char_ngram_range
        tokens: list[str] = []
        for word in words:
            w_len = len(word)
            for n in range(min_n, max_n + 1):
                if w_len < n:
                    continue
                for i in range(w_len - n + 1):
                    tokens.append(word[i : i + n])
        return tokens

    def _build_tfidf_matrix(
        self,
        token_lists: list[list[str]],
    ) -> tuple[dict[str, int], list[str], np.ndarray, np.ndarray]:
        df_counter: Counter[str] = Counter()
        for toks in token_lists:
            df_counter.update(set(toks))

        sorted_terms = sorted(df_counter.keys())
        vocab = {term: idx for idx, term in enumerate(sorted_terms)}
        V = len(vocab)
        N = len(self.documents)

        if V == 0 or N == 0:
            return vocab, sorted_terms, np.zeros(0, dtype=np.float64), np.zeros((N, 0), dtype=np.float64)

        df_array = np.array([df_counter[term] for term in sorted_terms], dtype=np.float64)
        idf_array = np.log((1.0 + N) / (1.0 + df_array)) + 1.0

        doc_matrix = np.zeros((N, V), dtype=np.float64)
        for i, toks in enumerate(token_lists):
            counts = Counter(toks)
            for term, count in counts.items():
                if term in vocab:
                    j = vocab[term]
                    if self.config.sublinear_tf:
                        tf = 1.0 + math.log(count)
                    else:
                        tf = float(count)
                    doc_matrix[i, j] = tf * idf_array[j]

            norm = np.linalg.norm(doc_matrix[i])
            if norm > 0.0:
                doc_matrix[i] /= norm

        return vocab, sorted_terms, idf_array, doc_matrix

    def _init_word_index(self) -> None:
        doc_tokens = [
            self._extract_word_tokens(doc.get(self.config.index_field, ""))
            for doc in self.documents
        ]
        self._vocab, self._terms, self._idf, self._doc_matrix = self._build_tfidf_matrix(doc_tokens)

    def _init_char_index(self) -> None:
        doc_tokens = [
            self._extract_char_tokens(doc.get(self.config.index_field, ""))
            for doc in self.documents
        ]
        self._char_vocab, self._char_terms, self._char_idf, self._char_doc_matrix = (
            self._build_tfidf_matrix(doc_tokens)
        )

    def _init_hybrid_index(self) -> None:
        self._init_word_index()
        self._init_char_index()

    def _compute_query_vector(
        self,
        tokens: list[str],
        vocab: dict[str, int],
        idf_array: np.ndarray,
    ) -> np.ndarray:
        V = len(vocab)
        q_vec = np.zeros(V, dtype=np.float64)
        if V == 0 or not tokens:
            return q_vec

        counts = Counter(tokens)
        for term, count in counts.items():
            if term in vocab:
                j = vocab[term]
                if self.config.sublinear_tf:
                    tf = 1.0 + math.log(count)
                else:
                    tf = float(count)
                q_vec[j] = tf * idf_array[j]

        norm = np.linalg.norm(q_vec)
        if norm > 0.0:
            q_vec /= norm
        return q_vec

    def rank(self, query: str) -> Ranked:
        """Return ALL documents with their raw cosine score, highest first.

        No threshold is applied. Ties are broken by ``id`` ascending.
        Scores lie in [0, 1].
        """
        if self.config.analyzer == "word":
            q_tokens = self._extract_word_tokens(query)
            q_vec = self._compute_query_vector(q_tokens, self._vocab, self._idf)
            scores = self._doc_matrix @ q_vec
        elif self.config.analyzer == "char":
            q_tokens = self._extract_char_tokens(query)
            q_vec = self._compute_query_vector(q_tokens, self._char_vocab, self._char_idf)
            scores = self._char_doc_matrix @ q_vec
        elif self.config.analyzer == "hybrid":
            alpha = self.config.hybrid_alpha
            q_word_tokens = self._extract_word_tokens(query)
            q_word_vec = self._compute_query_vector(q_word_tokens, self._vocab, self._idf)
            word_scores = self._doc_matrix @ q_word_vec

            q_char_tokens = self._extract_char_tokens(query)
            q_char_vec = self._compute_query_vector(q_char_tokens, self._char_vocab, self._char_idf)
            char_scores = self._char_doc_matrix @ q_char_vec

            scores = alpha * word_scores + (1.0 - alpha) * char_scores
        else:
            scores = np.zeros(len(self.documents), dtype=np.float64)

        scores = np.clip(scores, 0.0, 1.0)

        results: Ranked = [
            (self.documents[i], float(scores[i])) for i in range(len(self.documents))
        ]
        results.sort(key=lambda item: (-item[1], item[0]["id"]))
        return results

    def search(self, query: str, top_k: int = 3) -> Ranked:
        """Return ``rank(query)[:top_k]``, or ``[]`` to abstain.

        Abstain when ``top_k <= 0``, when the top-1 score is 0 (no known
        terms), or when the top-1 score is below ``config.threshold``.
        """
        if top_k <= 0:
            return []
        ranked = self.rank(query)
        if not ranked:
            return []
        top1_score = ranked[0][1]
        if top1_score <= 0.0 or top1_score < self.config.threshold:
            return []
        return ranked[:top_k]

    def explain(self, query: str, doc_id: str, top_n: int = 5) -> list[tuple[str, float]]:
        """Return the ``top_n`` features contributing most to the score of ``doc_id``.

        Each item is ``(feature, contribution)`` sorted descending; with
        L2-normalised vectors the contributions of all features sum to the
        cosine score.
        """
        if doc_id not in self._doc_id_to_idx:
            return []
        doc_idx = self._doc_id_to_idx[doc_id]

        contributions: dict[str, float] = Counter()

        if self.config.analyzer in ("word", "hybrid"):
            scale = self.config.hybrid_alpha if self.config.analyzer == "hybrid" else 1.0
            q_tokens = self._extract_word_tokens(query)
            q_vec = self._compute_query_vector(q_tokens, self._vocab, self._idf)
            doc_vec = self._doc_matrix[doc_idx]
            for term, j in self._vocab.items():
                contrib = q_vec[j] * doc_vec[j]
                if contrib > 0.0:
                    contributions[term] += scale * float(contrib)

        if self.config.analyzer in ("char", "hybrid"):
            scale = (1.0 - self.config.hybrid_alpha) if self.config.analyzer == "hybrid" else 1.0
            q_tokens = self._extract_char_tokens(query)
            q_vec = self._compute_query_vector(q_tokens, self._char_vocab, self._char_idf)
            doc_vec = self._char_doc_matrix[doc_idx]
            for term, j in self._char_vocab.items():
                contrib = q_vec[j] * doc_vec[j]
                if contrib > 0.0:
                    contributions[term] += scale * float(contrib)

        sorted_contribs = sorted(contributions.items(), key=lambda item: (-item[1], item[0]))
        return sorted_contribs[:top_n]
