# INTERFACE — Project 12 · Campus Notice & FAQ Assistant

> Đây là hợp đồng kỹ thuật giữa 3 thành viên. Code đúng chữ ký hàm và định dạng dữ liệu ở đây thì cả nhóm làm song song được mà không phải chờ nhau.
>
> **Muốn đổi interface:** mở PR sửa file này trước, cả 3 người đồng ý rồi mới sửa code.
>
> Phiên bản **v2** (sau rà soát) — 01/10/2026 · chốt qua nhóm chat trước **T7 03/10/2026 10:00** (việc N02, không họp). Mã việc (V01, A04, D10…) tham chiếu tới [PLAN.md](PLAN.md).

---

## 1. Nguyên tắc chung

- **Môi trường:** Python 3.11, venv `.venv` ở gốc repo. Chỉ dùng thư viện có trong `requirements.txt` (numpy, pandas, matplotlib, scikit-learn, streamlit, pytest).
- **Không gọi LLM hay API hosted** ở bất kỳ đâu trong code chạy. Vi phạm là 0 điểm.
- **Retrieval tự viết:** TF-IDF và cosine viết bằng Python/numpy. scikit-learn chỉ dùng để *đối chiếu* kết quả trong test hoặc notebook.
- **Intent được phép dùng scikit-learn.**
- **Import scikit-learn bên trong hàm hoặc method**, không đặt ở đầu file trong `starter/`. Lý do: starter yêu cầu sanity test offline chạy được khi chưa cài sklearn.
- **Quy ước import:**
  - Entry point (app, script, test) thêm `PROJECT_ROOT` vào `sys.path`, rồi import qua package `starter`, ví dụ `from starter.retrieval import Retriever`.
  - Bên trong `starter/` dùng import tương đối, ví dụ `from .preprocess import tokenize`.
  - Riêng `student_core.py` import tuyệt đối `starter.…` **bên trong hàm**, vì sanity test của thầy nạp file này theo đường dẫn.
- **Tất định:** cùng input phải cho cùng output. Chỗ nào bắt buộc có ngẫu nhiên thì cố định `random_state=42`.
- **Đường dẫn file** luôn tính từ `PROJECT_ROOT = Path(__file__).resolve().parent.parent`, không phụ thuộc thư mục đang đứng.
- **Tập test:** Việt Anh và Dương **không mở `data/queries_test.csv` trước 15/10**. Script được phép đọc *cột `expected_doc_id`* của file này để loại tài liệu đích khỏi tập dev (mục 8).

---

## 2. Cấu trúc thư mục và người phụ trách

```text
ain_project/  (gốc repo)
├── README.md, ASSIGNMENT.md             # giới thiệu repo · đề bài gốc của thầy
├── .github/workflows/project-12-tests.yml  # CI: tự chạy pytest cho mọi PR (có sẵn)
├── PLAN.md, INTERFACE.md                # Vinh (sửa INTERFACE cần cả nhóm duyệt)
├── pytest.ini                           # có sẵn: bỏ qua 2 test stub (mục 4)
├── data/                                # dữ liệu gốc của thầy — KHÔNG sửa
├── starter/
│   ├── student_core.py                  # API công khai — chung (wiring A05)
│   ├── preprocess.py, retrieval.py      # Việt Anh
│   ├── bm25.py                          # Vinh (BM25 để so sánh, E7)
│   ├── intent.py                        # Dương
│   └── app.py                           # Dương (app demo D10)
├── experiments/
│   ├── make_auto_dev.py                 # Vinh: sinh queries_dev_auto.csv (V05)
│   ├── dev/queries_dev_auto.csv         # tự sinh: 49 normal + 49 typo
│   ├── dev/queries_dev_vietanh.csv      # Việt Anh viết tay: 14 paraphrase + 10 ngoài kho
│   ├── dev/queries_dev_duong.csv        # Dương viết tay: 14 paraphrase + 10 ngoài kho
│   ├── metrics.py, evaluate.py          # Vinh
│   ├── baselines.py                     # Vinh (Jaccard, majority, k-NN)
│   ├── run_ablation.py                  # Vinh (các nhóm thí nghiệm, batch tập test)
│   ├── sweep_threshold.py               # Vinh (E6)
│   ├── noise_curve.py                   # Việt Anh (E3b)
│   ├── intent_cv.py                     # Dương (E5b)
│   └── results/                         # output do script sinh ra — commit lên repo
├── notes/                               # tính tay, phân tích lỗi, so sánh lý thuyết, ngân hàng câu hỏi
├── notebooks/                           # thống kê corpus, ma trận nhầm lẫn (Dương)
└── tests/
    ├── test_project_12_sanity.py        # của thầy — KHÔNG sửa
    ├── test_retrieval.py                # Việt Anh
    ├── test_intent.py                   # Dương
    └── test_metrics.py                  # Vinh
```

