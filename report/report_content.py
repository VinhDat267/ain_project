"""Content of the final report (English), consumed by build_final_report.py.

Markup inside strings: **bold**, *italic*, _{subscript}, ^{superscript},
[@key] or [@a; @b] for IEEE citations (numbered in order of first use), and
{tab:x} / {fig:x} / {eq:x} for the number of a labelled table, figure or
equation. Every number below comes from a committed result file; the file is
named next to each table.
"""

TITLE = "Campus Notice and FAQ Assistant: Classical TF-IDF Retrieval with Dual-Gate Abstention"

MEMBERS = [
    ("Nguyễn Đạt Vinh", "2301040198", True),
    ("Lương Việt Anh", "2301040004", False),
    ("Nguyễn Ánh Dương", "2401040080", False),
]

ABSTRACT = (
    "Students at Hanoi University (HANU) ask the same administrative questions about registration, tuition, "
    "examinations and graduation every semester, and an assistant that invents a deadline is worse than no "
    "assistant at all. We built an offline Campus Notice and FAQ Assistant that answers English questions only "
    "from a fixed synthetic corpus of 112 documents (84 FAQs and 28 notices over seven intents) and refuses when "
    "the corpus has no answer. Retrieval is TF-IDF over word-bounded character 3–5-grams with sublinear term "
    "frequency and cosine similarity, written from first principles in NumPy; a word TF-IDF Logistic Regression "
    "model predicts one of seven intents; and a dual gate answers only when the best cosine is at least 0.15 and "
    "the intent posterior is at least 0.34. The core is packaged as a Streamlit application with source cards, "
    "match labels, per-feature explanations and a refusal banner that names the failed gate. On the course's "
    "120-query benchmark the system reaches a full MRR of 0.943, 97.1% intent accuracy, 15/15 refused "
    "out-of-corpus questions and 108/120 correct end-to-end decisions, against a balanced end-to-end accuracy of "
    "0.614 for a Jaccard baseline. That benchmark, however, was inspected during development. On 146 "
    "team-written development queries the same configuration refuses only 12/20 out-of-corpus questions and "
    "ranks the correct document first for 5/28 heavy paraphrases. The main limitation is lexical matching: the "
    "system cannot connect synonyms, and its abstention threshold does not transfer from the benchmark to fresh "
    "questions."
)

KEYWORDS = "information retrieval, TF-IDF, character n-grams, selective prediction, intent classification"

# --- MathML helpers -------------------------------------------------------
def _r(*parts):
    return "<mrow>" + "".join(parts) + "</mrow>"


def mi(x, normal=False):
    return f'<mi mathvariant="normal">{x}</mi>' if normal else f"<mi>{x}</mi>"


def mb(x):
    return f'<mi mathvariant="bold">{x}</mi>'


def mo(x):
    return f"<mo>{x}</mo>"


def mn(x):
    return f"<mn>{x}</mn>"


def mt(x):
    return f"<mtext>{x}</mtext>"


def frac(a, b):
    return f"<mfrac>{_r(a)}{_r(b)}</mfrac>"


def sub(a, b):
    return f"<msub>{_r(a)}{_r(b)}</msub>"


def sup(a, b):
    return f"<msup>{_r(a)}{_r(b)}</msup>"


def hat(a):
    return f"<mover accent=\"true\">{_r(a)}<mo>^</mo></mover>"


def sumover(lo, hi, body):
    if hi is None:
        return f"<munder><mo>∑</mo>{_r(lo)}</munder>" + body
    return f"<munderover><mo>∑</mo>{_r(lo)}{_r(hi)}</munderover>" + body


def par(*a):
    return '<mfenced open="(" close=")" separators="">' + _r(*a) + "</mfenced>"


def norm(*a):
    return '<mfenced open="‖" close="‖" separators="">' + _r(*a) + "</mfenced>"


def math(*parts):
    return '<math xmlns="http://www.w3.org/1998/Math/MathML">' + "".join(parts) + "</math>"


LN = mi("ln", normal=True)
EXP = mi("exp", normal=True)

EQ_TFIDF = math(
    mi("w"), par(mi("t"), mo(","), mi("d")), mo("="), par(mn("1"), mo("+"), LN, mo("&#8289;"), mi("tf"),
                                                     par(mi("t"), mo(","), mi("d"))),
    mo("·"), mi("idf"), par(mi("t")), mo(","), mt(" "),
    mi("idf"), par(mi("t")), mo("="), LN, par(frac(mn("1") + mo("+") + mi("N"),
                                                   mn("1") + mo("+") + mi("df") + par(mi("t")))), mo("+"), mn("1"),
)
EQ_COS = math(
    mi("s"), par(mi("q"), mo(","), mi("d")), mo("="),
    frac(mb("q") + mo("·") + mb("d"), norm(mb("q")) + norm(mb("d"))), mo("="),
    sumover(mi("t") + mo("∈") + mi("V"), None, sub(hat(mi("q")), mi("t")) + sub(hat(mi("d")), mi("t"))),
)
EQ_SOFTMAX = math(
    mi("P"), par(mi("c"), mo("|"), mb("x")), mo("="),
    frac(EXP + par(sub(mb("w"), mi("c")), mo("·"), mb("x"), mo("+"), sub(mi("b"), mi("c"))),
         sumover(mi("k") + mo("=") + mn("1"), mn("7"),
                 EXP + par(sub(mb("w"), mi("k")), mo("·"), mb("x"), mo("+"), sub(mi("b"), mi("k"))))),
)
EQ_LOSS = math(
    sub(mi("min", normal=True), mi("W") + mo(",") + mb("b")), mt(" "), frac(mn("1"), mn("2")),
    sup(norm(mi("W")), mn("2")), mo("+"), mi("C"),
    sumover(mi("j") + mo("=") + mn("1"), mi("n"),
            mo("−") + LN + mi("P") + par(sub(mi("y"), mi("j")), mo("|"), sub(mb("x"), mi("j")))),
    mo(","), mt(" "), mi("C"), mo("="), mn("10"),
)
EQ_GATE = math(
    mi("a"), par(mi("q")), mo("="),
    "<mrow><mo>{</mo><mtable columnalign=\"left\">"
    "<mtr><mtd>" + _r(mt("top-"), mi("k"), mt(" ranking of "), mi("D"), mt(" ")) + "</mtd><mtd>" +
    _r(mt("if "), sub(mi("s"), mn("1")), par(mi("q")), mo("≥"), sub(mi("τ"), mi("s")),
       mt(" and "), mi("p"), par(mi("q")), mo("≥"), sub(mi("τ"), mi("p"))) + "</mtd></mtr>"
    "<mtr><mtd>" + _r(mo("∅")) + "</mtd><mtd>" + _r(mt("otherwise")) + "</mtd></mtr>"
    "</mtable></mrow>",
)
EQ_MRR = math(
    mt("MRR"), mo("="), frac(mn("1"), mo("|") + mi("Q") + mo("|")),
    sumover(mi("i") + mo("=") + mn("1"), mo("|") + mi("Q") + mo("|"), frac(mn("1"), sub(mi("r"), mi("i")))),
)

