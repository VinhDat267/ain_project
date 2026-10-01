# Project 12 — Campus Notice and FAQ Assistant

## 1. Problem Description

Information Retrieval (IR) and Natural Language Processing (NLP) within Artificial Intelligence (AI) focus on matching human queries against semi-structured textual collections. Under the classical Vector Space Model (VSM), queries and document passages are projected into high-dimensional spaces using weighted term representations—such as Term Frequency-Inverse Document Frequency (TF-IDF)—with document relevance ranked by Cosine Similarity between vector orientations.

This project builds a conversational search assistant that helps students navigate campus administrative information. The system covers seven core operational intents:
$$\mathcal{I} = \{\text{course\_registration}, \text{exam}, \text{tuition}, \text{class\_schedule}, \text{student\_services}, \text{graduation}, \text{technical\_support}\}$$

Student queries vary from formal canonical expressions to colloquial phrasing, semantic paraphrases, and typographical errors. When a query falls outside the document corpus (out-of-corpus — OOC), the system must abstain gracefully rather than hallucinating an answer. Students will construct classical text vectorization and retrieval pipelines from first principles, implement intent classification, and calibrate relevance thresholds.

---

## 2. Provided Materials & Starter Resources

The project package provides a synthetic campus FAQ and notice corpus, benchmark query sets, generation scripts, and a Streamlit conversational interface.

### File Structure
```text
project-12-campus-faq/
├── data/
│   ├── faq.json                  # 84 structured FAQ items across 7 administrative intents
│   ├── notices.json              # 28 formal campus announcements across the same 7 intents
│   ├── intents.csv               # Taxonomy of the 7 intents with operational descriptions
│   ├── queries_test.csv          # 120 benchmark queries (normal, paraphrase, typo, out_of_corpus)
│   └── documents.md              # Human-readable index of all document identifiers and contents
├── scripts/
│   └── generate_corpus.py        # Deterministic synthetic corpus generator (default seed 42)
├── starter/
│   ├── student_core.py           # Algorithmic stubs: classify_intent and retrieve (load_documents provided)
│   └── app.py                    # Streamlit conversational search and retrieval dashboard
├── tests/
│   └── test_project_12_sanity.py # Unit tests verifying corpus integrity, schemas, and stub contracts
└── requirements.txt              # Pinned Python package dependencies (including scikit-learn, streamlit)
```

### Starter Infrastructure vs. Student Implementation
`starter/student_core.py` includes `load_documents` as a **provided helper** that handles document ingestion and metadata extraction — students do not implement this function. `starter/app.py` renders the interactive Q&A interface. Students implement the retrieval core in `starter/student_core.py`:

- **`classify_intent(query)`** — uses a supervised text model (e.g., BoW + Multinomial Naive Bayes or TF-IDF + Logistic Regression) to return a predicted intent label and posterior confidence score.
- **`retrieve(query, top_k)`** — applies TF-IDF vectorization and Cosine Similarity to return a ranked list of document matches. When similarity falls below a calibrated threshold, the method must return an empty list rather than surfacing an irrelevant passage.

Students may use `scikit-learn` for classical IR and classification. Commercial or hosted LLM APIs are strictly prohibited.

### Installation and Execution
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run starter/app.py
```

---

## 3. Requirements & Deliverables

### 3.1 Midterm Milestone — AI Core
- **Algorithmic Implementation**: Build a text retrieval and classification pipeline in `starter/student_core.py`. Implement `classify_intent` and `retrieve` as specified above. The retrieval method must implement an explicit abstention rule: return an empty list when the top Cosine Similarity score falls below a calibrated threshold.
- **Mandatory Controlled Experiment**: Evaluate the pipeline on the 120 benchmark queries in `data/queries_test.csv`. Report Mean Reciprocal Rank (MRR), Precision@$k$, and Intent Classification Accuracy across three query types: standard formal queries (`normal`), semantic reformulations (`paraphrase`), and noise-injected inputs (`typo`). Document retrieval degradation under lexical variation and analyze failure modes on out-of-corpus queries.
- **Deliverables**: Implemented `student_core.py`, evaluation scripts or notebooks, and `presentation.pdf`.
- **Grading**: Vector space modeling and retrieval correctness (15 pts); robustness analysis and abstention calibration (10 pts); oral defense with live query retrieval demo (15 pts). **Total: 40 pts.**

### 3.2 Final Milestone — AI Product
- **Interactive Application**: Package the retrieval system into a Streamlit Q&A dashboard. Required features: a natural-language question bar; intent classification badge with confidence percentage; top-k relevant excerpt cards with source attribution (`faq.json` vs. `notices.json`) and similarity scores; a similarity threshold slider; and an explicit abstention banner ("Information not found — please contact the administrative office") when confidence drops below threshold.
- **Stress & Edge Scenarios**: Demonstrate live resilience across all four evaluation query types: straightforward requests, multi-word semantic paraphrases, noisy typographical inputs, and irrelevant out-of-corpus prompts.
- **Deliverables**: Functional Streamlit application, clean GitHub repository, and `report.pdf` (IEEE format).
- **Grading**: Application ergonomics, search responsiveness, and citation transparency (25 pts); report mathematical rigor, vector derivations, and empirical tables (15 pts); oral defense against adversarial queries (10 pts). **Total: 50 pts.**

---

## 4. References

- [1] G. Salton, A. Wong, and C. S. Yang, "A vector space model for automatic indexing," *Communications of the ACM*, vol. 18, no. 11, pp. 613–620, 1975, doi: 10.1145/361219.361220.
- [2] C. D. Manning, P. Raghavan, and H. Schütze, *Introduction to Information Retrieval*. Cambridge, UK: Cambridge University Press, 2008.
- [3] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 828–864.