Mỗi người chỉ sửa file của mình. File chung (`student_core.py`, `INTERFACE.md`, `run_ablation.py` phần nhóm thí nghiệm của người khác) sửa qua PR có người duyệt.

---

## 3. Kiểu dữ liệu chung

`Document` là dict do `load_documents()` trả về. Hàm này đã có sẵn, không phải viết.

| Khoá | Ví dụ | Ghi chú |
|---|---|---|
| `id` | `faq_exam_03` | duy nhất |
| `intent` | `exam` | 1 trong 7 intent |
| `question` | `Can I reschedule …?` | với notice là `title` |
| `answer` | `Contact …` | với notice là `body` |
| `text` | `question + " " + answer` | |
| `source` | `faq.json` / `notices.json` | dùng để ghi nguồn trên UI |

`Ranked = list[tuple[Document, float]]`, sắp xếp theo score giảm dần.

7 intent theo đúng thứ tự trong `data/intents.csv`: `course_registration`, `exam`, `tuition`, `class_schedule`, `student_services`, `graduation`, `technical_support`.

---

## 4. API công khai — `starter/student_core.py` (KHÔNG đổi chữ ký)

| Hàm | Trả về | Ràng buộc |
|---|---|---|
| `load_documents()` | `list[Document]` | có sẵn — không sửa |
| `classify_intent(query: str)` | `tuple[str, float]` | intent ∈ 7 intent; confidence ∈ [0, 1]; không raise với query rỗng |
| `retrieve(query: str, top_k: int = 3)` | `Ranked` | tối đa `top_k` phần tử; **`[]` khi từ chối trả lời** |

**Wiring** (A05, **T4 07/10 12:00**, Việt Anh làm, Vinh duyệt):

```python
DEFAULT_RETRIEVAL_CONFIG = RetrievalConfig(...)  # cấu hình đóng băng — chỉ cập nhật 1 lần ở V17 (14/10)
DEFAULT_INTENT_CONFIG = IntentConfig(...)        # model chỉ được là "nb" hoặc "logreg" (mục 6)

def retrieve(query, top_k=3):
    return _get_retriever().search(query, top_k)   # Retriever dựng 1 lần (lazy), dùng lại

def classify_intent(query):
    return _get_classifier().predict(query)        # fit 1 lần trên build_training_data(load_documents(), ...)
```

- **Phương án dự phòng** khi `intent.py` chưa xong: lấy `intent` của tài liệu top-1 trong `rank(query)`, confidence là score top-1.
- **2 test stub của thầy** (`test_classify_intent_is_not_implemented`, `test_retrieve_is_not_implemented`) kiểm tra rằng core *vẫn còn trống*, nên sẽ fail khi core đã cài xong. Nhóm **không sửa file test của thầy**; thay vào đó `pytest.ini` bỏ qua đúng 2 test này. Kết quả chuẩn khi chạy `pytest`: **`15 passed, 2 deselected`** cộng các test của nhóm.

---

## 5. Retrieval — `starter/preprocess.py`, `starter/retrieval.py` (Việt Anh)

### 5.1 `preprocess.py`

```python
STOPWORDS: frozenset[str]
def tokenize(text: str, remove_stopwords: bool = False) -> list[str]: ...
```

- Chuyển về chữ thường, tách token theo chữ cái và chữ số.
- Chuỗi rỗng hoặc toàn khoảng trắng trả về `[]`. **Không bao giờ raise.**

### 5.2 `RetrievalConfig`

```python
@dataclass(frozen=True)
class RetrievalConfig:
    analyzer: Literal["word", "char", "hybrid"] = "word"
    index_field: Literal["question", "text"] = "text"
    word_ngram_range: tuple[int, int] = (1, 1)
    char_ngram_range: tuple[int, int] = (3, 5)
    remove_stopwords: bool = True
    sublinear_tf: bool = False
    hybrid_alpha: float = 0.5
    threshold: float = 0.0
```