# --- Body -----------------------------------------------------------------
# Block kinds: h1, h2, p, bullets, eq, table, fig, fig2, code, refs-marker.
BLOCKS = [
    ("h1", "1  Introduction and Problem Definition"),
    ("h2", "1.1  Context and Motivation"),
    ("p", "Every semester, HANU students ask the academic office, the bursar and the IT help desk the same "
          "questions: when tuition is due, what to do when a section is full, whom to tell about two exams at the "
          "same time, how to reset a portal password. The answers already exist as FAQ entries and official "
          "notices, but they are spread over several offices, so students queue at a counter or ask in group "
          "chats where answers are often out of date. A search box that matches exact words fails on the way "
          "students type: they misspell (“Sutdent Portal”), reword (“two of my finals overlap” "
          "instead of “exam conflict”) and ask about things the university documents do not cover, such "
          "as restaurants near campus."),
    ("p", "A generative chatbot would answer all of these fluently, but in an administrative setting fluency is a "
          "risk: a large language model can state an invented deadline or refund rule with full confidence "
          "[@ji], and the course forbids hosted language models as the core algorithm. Project 12 of the course "
          "kit [@kit] therefore asks for a classical solution: retrieve the right existing document, say which "
          "topic the question belongs to, and say plainly when nothing in the corpus answers it. Our assistant "
          "never generates text; every answer a student sees is a document the office wrote."),
    ("h2", "1.2  Problem Statement"),
    ("p", "Given a free-text English question *q* and a fixed corpus *D* of *N* = 112 documents, each labelled "
          "with one of seven intents, the system must return either a ranked list of at most *k* = 3 documents "
          "with their similarity scores, together with the predicted intent and its confidence, or an empty list "
          "(an abstention) when the corpus does not answer *q*. Table {tab:spec} summarises the task."),
    ("table", "spec", "Problem specification.",
     [["Item", "Description"]],
     [["Input", "A free-text English question, e.g. “When is tuition due for the semester?”"],
      ["Output", "One of 7 intents with a confidence and the top-3 documents with source and cosine score, or "
                 "the refusal “Information not found — please contact the administrative office.”"],
      ["Corpus", "84 FAQs and 28 dated notices, 16 documents per intent, synthetic, provided by the course [@kit]"],
      ["Constraints", "Offline on a laptop CPU, Python 3.11; retrieval written by the team in NumPy; "
                      "scikit-learn only for intent classification; no language-model API"],
      ["Assumptions", "Each in-corpus question has exactly one correct document; questions are in English; the "
                      "corpus is correct and current"]],
     [1900, 7170], {}),
    ("h2", "1.3  Objectives and Contributions"),
    ("bullets", [
        "A retrieval engine written from first principles (word-bounded character n-gram TF-IDF, cosine ranking "
        "and an exact per-feature explanation) whose scores match scikit-learn’s TfidfVectorizer in the "
        "test suite.",
        "A dual-gate abstention rule that combines a cosine floor with an intent-confidence gate, with an "
        "ablation showing which gate actually refuses out-of-corpus questions.",
        "A Streamlit product with source attribution, match labels, explanations, threshold sliders and an "
        "evaluation dashboard; the same core is also served by a FastAPI and React web app.",
        "An evaluation beyond the course benchmark (a 146-query development split, a typo-noise curve, "
        "cross-validation, a threshold sweep and 14 scripted scenarios) that shows where the midterm results "
        "do not generalise.",
    ]),

    ("h1", "2  AI Background and Formal Formulation"),
    ("p", "The project belongs to the Language topic of the course [@cs50]. Documents and queries are sparse "
          "vectors over a vocabulary compared geometrically, as in the vector space model [@salton; @manning]; "
          "the intent classifier is a supervised learner [@aima]; and the abstention rule makes the system a "
          "selective predictor that may decline to answer [@chow]."),
    ("h2", "2.1  Formal Problem Formulation"),
    ("p", "Let *D* = {*d*_{1}, …, *d*_{N}}, *N* = 112, be the corpus and *C* = {*c*_{1}, …, *c*_{7}} the intents "
          "course_registration, exam, tuition, class_schedule, student_services, graduation and "
          "technical_support. Each document is its question (or notice title) followed by its answer (or body)."),
    ("p", "**Vocabulary.** The product analyzer lowercases a text, splits it on white space, pads each word *w* "
          "as “ *w* ” and emits every character n-gram of length 3 to 5 inside the padded word "
          "(char_wb). Over the corpus this gives a vocabulary *V* of 8,398 features, against 845 word unigrams."),
    ("p", "**Document vectors.** With tf(*t*, *d*) the count of feature *t* in *d* and df(*t*) the number of "
          "documents containing *t*, each document is a vector in ℝ^{|V|} with components"),
    ("eq", "tfidf", EQ_TFIDF),
    ("p", "for tf > 0 (and 0 otherwise), normalised to unit L2 length. A query is mapped in the same way with the "
          "corpus idf, and features never seen in *D* are dropped."),
    ("p", "**Similarity and ranking.** For unit vectors, cosine similarity is a dot product that decomposes over "
          "the shared features:"),
    ("eq", "cos", EQ_COS),
    ("p", "Ranking sorts *D* by *s*(*q*, ·), ties broken by document id. Each summand is the contribution of one "
          "feature, which explain() reports, so the explanation is exact rather than approximate."),
    ("p", "**Intent.** The classifier is trained on *n* = 231 labelled texts (*x*_{j}, *y*_{j}): the 112 full "
          "texts, the 112 questions or titles and the 7 intent descriptions of intents.csv. Each **x** is a "
          "sublinear word TF-IDF vector, and multinomial Logistic Regression models"),
    ("eq", "softmax", EQ_SOFTMAX),
    ("p", "fitted by minimising the L2-regularised cross-entropy"),
    ("eq", "loss", EQ_LOSS),
    ("p", "**Abstention.** Let *s*_{1}(*q*) be the highest cosine and *p*(*q*) = max_{c} *P*(*c* | *q*) the "
          "intent confidence. The answer is"),
    ("eq", "gate", EQ_GATE),
    ("p", "with *τ*_{s} = 0.15 and *τ*_{p} = 0.34. An in-corpus question is handled correctly when *a*(*q*) ranks "
          "the expected document first; an out-of-corpus question when *a*(*q*) = ∅."),
    ("h2", "2.2  Selected Method"),
    ("p", "As a hand-worked example of Equations ({eq:tfidf}) and ({eq:cos}) with word features, take *N* = 3 "
          "documents D1 “tuition fees due semester”, D2 “exam schedule posted semester” and D3 "
          "“tuition payment deadline”, and the query “tuition semester deadline”. A feature "
          "found in one document gets idf = ln(4/2) + 1 = 1.693, while *tuition* and *semester* occur in two and "
          "get ln(4/3) + 1 = 1.288, so the rare word *deadline* weighs more. After L2 normalisation the query is "
          "(deadline 0.681, semester 0.518, tuition 0.518) and D3 is (deadline 0.623, payment 0.623, tuition "
          "0.474). Hence *s*(*q*, D3) = 0.681 × 0.623 + 0.518 × 0.474 = 0.424 + 0.245 = 0.669, ahead of D1 "
          "(0.443) and D2 (0.208), and explain() for D3 returns exactly the terms 0.424 (deadline) and 0.245 "
          "(tuition). Our Retriever reproduces these values (notes/hand_calc.md)."),
    ("p", "With char_wb features the same computation runs over sub-word units. The misspelling "
          "“sutdent” still shares n-grams such as “dent” and “ent ” with "
          "“student”, so a swap removes only the features that cross the swapped letters, and the "
          "cosine of the right FAQ drops only from 0.539 to 0.528 (Section 5). For the classifier, “Can I "
          "rent a kayak from the campus recreation center?” shares only generic words with the training "
          "texts, so the seven logits of Equation ({eq:softmax}) are close and the posterior is flat: its "
          "maximum is 0.29, below *τ*_{p}, although its best cosine of 0.39 passes the floor. This is the case "
          "the second gate was designed for."),
    ("h2", "2.3  Baseline and Related Work"),
    ("p", "**Baselines.** The main baseline is Jaccard word overlap with a majority-class intent and no "
          "abstention, the simplest system a student could write, run on the same corpus, queries and metrics. "
          "We also report the course’s default word TF-IDF retriever (stop words removed, raw TF) with a "
          "1-nearest-neighbour intent, Okapi BM25 [@bm25] with *k*_{1} = 1.5 and *b* = 0.75 written by the team, "
          "and the intent models of Table {tab:cv}."),
    ("p", "**Related work.** TF-IDF in the vector space model [@salton; @manning] remains the standard sparse "
          "baseline for document and FAQ retrieval. BM25 [@bm25] adds term-frequency saturation and length "
          "normalisation, but its unbounded scores make one absolute refusal threshold harder to set than for "
          "cosine in [0, 1]. Sub-word units make lexical models robust to misspellings [@bojanowski]. For FAQ "
          "retrieval, Sakata et al. [@sakata] show that matching the query against the answer as well as the "
          "stored question helps reworded questions, in line with our finding that indexing question plus answer "
          "beats the question alone (development paraphrase MRR@10 0.244 against 0.106). Dense retrievers such "
          "as DPR [@dpr] would close our synonym gap but need pretrained neural encoders. Declining to answer below a confidence threshold is Chow’s reject "
          "option [@chow], studied today as selective classification [@geifman]."),

    ("h1", "3  System Architecture and Algorithm Design"),
    ("h2", "3.1  User Flow"),
    ("p", "The student starts the Streamlit application with one command (Appendix A), types a question or picks "
          "a sample and presses Enter. Figure {fig:flow1}(a) shows the typical case: a banner with the predicted "
          "intent, its confidence and the matching office, then three answer cards. Each card states its source "
          "(FAQ entry, or Notice with its publication date), a match label derived from the cosine (Strong ≥ "
          "0.35, Possible 0.22–0.35, Weak < 0.22, shown as text and icon, not colour alone), a score bar and the "
          "full answer with the query terms highlighted. *Helpful* and *Needs clarification* buttons store a "
          "vote in a local file."),
    ("p", "When the gate refuses (Figure {fig:flow1}(b)), the application shows the refusal banner required by "
          "the assignment, states which gate failed with the measured values (here the cosine 0.39 passed and the "
          "intent confidence 29% failed), lists the seven covered topics and suggests how to rephrase. It shows "
          "no office routing, because the intent guess on a refused question is unreliable. A question in "
          "Vietnamese receives a bilingual notice that the corpus is in English."),
    ("fig2", "flow1", "Student view of the application: answer cards and the refusal path.",
     [("../output/playwright/live-demo/01-normal.png", "(a) A typical question answered with three cards."),
      ("../output/playwright/live-demo/05-kayak.png", "(b) An out-of-corpus question refused; the banner names "
                                                       "the failed gate.")]),
    ("p", "*Research & Inspector Mode* (Figure {fig:flow2}(a)) exposes the cosine floor, the intent gate and *k* "
          "as sliders, as the assignment requires, and adds an explain() table under each card listing the "
          "n-grams that contribute most to its cosine. The second tab (Figure {fig:flow2}(b)) is an evaluation "
          "dashboard that reads every number from the result files of Section 4."),
    ("fig2", "flow2", "Inspector mode and the evaluation dashboard.",
     [("figures/fig_inspector_explain.png", "(a) Threshold sliders and explain() for failure F1 of Section 5.2."),
      ("figures/fig_dashboard.png", "(b) Dashboard read from the committed result files.")]),
    ("h2", "3.2  System Overview"),
    ("fig", "arch", "High-level architecture of the system.", "figures/fig_architecture.png", 10.5),
    ("p", "In Figure {fig:arch}, the user interface (starter/app.py, or the React front end served by FastAPI "
          "[@fastapi] in webapp/) sends the raw query to the public core API in starter/student_core.py, which "
          "exposes the two functions fixed by the assignment, retrieve(query, top_k) and classify_intent(query). "
          "On first use the core builds the char_wb index of the 112 documents and fits the intent classifier, "
          "and caches both. The retriever returns every document with its cosine and the classifier returns the "
          "seven posteriors; the dual gate of Equation ({eq:gate}) then returns the top-*k* (document, score) "
          "pairs or an empty list, which the interface renders as cards or a refusal. The evaluation scripts call "
          "the same two functions with the same configuration objects, so Sections 4 and 5 measure exactly the "
          "code a student uses; the web app reuses the core unchanged behind REST endpoints."),
    ("h2", "3.3  Algorithm Design"),
    ("p", "Algorithm 1 gives the query path; the index (vocabulary, idf and the row-normalised document matrix "
          "*M*) is built once with Equation ({eq:tfidf})."),
    ("code", [
        "**Algorithm 1: Answer a question with dual-gate abstention**",
        "Input:  query q; vocabulary V, idf, unit document matrix M (N x |V|);",
        "        intent model P(c|x); tau_s = 0.15, tau_p = 0.34; k = 3",
        "Output: at most k (document, score) pairs, or [] to abstain",
        "1: F <- char_wb_ngrams(lowercase(q), 3, 5)       # query features",
        "2: for each distinct t in F that is in V:",
        "3:     q_t <- (1 + ln count(t, F)) * idf(t)",
        "4: if ||q|| = 0: return []                        # no known feature",
        "5: q <- q / ||q||;  s <- M q                      # N cosine scores",
        "6: R <- documents sorted by s descending, ties by id",
        "7: if s(R_1) < tau_s: return []                   # gate 1: similarity floor",
        "8: p <- max_c P(c | word_tfidf(q))                # gate 2: intent confidence",
        "9: if p < tau_p: return []",
        "10: return the first k items of R",
    ]),
    ("p", "**Complexity.** Building the index costs O(*L*) for a corpus of total length *L* plus O(*N*|*V*|) to "
          "fill the dense 112 × 8,398 matrix (7.5 MB in float64). A query of length ℓ costs O(ℓ) for its "
          "features, O(*N*|*V*|) for the matrix-vector product, O(*N* log *N*) for the sort and O(7|*V*_{w}|) for "
          "the classifier over the word vocabulary *V*_{w}: linear in the corpus size, about one millisecond per "
          "question here (Section 4.3). An inverted index would matter only for much larger corpora."),
    ("h2", "3.4  Implementation and Design Decisions"),
    ("p", "The system uses Python 3.11, NumPy 1.26 [@numpy] for the retriever, scikit-learn 1.5 [@sklearn] for "
          "the intent classifier and the cross-checks, pandas for the evaluation, Streamlit 1.39 [@streamlit] for "
          "the application, and FastAPI with React for the optional web app. The team wrote the tokeniser, the "
          "char_wb analyzer, TF-IDF weighting, cosine ranking, explain(), BM25, the Jaccard baseline, all metrics "
          "and the evaluation harness; scikit-learn is used only for the intent models and, in tests, to check "
          "that our TF-IDF scores equal TfidfVectorizer’s. Table {tab:decisions} lists the key decisions."),
    ("table", "decisions", "Key design decisions.",
     [["Decision", "Alternatives considered", "Rationale"]],
     [["Features: char_wb 3–5 n-grams, sublinear TF", "Word unigrams or bigrams, char without word "
       "boundaries, char_wb 2–4, word+char hybrid",
       "Best benchmark paraphrase MRR@10 among the retrievers (0.827), perfect typo Hit@1, robust to three typos; "
       "char_wb 2–4 was better on development paraphrases (0.344 vs 0.299) but 3–5 was frozen at the midterm"],
      ["Index field: question + answer", "Question only",
       "Question-only indexing collapses on paraphrases (development MRR@10 0.106 vs 0.244)"],
      ["Ranking: cosine", "Okapi BM25",
       "Bounded in [0, 1], so one absolute floor fits every query, and exactly decomposable for explain()"],
      ["Intent: word TF-IDF + Logistic Regression, C = 10", "Naive Bayes, k-NN, linear SVM",
       "Best cross-validated accuracy (Table {tab:cv}) and posteriors usable as a gate; LinearSVC has none"],
      ["Abstention: conjunctive dual gate", "None; cosine threshold only",
       "Cosine alone refuses 1/15 benchmark out-of-corpus questions; with the intent gate 15/15"],
      ["Product: three cards, labels, explain()", "One answer; raw scores only",
       "Three cards deliver the right document for 101/105 in-corpus benchmark questions vs 93/105 at top-1"]],
     [2400, 2470, 4200], {"size": 20, "split": True}),

    ("h1", "4  Experimental Methodology and Results"),
    ("h2", "4.1  Experimental Setup"),
    ("p", "**Data.** All experiments use the 112-document course corpus [@kit] and two query sets. The benchmark "
          "data/queries_test.csv has 120 queries: 35 *normal* (verbatim FAQ questions), 35 *paraphrase*, 35 "
          "*typo* (one adjacent-letter swap) and 15 *out-of-corpus* (OOC). It was inspected during development, "
          "and its 35 normal queries also appear in the intent training texts, so benchmark numbers are "
          "optimistic. The development split in experiments/dev/ has 146 queries: 49 normal and 49 typo queries "
          "generated from the 49 FAQs that no benchmark query targets (typo seed 42000 + *i*), and 28 "
          "paraphrases and 20 OOC questions written by hand by the team. The product configuration was "
          "not re-tuned on it, so it is our closest estimate for fresh questions."),
    ("p", "**Protocol and environment.** The pipeline is deterministic: reruns give identical scores, and every "
          "committed result matched when we re-ran the experiments for this report, so we report single values. "
          "Intent models are also evaluated by stratified 5-fold cross-validation over the 112 documents (seed "
          "42) and by leave-one-document-out (LODO), which removes the target document from training. Hardware "
          "and software: AMD Ryzen 5 5600H laptop CPU, 20 GB RAM, Windows 11, Python 3.11.16, NumPy 1.26.4, "
          "scikit-learn 1.5.2, pandas 2.2.3, Streamlit 1.39.0. Appendix A gives the command for every table."),
    ("h2", "4.2  Evaluation Metrics"),
    ("p", "For an in-corpus query *i* whose expected document is at rank *r*_{i}, the mean reciprocal rank is"),
    ("eq", "mrr", EQ_MRR),
    ("p", "We report MRR@10 (1/*r*_{i} set to 0 when *r*_{i} > 10) unless *full MRR* is stated. Hit@*k* is the "
          "share of queries with *r*_{i} ≤ *k* (P@1 equals Hit@1, as each query has one correct document), and "
          "intent accuracy the share of in-corpus queries with the right intent. *OOC refused* counts OOC "
          "queries with *a*(*q*) = ∅, and the *false-abstention rate* is the share of in-corpus queries refused. "
          "A decision is end-to-end (E2E) correct when an in-corpus query is answered with the right document "
          "first or an OOC query is refused; *balanced E2E* averages E2E accuracy over the four query types. "
          "Latency is the wall-clock time per query after start-up."),
    ("h2", "4.3  Results"),
    ("p", "Table {tab:main} compares the final system with the baselines and the midterm version on both query "
          "sets."),
    ("table", "main", "Comparison with the baselines and the Midterm version. The pipeline is deterministic, so "
                      "each value is a single run (reruns are identical). Best values in bold.",
     [[("Method", 1, 2), ("Benchmark (120 queries)", 4, 1), ("Development split (146 queries)", 3, 1)],
      [None, "Para. MRR@10", "Typo Hit@1", "OOC refused", "Bal. E2E", "Para. MRR@10", "OOC refused",
       "Bal. E2E"]],
     [["Baseline: Jaccard + majority intent, no gate", "0.680", "0.886", "0/15", "0.614", "0.247", "2/20",
       "0.565"],
      ["Word TF-IDF + cosine, 1-NN intent, no gate", "0.743", "0.943", "0/15", "0.643", "0.244", "2/20",
       "0.545"],
      ["BM25 (own code), 1-NN intent, no gate", "0.717", "0.943", "0/15", "0.636", "0.270", "2/20", "0.570"],
      ["Midterm: char_wb + LR + dual gate", "**0.827**", "**1.000**", "**15/15**", "**0.914**", "not run",
       "not run", "not run"],
      ["Final: same core + zero-score guard", "**0.827**", "**1.000**", "**15/15**", "**0.914**", "**0.320**",
       "**12/20**", "**0.659**"]],
     [2049, 1003, 1003, 1003, 1003, 1003, 1003, 1003], {"size": 19, "center_from": 1}),
    ("p", "Sources: test/frozen_compare.csv, dev/ablation_E0, E1, E7_compare.csv and final-dev/summary.csv under "
          "experiments/results/.", {"style": "Caption"}),
    ("p", "**Benchmark.** The final system raises balanced E2E from 0.614 (Jaccard) and 0.643 (word TF-IDF) to "
          "0.914 through two effects. The char_wb retriever lifts paraphrase MRR@10 from 0.743 to 0.827 and typo "
          "Hit@1 from 0.943 to 1.000; without any gate it already reaches 0.679. The gate refuses all 15 OOC "
          "queries at the cost of two false abstentions, for 108/120 correct decisions, a full MRR of 0.943, "
          "Hit@3 of 0.981 and 97.1% intent accuracy (102/105). The gate ablation shows which gate matters: no "
          "gate gives 95/120 correct with 0/15 OOC refused, the cosine floor alone 96/120 with 1/15, and the "
          "intent gate alone or both gates 108/120 with 15/15 (midterm-sample/ablation.csv)."),
    ("p", "**Development split.** Normal and typo queries stay at Hit@1 = 1.000, but the 28 hand-written "
          "paraphrases reach only MRR@10 0.320 (Hit@1 5/28, Hit@3 12/28), and the gate refuses 15 of them, so "
          "only one is answered with the right document first. OOC refusal drops from 15/15 to 12/20 and the "
          "false-abstention rate rises from 1.9% to 11.9% (15/126). Balanced E2E falls to 0.659, still above "
          "every baseline (0.545–0.570), mostly through the 12 correct refusals; again the intent gate does the "
          "refusing (the cosine floor alone refuses 3/20)."),
    ("p", "**Intent models.** Logistic Regression with TF-IDF is the best of nine cross-validated classifiers "
          "(Table {tab:cv}), but its lead over the linear SVM (0.009) is far inside one standard deviation "
          "(0.074), so the choice rests on its posteriors, which the gate needs. Training overlap inflates intent "
          "accuracy: on the development split, word TF-IDF Logistic Regression scores 0.881 with every document "
          "in training but 0.651 under LODO, and 1-NN drops from 0.889 to 0.571 (dev/ablation_E5_compare.csv)."),
    ("table", "cv", "Intent classification, stratified 5-fold cross-validation over the 112 documents (mean ± "
                    "std over folds; experiments/intent_cv.py). Best values in bold.",
     [["Model", "Accuracy", "Macro-F1"]],
     [["Majority class", "0.134 ± 0.003", "0.034 ± 0.001"],
      ["k-NN, k = 1 / k = 5", "0.769 ± 0.073 / 0.814 ± 0.101", "0.741 ± 0.102 / 0.793 ± 0.123"],
      ["Multinomial Naive Bayes, BoW / TF-IDF", "0.804 ± 0.071 / 0.831 ± 0.084", "0.787 ± 0.091 / 0.826 ± 0.097"],
      ["Logistic Regression, BoW", "0.823 ± 0.060", "0.807 ± 0.067"],
      ["Logistic Regression, TF-IDF (product)", "**0.876 ± 0.074**", "**0.872 ± 0.085**"],
      ["Linear SVM, BoW / TF-IDF", "0.867 ± 0.072 / 0.867 ± 0.083", "0.860 ± 0.084 / 0.861 ± 0.094"]],
     [3070, 3000, 3000], {"center_from": 1, "size": 20}),
    ("p", "**Typo robustness and latency.** With *k* = 0 to 3 adjacent swaps injected into the 49 normal "
          "development queries (experiments/noise_curve.py), Hit@1 of word TF-IDF and Jaccard falls to 0.837 at "
          "*k* = 3, while char_wb stays at 1.000 for *k* = 0, 1 and 3 and at 0.959 for *k* = 2 (one query, since "
          "each level draws new random typos). After start-up the median latency per development query is "
          "0.85 ms, and the 840-word stress query of Section 5 takes 3.2 ms."),
    ("h2", "4.4  Discussion"),
    ("p", "**Why the method beats the baseline.** Character n-grams keep most features of a misspelled word, so "
          "typos cost almost nothing, and sub-word overlap gives partial credit to variants such as *register* "
          "and *registration*; sublinear TF stops a word repeated in a long answer from dominating. The gain on "
          "development paraphrases is small (0.244 → 0.320) because heavy rewordings (“Which physical "
          "credentials must test-takers present upon entering the evaluation hall?”) share almost no "
          "character sequences with their target FAQ."),
    ("p", "**Is the difference meaningful?** One of the 35 benchmark paraphrases moves Hit@1 by 0.029, so the "
          "0.714 against 0.657 Hit@1 gap between char_wb and word TF-IDF is two queries. It agrees in direction "
          "with the development split, but we claim no statistical significance. The refusal effect is larger "
          "and consistent: on both sets the intent gate, not the cosine floor, does the refusing."),
    ("p", "**Sensitivity.** Table {tab:sweep} varies *τ*_{p} with the cosine floor at 0.15. On the benchmark 0.34 "
          "is exactly tuned: the most confident benchmark OOC query scores 0.332, and benchmark E2E peaks there. "
          "On the development split the best value is 0.55 (119/146), which refuses all 20 OOC questions and 25 "
          "in-corpus ones. The threshold therefore does not transfer; it was chosen with the benchmark in view, "
          "which is the main reason the midterm numbers overstate the system. Because a refusal is cheap for a "
          "student and a wrong answer is costly, a higher threshold chosen on held-out data would be defensible; "
          "we keep 0.34 so that the reported results stay reproducible and the development split stays untuned."),
    ("table", "sweep", "Sensitivity of the intent gate *τ*_{p} with the cosine floor fixed at 0.15 "
                       "(intent_gate_sweep.csv from scripts/evaluate.py). The product uses 0.34.",
     [[("*τ*_{p}", 1, 2), ("Benchmark (105 in-corpus, 15 OOC)", 3, 1), ("Development (126 in-corpus, 20 OOC)", 3, 1)],
      [None, "OOC refused", "False abst.", "E2E correct", "OOC refused", "False abst.", "E2E correct"]],
     [["0.00", "1", "0", "96", "3", "2", "106"],
      ["0.30", "12", "1", "106", "9", "13", "108"],
      ["**0.34**", "15", "2", "**108**", "12", "15", "111"],
      ["0.40", "15", "10", "104", "16", "18", "115"],
      ["0.45", "15", "12", "102", "18", "22", "117"],
      ["0.50", "15", "16", "98", "19", "23", "118"],
      ["0.55", "15", "23", "93", "20", "25", "**119**"],
      ["0.60", "15", "26", "90", "20", "27", "117"]],
     [1170, 1300, 1300, 1300, 1330, 1335, 1335], {"center_from": 0, "size": 21}),

    ("h1", "5  Scenario Evaluation and Failure Analysis"),
    ("h2", "5.1  Scenario Results"),
    ("p", "We scripted 14 scenarios covering the four query types of the assignment plus edge, stress and "
          "out-of-scope inputs (experiments/scenarios.py, checked by tests/test_scenarios.py). Each calls the "
          "product functions with the product thresholds, and its expected behaviour was fixed before the run. "
          "Table {tab:scen} summarises them: 11 pass, one is partial and two fail."),
    ("table", "scen", "Behaviour of the system on representative scenarios "
                      "(experiments/results/scenarios/scenarios.csv).",
     [["ID", "Scenario", "Observed behaviour", "Outcome"]],
     [["S1", "Typical: “How do I reset my Student Portal password?”",
       "Correct FAQ first, cosine 0.539; technical_support 88%", "Pass"],
      ["S2", "One typo: “Sutdent”", "Same ranking, cosine 0.528", "Pass"],
      ["S3", "Three typos: “Hwo do I rseet my Sutdent Portal pasword?”",
       "Correct FAQ first, cosine 0.344, intent 63%", "Pass"],
      ["S4", "Light paraphrase: “I forgot my Student Portal password - how do I reset it?”",
       "Correct FAQ first, cosine 0.514", "Pass"],
      ["S5", "Synonym paraphrase: “Two of my finals overlap on the same day - who do I tell?”",
       "Class-overlap FAQ first; correct exam-conflict FAQ second", "Partial"],
      ["S6", "Topic boundary: “Where do I go to see my current classes and times?”",
       "Correct FAQ first (0.297) but intent 25% < 34%: refused", "Fail"],
      ["S7", "Two questions in one (tuition due date and exam week)",
       "Tuition FAQ first, exam FAQs second and third", "Pass"],
      ["S8", "Out of scope with campus words: kayak rental", "Refused: cosine 0.394 passed, intent 29% failed",
       "Pass"],
      ["S9", "Out of scope with university words: dining halls at Thanksgiving",
       "Answered with a class-schedule FAQ: cosine 0.441, intent 35%", "Fail"],
      ["S10", "Out of scope, no campus words: “What is the capital of Australia?”",
       "Refused: cosine 0.140 < 0.15", "Pass"],
      ["S11", "Vietnamese input", "Refused (cosine 0.089); English-only notice shown", "Pass"],
      ["S12", "Empty input (spaces only)", "Refused without an error", "Pass"],
      ["S13", "Punctuation only: “???!!!”", "Refused: no known feature, cosine 0", "Pass"],
      ["S14", "Stress: an 840-word query", "Tuition FAQ first, answered in 3.2 ms", "Pass"]],
     [680, 3800, 3620, 970], {"size": 20, "split": True}),
    ("h2", "5.2  Failure Analysis"),
    ("p", "**F1 — synonym mismatch (S5 and benchmark q_056).** “Two of my finals overlap on the same day - "
          "who do I tell?” expects faq_exam_02 (“Two of my final exams are scheduled at the same "
          "time”) but returns faq_class_schedule_02 (“How do I check if two of my classes overlap in "
          "time?”), 0.268 against 0.189. The explain() table in Figure {fig:flow2}(a) shows why: the largest "
          "contributions are n-grams of *overlap* (erl, erla, erlap, overl, …, 0.0169 each), a word in the "
          "class FAQ but not in the exam FAQ, which says *conflict*. The mirror case q_056 (“How can I tell "
          "if my class times conflict with each other?”) ranks the class FAQ 11th because the n-grams of "
          "*conflict* carry a high idf in an exam-conflict notice. Root cause: the algorithm is lexical, and the "
          "intent (class_schedule, 37%) is wrong too. Fix: a small domain synonym table applied to the query "
          "(overlap ↔ conflict, full ↔ no open seats) and separate scores for the stored question and the answer."),
    ("p", "**F2 — false abstention (S6, benchmark q_064).** The correct document is ranked first (0.297), but "
          "the posterior is flat (class_schedule 0.253, technical_support 0.170, graduation 0.153), so its "
          "maximum falls below *τ*_{p}. Root cause: the assumption that intent confidence measures relevance; the posteriors were "
          "never calibrated [@guo]. Fix: accept when the top document’s intent is among the two most likely "
          "intents, or calibrate the posteriors on held-out data."),
    ("p", "**F3 — out-of-corpus leaks (S9 and 7 other development questions).** Eight of the 20 development OOC "
          "questions pass both gates, e.g. “Where can students submit complaints regarding vending machine "
          "malfunctions on campus?” (cosine 0.215, intent 0.538 for student_services). Root cause: data and "
          "threshold. The benchmark has only 15 OOC queries, *τ*_{p} sits just above their maximum, and "
          "questions about complaints, permits or holidays resemble real student-services and schedule "
          "documents. Fix: choose *τ*_{p} on a held-out OOC set (Table {tab:sweep} points to 0.45–0.55) or train "
          "an explicit out-of-scope class on negative examples."),
    ("p", "**F4 — heavy paraphrases (development split).** 23 of the 28 development paraphrases do not rank the "
          "target first and 16 rank it below third. Root cause: no notion of meaning beyond shared surface "
          "forms. Fix: synonym lists help only for known pairs; a real fix needs semantic representations such as "
          "word embeddings or latent semantic analysis."),
    ("h2", "5.3  Improvement over the Midterm"),
    ("p", "The AI core has not changed since the midterm: features, intent model and thresholds were frozen when "
          "the team integrated its algorithm study on 2 November 2026, and the only change is a guard that "
          "refuses a query whose best cosine is exactly zero, which matters when the slider sets the floor to 0. "
          "The two ranking fixes proposed at the midterm (a synonym list and separate question and answer "
          "weights) were not implemented, so Table {tab:main} shows identical benchmark numbers. The final phase "
          "changed three other things."),
    ("bullets", [
        "**Evaluation.** The midterm reported only the inspected benchmark. The final evaluation adds the "
        "development-split run, the frozen baseline batch, the noise curve, cross-validation, the gate sweep and "
        "the scenarios. Its effect is a correction, not a gain: OOC refusal on fresh questions is 12/20, not "
        "15/15. Two development queries wrongly labelled out-of-corpus were also fixed.",
        "**Product.** The midterm demo showed the intent badge, cards and a plain refusal. The final application "
        "adds match labels, notice dates, highlighting, a refusal naming the failed gate, explain() tables, "
        "sliders, feedback, a dashboard read from result files, a Vietnamese-input notice and office contacts "
        "taken only from the corpus (an earlier version showed invented rooms and opening hours).",
        "**Engineering.** The core also runs as a FastAPI and React web app in Docker, and continuous "
        "integration runs the 131 tests, builds the front end and smoke-tests the container.",
    ]),

    ("h1", "6  Limitations, Ethics and Conclusion"),
    ("h2", "6.1  Limitations and Future Work"),
    ("p", "The system matches surface forms only, so it cannot relate synonyms (development paraphrase Hit@1 "
          "5/28). The intent threshold was fitted with the benchmark in view and lets 8/20 fresh OOC questions "
          "through, and benchmark figures are upper bounds because the benchmark was inspected and its normal "
          "queries overlap the training data. The data are small and synthetic: one query moves a rate by three "
          "to five points and no real student questions were available. The confidence shown is an "
          "uncalibrated posterior, and the system handles English only, keeps no conversation context and does "
          "not check whether a notice has expired. Next steps: (1) collect a fresh held-out set written by "
          "someone who has not seen the corpus and choose *τ*_{p} on a validation part of it; (2) add a curated "
          "synonym table and question/answer weighting, measured on the development paraphrases; (3) add an "
          "out-of-scope class trained on negative questions and calibrate the classifier."),
    ("h2", "6.2  Ethical Considerations"),
    ("p", "The main risk is over-trust: a well-formatted card looks authoritative even when it is the wrong "
          "document, which happens silently for 10 of the 105 in-corpus benchmark questions. The application "
          "mitigates this by always showing the source and date, a match label and up to three alternatives, by "
          "refusing rather than guessing, and by stating on every page that the corpus is synthetic and not an "
          "official HANU service; every score is explainable and every refusal names its gate. The system runs offline and sends no query to an external service; the optional "
          "feedback buttons store the query, the top document and a timestamp in a local, git-ignored file, "
          "without user identity. Students who misspell or write non-native English could be served worse; "
          "character n-grams reduce the typo effect and Vietnamese input gets a clear notice, but we did not test "
          "with real non-native writers."),
    ("h2", "6.3  Conclusion"),
    ("p", "We built an offline campus FAQ assistant that answers only from 112 documents and refuses otherwise, "
          "using hand-written char_wb TF-IDF retrieval, a Logistic Regression intent classifier and a dual-gate "
          "abstention rule, packaged as an explainable Streamlit application. On the course benchmark it reaches "
          "a full MRR of 0.943 and 108/120 correct decisions with all 15 out-of-corpus questions refused, well "
          "above a Jaccard baseline (balanced E2E 0.914 against 0.614). On fresh team-written questions it keeps "
          "perfect normal and typo retrieval but refuses only 12/20 out-of-corpus questions and rarely finds "
          "heavily reworded ones. The main lesson concerns evaluation more than algorithms: a threshold chosen "
          "while looking at the test set looks perfect on that set, and only an untouched split shows how the "
          "system will behave for real students."),
]