| Trường | Ý nghĩa |
|---|---|
| `analyzer` | `word`: TF-IDF theo từ · `char`: theo n-gram ký tự (trong ranh giới từ) · `hybrid`: kết hợp hai cách |
| `index_field` | lập chỉ mục chỉ `question`, hay `text` (câu hỏi kèm câu trả lời) |
| `word_ngram_range`, `char_ngram_range` | độ dài n-gram nhỏ nhất và lớn nhất |
| `remove_stopwords` | áp cho `word` |
| `sublinear_tf` | dùng `1 + log(tf)` thay cho `tf` |
| `hybrid_alpha` | `score = α·score_word + (1−α)·score_char` |
| `threshold` | từ chối khi score top-1 `< threshold` |

### 5.3 `Retriever`

```python
class Retriever:
    def __init__(self, documents: list[Document], config: RetrievalConfig = RetrievalConfig()) -> None: ...
    def rank(self, query: str) -> Ranked: ...
    def search(self, query: str, top_k: int = 3) -> Ranked: ...
    def explain(self, query: str, doc_id: str, top_n: int = 5) -> list[tuple[str, float]]: ...  # A11
```

- **`rank(query)`** trả về **toàn bộ** tài liệu kèm cosine thô, **không áp ngưỡng**. Script đánh giá dùng hàm này để quét ngưỡng mà không phải chạy lại retrieval.
- **`search(query, top_k)`** trả về `rank(query)[:top_k]`, **nhưng trả `[]`** khi rơi vào một trong ba trường hợp:
  - `top_k <= 0`;
  - score top-1 bằng `0`, tức query không có từ nào nằm trong bộ từ vựng;
  - score top-1 nhỏ hơn `config.threshold`.
- **`explain(query, doc_id, top_n)`** trả về các đặc trưng (từ hoặc n-gram ký tự) đóng góp nhiều nhất vào score, dạng `(feature, contribution)`, sắp giảm dần.
  - Với vector đã chuẩn hoá L2, cosine bằng `Σ_t q̂_t · d̂_t`. Vì vậy `contribution(t) = q̂_t · d̂_t`, và tổng contribution của mọi đặc trưng đúng bằng score.
  - Với `hybrid`, nhân contribution của mỗi phần với trọng số tương ứng (α hoặc 1−α).
- **Quy tắc chung:**
  - score ∈ [0, 1];
  - khi bằng điểm, sắp theo `id` tăng dần;
  - chỉ mục dựng **một lần** trong `__init__`;
  - mỗi truy vấn chạy dưới 50 ms.

### 5.4 Tiêu chí "xong"

**A04, mở PR trước T3 06/10 12:00 (PR nháp từ T2 05/10)**

- [ ] `analyzer="word"` chạy được.
- [ ] Score khớp `sklearn.feature_extraction.text.TfidfVectorizer` cấu hình tương đương, sai số dưới `1e-6`. sklearn mặc định dùng `idf(t) = ln((1+N)/(1+df)) + 1`; muốn so sánh thì dùng cùng công thức. Cấu hình đối chiếu đã kiểm chứng chạy được: `TfidfVectorizer(tokenizer=..., lowercase=False, token_pattern=None, smooth_idf=True, norm="l2")`.
- [ ] Có `tests/test_retrieval.py` kiểm tra: thứ tự giảm dần, score ∈ [0, 1], query rỗng ra `[]`, `top_k` đúng, tất định.

**A06–A07 (T6 09/10 và CN 11/10):** các tuỳ chọn theo từ, `char`, `hybrid`, `sublinear_tf` chạy được, có test.

**A11 (T5 15/10):** `explain()` chạy được, có test kiểm tra tổng contribution bằng score.

### 5.5 BM25 — `starter/bm25.py` (Vinh, V13, chỉ để so sánh)

```python
class BM25Retriever:
    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75,
                 index_field: Literal["question", "text"] = "text", threshold: float = 0.0) -> None: ...
    def rank(self, query: str) -> Ranked: ...
    def search(self, query: str, top_k: int = 3) -> Ranked: ...
```