REFERENCES = {
    "ji": "Z. Ji *et al.*, “Survey of hallucination in natural language generation,” *ACM Comput. "
          "Surv.*, vol. 55, no. 12, Art. no. 248, 2023, doi: 10.1145/3571730.",
    "kit": "T. V. Nguyen, “AIN course projects (Project 12: Campus Notice & FAQ Assistant),” GitHub "
           "repository. [Online]. Available: https://github.com/vinhnt21/ain-projects (accessed Nov. 25, 2026).",
    "cs50": "D. J. Malan and B. Yu, “CS50’s Introduction to Artificial Intelligence with Python,” "
            "Harvard University. [Online]. Available: https://cs50.harvard.edu/ai/ (accessed Nov. 25, 2026).",
    "salton": "G. Salton, A. Wong, and C. S. Yang, “A vector space model for automatic indexing,” "
              "*Commun. ACM*, vol. 18, no. 11, pp. 613–620, 1975.",
    "manning": "C. D. Manning, P. Raghavan, and H. Schütze, *Introduction to Information Retrieval*. Cambridge, "
               "U.K.: Cambridge Univ. Press, 2008.",
    "aima": "S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: "
            "Pearson, 2020.",
    "chow": "C. K. Chow, “On optimum recognition error and reject tradeoff,” *IEEE Trans. Inf. "
            "Theory*, vol. IT-16, no. 1, pp. 41–46, 1970.",
    "bm25": "S. Robertson and H. Zaragoza, “The probabilistic relevance framework: BM25 and beyond,” "
            "*Found. Trends Inf. Retr.*, vol. 3, no. 4, pp. 333–389, 2009.",
    "bojanowski": "P. Bojanowski, E. Grave, A. Joulin, and T. Mikolov, “Enriching word vectors with "
                  "subword information,” *Trans. Assoc. Comput. Linguist.*, vol. 5, pp. 135–146, 2017.",
    "sakata": "W. Sakata, T. Shibata, R. Tanaka, and S. Kurohashi, “FAQ retrieval using query-question "
              "similarity and BERT-based query-answer relevance,” in *Proc. 42nd Int. ACM SIGIR Conf. Res. "
              "Develop. Inf. Retr.*, Paris, France, 2019, pp. 1113–1116.",
    "dpr": "V. Karpukhin *et al.*, “Dense passage retrieval for open-domain question answering,” in "
           "*Proc. Conf. Empirical Methods Natural Lang. Process. (EMNLP)*, 2020, pp. 6769–6781.",
    "geifman": "Y. Geifman and R. El-Yaniv, “Selective classification for deep neural networks,” in "
               "*Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, Long Beach, CA, USA, 2017, pp. 4878–4887.",
    "fastapi": "S. Ramírez, “FastAPI.” [Online]. Available: https://fastapi.tiangolo.com (accessed "
               "Nov. 25, 2026).",
    "numpy": "C. R. Harris *et al.*, “Array programming with NumPy,” *Nature*, vol. 585, no. 7825, "
             "pp. 357–362, 2020.",
    "sklearn": "F. Pedregosa *et al.*, “Scikit-learn: Machine learning in Python,” *J. Mach. Learn. "
               "Res.*, vol. 12, pp. 2825–2830, 2011.",
    "streamlit": "Snowflake Inc., “Streamlit documentation.” [Online]. Available: "
                 "https://docs.streamlit.io (accessed Nov. 25, 2026).",
    "guo": "C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, “On calibration of modern neural "
           "networks,” in *Proc. 34th Int. Conf. Mach. Learn. (ICML)*, Sydney, NSW, Australia, 2017, "
           "pp. 1321–1330.",
}