- **Tự viết**, dùng `tokenize(..., remove_stopwords=True)` của `preprocess.py`; không dùng thư viện BM25.
- Công thức: `score(q, d) = Σ_{t ∈ q} idf(t) · tf(t,d)·(k1+1) / (tf(t,d) + k1·(1 − b + b·|d|/avgdl))`, với `idf(t) = ln((N − df(t) + 0.5)/(df(t) + 0.5) + 1)` (luôn không âm).
- `rank` và `search` theo đúng quy tắc ở mục 5.3, **trừ một điểm: score BM25 không nằm trong [0, 1]**. Vì vậy BM25 chỉ được so sánh bằng chỉ số xếp hạng (MRR, Hit@k, P@k); sản phẩm vẫn dùng cosine và ngưỡng như đề bài yêu cầu.
- Test: thứ tự giảm dần, tất định, query rỗng ra `[]`, và một ví dụ nhỏ tính tay khớp với code.

---

## 6. Intent — `starter/intent.py` (Dương)

```python
INTENTS: tuple[str, ...]  # 7 intent, đúng thứ tự intents.csv

@dataclass(frozen=True)
class IntentConfig:
    model: Literal["nb", "logreg", "svm"] = "nb"
    features: Literal["bow", "tfidf"] = "bow"
    ngram_range: tuple[int, int] = (1, 1)
    nb_alpha: float = 1.0                # Laplace smoothing cho MultinomialNB
    lr_C: float = 1.0                    # độ mạnh regularization cho LogisticRegression
    svm_C: float = 1.0                   # độ mạnh regularization cho LinearSVC
    include_descriptions: bool = False   # thêm 7 dòng mô tả trong data/intents.csv vào dữ liệu train

def build_training_data(
    documents: list[Document],
    exclude_ids: Collection[str] = (),
    include_descriptions: bool = False,
) -> tuple[list[str], list[str]]: ...

class IntentClassifier:
    def __init__(self, config: IntentConfig = IntentConfig()) -> None: ...
    def fit(self, texts: list[str], labels: list[str]) -> "IntentClassifier": ...
    def predict_proba(self, query: str) -> dict[str, float]: ...
    def predict(self, query: str) -> tuple[str, float]: ...
```

- **`build_training_data`** tạo `(texts, labels)` từ các tài liệu, dùng `doc["text"]` làm text và `doc["intent"]` làm nhãn.
  - **Bỏ qua các tài liệu có `id` nằm trong `exclude_ids`**, phục vụ đánh giá không rò rỉ (LODO, mục 7.2).
  - Khi `include_descriptions=True`, thêm 7 dòng `(description, intent)` đọc từ `data/intents.csv`. Đề bài viết bộ phân loại "trained on `data/intents.csv` and the labeled documents".
- **`fit`** trả về `self`. Gọi `predict` hoặc `predict_proba` trước khi `fit` thì raise `RuntimeError`.
- **`predict_proba`** trả về dict có **đủ 7 intent**, tổng xác suất bằng 1 (sai số `1e-6`). Lưu ý: `classes_` của sklearn xếp theo bảng chữ cái, khác thứ tự `INTENTS`, nên phải ghép theo `classes_`.
- **`predict`** trả về intent có xác suất cao nhất cùng xác suất đó.
- **Query rỗng không được raise.** Khi đó mô hình trả intent theo xác suất tiên nghiệm (prior). Đã kiểm chứng: `MultinomialNB` trả đúng prior với chuỗi rỗng.
- Import sklearn **bên trong method**. `LogisticRegression` và `LinearSVC` đặt `random_state=42`.
- **Với `model="svm"`:** `LinearSVC` không có xác suất. `predict_proba` trả về **softmax của `decision_function`**, đây chỉ là điểm đã chuẩn hoá, không phải xác suất. Vì vậy **SVM chỉ dùng để so sánh**; mô hình cho sản phẩm (`DEFAULT_INTENT_CONFIG`) chỉ được chọn giữa `nb` và `logreg`.

### 6.1 Tiêu chí "xong"

**D04: PR nháp T2 05/10, PR chính T3 06/10, hạn cứng T5 08/10**

- [ ] `model="nb"`, `features="bow"` chạy được.
- [ ] Có `tests/test_intent.py` kiểm tra:
  - proba có đủ 7 khoá và tổng bằng 1;
  - `predict` khớp argmax của proba;
  - query rỗng không lỗi;
  - `exclude_ids` loại đúng tài liệu;
  - gọi predict trước fit thì raise `RuntimeError`.
- [ ] Intent accuracy trên tập dev **cao hơn baseline đoán lớp phổ biến nhất**.

**D06: CN 11/10**

- [ ] Chạy được `model="logreg"`, `model="svm"`, `features="tfidf"` và `include_descriptions=True`, có test.

---

## 7. Đánh giá — `experiments/`

### 7.1 `metrics.py` (Vinh)

```python
def reciprocal_rank(ranked_ids: Sequence[str], expected_id: str, k: int = 10) -> float: ...
def hit_at_k(ranked_ids: Sequence[str], expected_id: str, k: int) -> int: ...
def precision_at_k(ranked_ids: Sequence[str], expected_id: str, k: int) -> float: ...
```

### 7.2 Định nghĩa chỉ số

"Trong kho" nghĩa là các câu có `type` khác `out_of_corpus`. "OOC" là các câu `out_of_corpus`.

| Chỉ số | Tính trên | Định nghĩa |
|---|---|---|
| **MRR@10** | câu trong kho | trung bình của `1/rank` của tài liệu đúng trong top 10 của `rank()`, **bỏ qua ngưỡng**; ngoài top 10 thì tính 0 |
| **Hit@1, Hit@3** | câu trong kho | 1 nếu tài liệu đúng nằm trong top-k, bỏ qua ngưỡng |
| **P@1, P@3** | câu trong kho | số tài liệu đúng trong top-k chia cho k. Vì mỗi câu chỉ có 1 tài liệu đúng, **P@3 tối đa là 1/3**. Phải ghi rõ điều này khi báo cáo |
| **Intent Acc** | câu trong kho | tỉ lệ `pred_intent == expected_intent` |
| **Intent Acc (LODO)** | câu trong kho | như trên, nhưng với mỗi câu, mô hình được **train lại sau khi bỏ `expected_doc_id`**. Đây là cách đánh giá không rò rỉ, vì câu `normal` chép nguyên văn từ FAQ |
| **OOC rejection** | câu OOC | tỉ lệ câu bị từ chối đúng (`abstained = 1`) |
| **False abstention** | câu trong kho | tỉ lệ câu bị từ chối nhầm |
| **E2E Acc@1** của một loại câu | từng loại | câu trong kho đúng khi *không bị từ chối và Hit@1 = 1*; câu OOC đúng khi *bị từ chối* |
| **Balanced E2E** | tất cả | **trung bình cộng E2E Acc@1 của 4 loại câu** `normal`, `paraphrase`, `typo`, `out_of_corpus`, mỗi loại trọng số ¼. Lấy trung bình theo loại để 98 câu dễ (normal, typo) không lấn át |
| **Latency** | tất cả | ms mỗi truy vấn, gồm cả retrieve và classify |

Mọi bảng kết quả đều tách theo `type`, cộng một dòng tổng. **Ghi kèm số câu** (ví dụ `31/35`), không chỉ ghi phần trăm.

### 7.3 `per_query.csv`: mỗi dòng là một câu hỏi

`query_id, type, query, expected_doc_id, expected_intent, top_ids, top1_score, top2_score, rank, rr, hit1, hit3, p1, p3, abstained, pred_intent, intent_conf, intent_correct, latency_ms`

- `top_ids`: 10 id đầu của `rank()`, ngăn cách bằng `|`.
- `rank`: vị trí tính từ 1 của tài liệu đúng trong toàn bộ thứ hạng; để trống với câu OOC.
- `intent_correct`: để trống với câu OOC.

### 7.4 Output, cách chạy và khoá tập test

```text
experiments/results/<split>/<run_name>/
├── config.json        # RetrievalConfig + intent + intent_mode + commit hash
├── per_query.csv
└── summary.csv        # mỗi dòng 1 type, mỗi cột 1 chỉ số ở mục 7.2
experiments/results/figures/*.png
```

```bash
# Tập dev: chạy bao nhiêu lần cũng được
python experiments/evaluate.py --split dev --run-name baseline --retriever jaccard --intent majority
python experiments/evaluate.py --split dev --run-name word_v1
python experiments/run_ablation.py --split dev --group E3

# Tập test: CHỈ MỘT LẦN, T5 15/10 21:00 (V18), chấm cả mẻ FROZEN_COMPARISONS
python experiments/run_ablation.py --split test --final
```