REPRO_LINES = [
    "python3.11 -m venv .venv                     # Windows: py -3.11 -m venv .venv",
    ".venv/bin/python -m pip install -r requirements.txt",
    r"# On Windows replace .venv/bin/python with .venv\Scripts\python.exe",
    ".venv/bin/python -m pytest -q                # 131 passed, 2 deselected",
    ".venv/bin/python scripts/evaluate.py         # Tables 3 and 5 (benchmark)",
    ".venv/bin/python scripts/evaluate.py --split dev      # Tables 3 and 5 (dev)",
    ".venv/bin/python experiments/run_ablation.py --split test --final",
    "    # Table 3 benchmark baselines; once experiments/results/test/LOCK",
    "    # exists, a repeat run needs --rerun-reason \"<why>\"",
    ".venv/bin/python experiments/run_ablation.py --split dev --group E0",
    "    # likewise E1, E2, E3, E4, E5, E7: development baselines (Tables 2, 3)",
    ".venv/bin/python experiments/intent_cv.py    # Table 4",
    ".venv/bin/python experiments/noise_curve.py  # typo curve, Section 4.3",
    ".venv/bin/python experiments/scenarios.py    # Table 6",
    ".venv/bin/python experiments/business_metrics.py  # top-3 delivery 101/105",
    ".venv/bin/python -m streamlit run starter/app.py  # the application",
    "# Repository: https://github.com/VinhDat267/ain_project",
]

CONTRIBUTIONS = [
    ("2301040198", "Nguyễn Đạt Vinh*", "Leader and reviewer; evaluation harness, metrics and baselines; BM25; "
                                        "threshold and gate experiments; integration of the midterm core; "
                                        "midterm slides; final review fixes, web app packaging and CI; report", "[ ]"),
    ("2301040004", "Lương Việt Anh", "Retrieval engine (TF-IDF, char_wb, cosine, explain()), preprocessing and "
                                      "core wiring; hand calculation; development paraphrase and OOC queries; "
                                      "noise curve, cross-validation, UI redesign, business metrics; IEEE draft",
     "[ ]"),
    ("2401040080", "Nguyễn Ánh Dương", "[Main tasks — to be confirmed by the group]", "[ ]"),
]

AI_TOOLS = [
    ("Claude Code (Anthropic, Claude Opus models)",
     "Pair programming for evaluation scripts, BM25, tests and the web app; code review; drafting and checking "
     "this report. Every number was regenerated from the committed scripts and checked by the team.",
     "experiments/, scripts/, webapp/, tests/, report/"),
    ("[Tools used by other members — name and version]", "[What they were used for]", "[Where]"),
]