- `--split dev` gộp tất cả file `experiments/dev/queries_dev_*.csv`.
- `evaluate.py` **không nhận** `--split test`. Tập test chỉ chạy qua `run_ablation.py --split test --final`.
- **Khoá tập test (`experiments/results/test/LOCK`):**
  - Chỉ ghi `LOCK` **sau khi cả mẻ chạy xong không lỗi**. Nội dung: thời điểm, commit hash, mã băm (hash) của `FROZEN_COMPARISONS`, danh sách run.
  - Nếu `LOCK` đã tồn tại, script **từ chối chạy**, trừ khi có `--rerun-reason "<lý do>"`.
  - Chạy lại **chỉ được phép để sửa bug trong code đánh giá**, không bao giờ để đổi tham số. Script kiểm tra hash của `FROZEN_COMPARISONS` phải trùng với hash trong `LOCK`, và ghi thêm một dòng vào `experiments/results/test/RERUN_LOG.md` (thời điểm, commit, lý do).

### 7.5 Chọn cấu hình, ngưỡng và mô hình intent (V15)

Chọn theo **hai bước**, để không bị vòng tròn giữa cấu hình và ngưỡng:

1. **Cấu hình retrieval:** trong các cấu hình đã chạy ở E1–E4, chọn cấu hình có **MRR@10 trung bình của `paraphrase` và `typo` cao nhất** trên tập dev. Chỉ số này không phụ thuộc ngưỡng. Nếu bằng nhau, chọn cấu hình đơn giản hơn (word, rồi char, rồi hybrid).
2. **Ngưỡng:** `sweep_threshold.py` quét `threshold` từ 0 đến 1, bước 0.01, cho *đúng cấu hình vừa chọn*. Câu bị từ chối khi `top1_score < th` hoặc `top1_score == 0`. Chọn mức có **Balanced E2E** cao nhất; bằng nhau thì lấy mức nhỏ hơn. Xuất `threshold_sweep.csv` và biểu đồ.
3. **Mô hình intent:** chọn giữa `nb` và `logreg` theo **Intent Acc (LODO)** trên tập dev; nếu chênh dưới 1 câu thì xét accuracy 5-fold CV (mục 7.10); nếu vẫn bằng thì chọn `nb`.

Không bước nào được dùng tập test.

### 7.6 Baseline — `experiments/baselines.py` (Vinh)

```python
class JaccardRetriever:
    def __init__(self, documents: list[Document], threshold: float = 0.0) -> None: ...
    def rank(self, query: str) -> Ranked: ...
    def search(self, query: str, top_k: int = 3) -> Ranked: ...

def majority_intent(documents: list[Document]) -> str: ...

def knn_intent(ranked: Ranked, k: int, exclude_id: str | None = None) -> tuple[str, float]: ...
```

- **`JaccardRetriever`** có cùng `rank` và `search` như `Retriever` (cùng quy tắc ở mục 5.3), nên `evaluate.py` dùng thay thế được.
  - Score là `|Q ∩ D| / |Q ∪ D|`, với Q và D là tập token (dùng `tokenize(..., remove_stopwords=True)`) của query và của `doc["text"]`.
- **`majority_intent`** trả về intent xuất hiện nhiều nhất. Dữ liệu cân bằng (mỗi intent 16 tài liệu), nên khi bằng nhau lấy intent đứng đầu `INTENTS`.
  - Baseline này tương đương **đoán ngẫu nhiên, khoảng 1/7 ≈ 14,3%**. Đây là mức sàn mà bộ phân loại nào cũng phải vượt.
- **`knn_intent`** là k-NN (CS50 W4) dùng chính thứ hạng cosine của retriever.
  - Lấy k tài liệu đầu của `ranked`, bỏ qua tài liệu có `id == exclude_id`. Ở chế độ LODO, `exclude_id` là `expected_doc_id`.
  - Mỗi intent được cộng dồn score của các tài liệu thuộc nó; intent có tổng lớn nhất thắng.
  - Confidence là tổng score của intent thắng chia cho tổng score của k tài liệu. Nếu mọi score bằng 0 thì trả về `majority_intent`, confidence 0.
  - `k = 1` chính là phương án dự phòng `top1_doc` trong `student_core`.

### 7.7 Hàm `evaluate_run` và các tuỳ chọn dòng lệnh (Vinh)

```python
def evaluate_run(
    queries: list[dict[str, str]],
    documents: list[Document],
    retriever: Retriever | JaccardRetriever | BM25Retriever,       # bất kỳ object nào có rank() và search()
    intent: IntentConfig | Literal["majority", "knn1", "knn5"],
    intent_mode: Literal["full", "lodo"] = "full",
) -> pandas.DataFrame: ...
```

| Cờ của `evaluate.py` | Giá trị | Mặc định |
|---|---|---|
| `--split` | chỉ `dev` | `dev` |
| `--run-name` | tên thư mục kết quả | bắt buộc |
| `--retriever` | `tfidf` (dùng `DEFAULT_RETRIEVAL_CONFIG`) / `jaccard` / `bm25` | `tfidf` |
| `--intent` | `model` (dùng `DEFAULT_INTENT_CONFIG`) / `majority` / `knn1` / `knn5` | `model` |
| `--intent-mode` | `full` / `lodo` | `full` |

Ở chế độ `lodo`: với `IntentConfig` thì train lại mô hình sau khi bỏ `expected_doc_id`; với `knn1` và `knn5` thì truyền `exclude_id=expected_doc_id`. Nhờ vậy 5 cách phân loại trong E5 được so sánh công bằng.

### 7.8 `run_ablation.py` (Vinh; Việt Anh thêm nhóm E3, E4)

```python
EXPERIMENTS: dict[str, dict[str, tuple[RetrievalConfig | str, IntentConfig | str, str]]]
#            nhóm ("E1"…"E5") → tên run → (retrieval, intent, intent_mode)
FROZEN_COMPARISONS: dict[str, tuple[RetrievalConfig | str, IntentConfig | str, str]]
#            chốt ở V17 (14/10); phải có run tên "final" = cấu hình DEFAULT
```

- `python experiments/run_ablation.py --split dev --group E3` chạy một nhóm trên tập dev và gộp kết quả vào `experiments/results/dev/ablation_<nhóm>.csv`.
- `python experiments/run_ablation.py --split test --final` chạy **toàn bộ `FROZEN_COMPARISONS` trên tập test trong một mẻ**, áp dụng khoá ở mục 7.4.
- Giá trị chuỗi cho retrieval là `"jaccard"` hoặc `"bm25"` (tham số mặc định); cho intent là `"majority"`, `"knn1"`, `"knn5"`.
- `FROZEN_COMPARISONS` gồm: run `final`, baseline Jaccard + majority, các biến thể retrieval chính (word, char, hybrid tốt nhất, BM25), và 5 cách phân loại intent (full và LODO). **Lựa chọn cuối cùng vẫn là cấu hình đã chọn trên dev**, kết quả test của các run so sánh chỉ để báo cáo.

### 7.9 Đường cong suy giảm theo lỗi gõ — `noise_curve.py` (Việt Anh, E3b)

- Đầu vào: 49 câu `normal` trong `queries_dev_auto.csv` (chỉ tài liệu không thuộc tập test).
- Với mỗi mức k = 0, 1, 2, 3: gọi `_make_typo` của `scripts/generate_corpus.py` k lần lên mỗi câu, lần thứ j dùng `random.Random(1000 * k + 100 * j + i)` (i là số thứ tự câu). Chấp nhận khả năng nhỏ hai lần đảo trùng một chỗ.
- Phương pháp so sánh: Jaccard, TF-IDF theo từ, n-gram ký tự, kết hợp (α tốt nhất từ E4).
- Chỉ số: Hit@1 và MRR@10 theo k. Xuất `experiments/results/dev/noise_curve.csv` và `experiments/results/figures/noise_curve.png`.

### 7.10 Cross-validation cho intent — `intent_cv.py` (Dương, E5b)

- `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` trên 112 tài liệu, nhãn là `intent`.
- Mỗi fold: `fit` trên tài liệu của fold train, dự đoán `text` của tài liệu fold test, cho NB, LR, SVM (cả `bow` và `tfidf`).
- k-NN trong CV: dựng `Retriever` chỉ trên tài liệu fold train, rồi dùng `knn_intent` với k = 1 và 5. Thêm `majority_intent` làm mức sàn.
- Báo cáo accuracy và macro-F1 dạng trung bình ± độ lệch chuẩn qua 5 fold. Xuất `experiments/results/dev/intent_cv.csv`.
- Ghi rõ hạn chế: đơn vị dự đoán ở đây là *tài liệu* (dài), khác *câu hỏi* (ngắn) của E5.

---

## 8. Tập dev

Tập dev gồm **146 câu**: 98 câu sinh tự động và 48 câu viết tay.

**Phần tự sinh: `experiments/dev/queries_dev_auto.csv` (V05, Vinh)**
- Tạo bằng `experiments/make_auto_dev.py`, cho **49 FAQ không thuộc tập test** (script đọc cột `expected_doc_id` của `queries_test.csv` để loại 35 tài liệu đích).
- Mỗi FAQ cho 2 câu: `normal` (chép nguyên câu hỏi) và `typo` (gọi `_make_typo` của thầy với `random.Random(42000 + i)`, i là số thứ tự FAQ theo `id` tăng dần).
- `id`: `dev_auto_n_01…` và `dev_auto_t_01…`.

**Phần viết tay: chỉ Việt Anh và Dương viết**
- Vinh **không viết** câu paraphrase và câu ngoài kho, vì đã nhìn thấy câu của tập test trong lúc lập kế hoạch.
- Mỗi người một file: `queries_dev_vietanh.csv` và `queries_dev_duong.csv` (header đã tạo sẵn). Cột giống hệt `data/queries_test.csv`: `id,query,type,expected_intent,expected_doc_id,notes`.
- `id` có tiền tố theo người: `dev_a_01…`, `dev_d_01…`.
- **Mỗi người 24 câu:** 14 câu `paraphrase` (2 tài liệu đích cho mỗi intent, theo bảng dưới) và 10 câu `out_of_corpus`.

| Loại | Cách viết |
|---|---|
| `paraphrase` | diễn đạt lại cùng ý câu hỏi của FAQ, như sinh viên thật sẽ hỏi; **tránh lặp lại từ khoá chính** của câu gốc |
| `out_of_corpus` | ít nhất 6 câu *nghe như* về trường (có các từ campus, university, student…) nhưng kho tài liệu **không trả lời được**, và ít nhất 2 câu hỏi chung ngoài trường. Kiểm tra lại với `data/documents.md`. Để trống `expected_intent` và `expected_doc_id` |

- Chỉ viết tiếng Anh, dùng ký tự ASCII. Không chép ví dụ có trong tài liệu của nhóm.
- **Không mở `data/queries_test.csv`.**
- **Hạn: CN 04/10 12:00** (A02, D02). Vinh kiểm tra lúc 18:00 cùng ngày (V06).

**Tài liệu đích cho câu paraphrase.** Không trùng 35 tài liệu đích của tập test.

| Intent | Việt Anh | Dương |
|---|---|---|
| `course_registration` | `faq_course_registration_06`, `faq_course_registration_08` | `faq_course_registration_07`, `faq_course_registration_10` |
| `exam` | `faq_exam_07`, `faq_exam_09` | `faq_exam_08`, `faq_exam_10` |
| `tuition` | `faq_tuition_07`, `faq_tuition_09` | `faq_tuition_08`, `faq_tuition_10` |
| `class_schedule` | `faq_class_schedule_06`, `faq_class_schedule_09` | `faq_class_schedule_08`, `faq_class_schedule_10` |
| `student_services` | `faq_student_services_05`, `faq_student_services_10` | `faq_student_services_08`, `faq_student_services_11` |
| `graduation` | `faq_graduation_04`, `faq_graduation_08` | `faq_graduation_06`, `faq_graduation_10` |
| `technical_support` | `faq_technical_support_05`, `faq_technical_support_09` | `faq_technical_support_08`, `faq_technical_support_10` |

---

## 9. Quy ước Git

- **Tên nhánh:** `<tên>/<mã-việc>-<mô-tả>`, ví dụ `vietanh/A04-retriever`, `duong/D04-intent-nb`, `vinh/V08-evaluate`.
- **Không push thẳng `main`.** Nếu repo bật được bảo vệ nhánh (cần GitHub Pro, miễn phí qua GitHub Student Developer Pack) thì bật; nếu không, đây là quy ước cả nhóm tự giữ.
- **Người duyệt:**
  - PR của **Việt Anh** và **Dương** do **Vinh** (nhóm trưởng) duyệt;
  - PR của **Vinh** do **Việt Anh** duyệt.
- **Thời hạn review:** **12 giờ** với PR nằm trên tiến độ chung (A03, A04, A05, V08); **24 giờ** với PR khác.
- **PR nháp sớm:** việc lớn mở PR nháp (draft) ngay khi có khung chạy được, để nhận góp ý trước hạn.
- **Trước khi mở PR**, chạy `pytest -q` ở gốc repo và phải xanh hoàn toàn. CI trên GitHub cũng phải xanh.
- **Commit message:** `<mã-việc> <module>: <mô tả ngắn>`, ví dụ `A04 retrieval: add word-level tf-idf`, `D04 intent: add multinomial nb`.
