# Lộ trình học — Project 12

> Dành cho cả nhóm, học từ đầu. Project 12 chỉ dùng một mảng hẹp của AI: **biểu diễn và truy hồi văn bản cổ điển**, cộng một ít **học máy có giám sát** và **đánh giá mô hình**. Không cần học hết môn trước khi làm.
>
> Mã việc (A04, D03, V13…) tham chiếu tới [PLAN.md](../PLAN.md). Mọi link đã kiểm tra mở được ngày 03/10/2026.

---

## Cách học

1. **Học vừa đủ cho việc sắp đến hạn**, theo đúng cột "Khi nào" bên dưới. Ví dụ word2vec chỉ cần cho slide so sánh vào giữa tháng.
2. **Mỗi chủ đề làm 3 bước:** xem đoạn video bài giảng, đọc notes, rồi **tính tay một ví dụ nhỏ**. Tính tay được mới là hiểu, và đó cũng là thứ hội đồng hay hỏi khi vấn đáp.
3. **Tự kiểm tra bằng [`qa_bank.md`](qa_bank.md):** trả lời được các câu trong đó bằng lời của mình là đủ.

**Nguồn chính:**
- [CS50 AI](https://cs50.harvard.edu/ai/): notes từng tuần, kèm [playlist video bài giảng trên YouTube](https://www.youtube.com/playlist?list=PLhQjrBD2T381PopUTYtMSstgk-hsTGkVm).
- [Ghi chú của thầy](https://sharing.vinhnguyenthanh.com/courses/intro-ai/) (tiếng Việt).
- Sách [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/) (Manning, Raghavan, Schütze; Stanford, đọc miễn phí): nguồn chuẩn cho TF-IDF, cosine, BM25 và chỉ số đánh giá truy hồi.
- [Tài liệu scikit-learn](https://scikit-learn.org/stable/). Link trỏ tới bản *stable* mới nhất; repo dùng bản **1.5.2**, các tham số cơ bản giống nhau. Nếu thấy lệch, đổi `stable` trong link thành `1.5`.

> Lưu ý: **TF-IDF và cosine không có trong notes CS50 hiện tại.** Hai chủ đề này phải học từ sách IR và scikit-learn. Trên slide cần nói rõ đây là phần mở rộng từ Bag-of-Words (xem PLAN mục 1.5).

---

## 1. Nền tảng chung — cả 3 người, trước T4 07/10

| Chủ đề | Học để hiểu gì | Tài liệu |
|---|---|---|
| Bức tranh chung | AI gồm những mảng nào; project này nằm ở đâu | Thầy: [Tổng quan về Trí tuệ Nhân tạo](https://sharing.vinhnguyenthanh.com/courses/intro-ai/00-overview) |
| Tokenization, n-gram, Bag-of-Words | Máy biến một câu thành tập từ và vector đếm từ như thế nào | [CS50 Lecture 6](https://cs50.harvard.edu/ai/notes/6/): mục *Tokenization*, *n-grams*, *Bag-of-Words Model* |
| Stopwords | Vì sao bỏ các từ như "the", "is"; khi nào không nên bỏ | Sách IR: [Dropping common terms: stop words](https://nlp.stanford.edu/IR-book/html/htmledition/dropping-common-terms-stop-words-1.html) |
| **TF-IDF và cosine similarity** | Vì sao từ hiếm quan trọng hơn từ phổ biến; đo độ giống nhau giữa câu hỏi và tài liệu | Sách IR **chương 6**: [Scoring, term weighting and the vector space model](https://nlp.stanford.edu/IR-book/html/htmledition/scoring-term-weighting-and-the-vector-space-model-1.html) · scikit-learn: [Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html) (mục *Tf–idf term weighting*) |
| Train / dev / test, overfitting, rò rỉ dữ liệu | Vì sao phải có tập dev; vì sao chỉ chạy tập test một lần | Thầy: [Evaluating Models](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning-evaluation) §1–§2, §8 · [Learning — Học từ dữ liệu](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning) |

**Tự kiểm tra:** tính tay được TF-IDF và cosine cho 3 câu ngắn. Việc A01 của Việt Anh làm đúng việc này; xem chung file `notes/hand_calc.md` khi có.

---

## 2. Theo vai

### Việt Anh — retrieval

| Khi nào | Chủ đề | Tài liệu |
|---|---|---|
| Trước T3 06/10 (A04) | Mô hình không gian vector, chuẩn hoá L2, cosine bằng tích vô hướng; công thức IDF của scikit-learn | Sách IR [chương 6](https://nlp.stanford.edu/IR-book/html/htmledition/scoring-term-weighting-and-the-vector-space-model-1.html) · scikit-learn [Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html) |
| Trước CN 11/10 (A07) | N-gram ký tự (`analyzer="char_wb"`): vì sao giúp với lỗi gõ và biến thể từ | scikit-learn [Text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html), mục về character n-grams |
| Trước T4 14/10 (A10) | word2vec, attention, Transformer, để so sánh lý thuyết trên slide | [CS50 Lecture 6](https://cs50.harvard.edu/ai/notes/6/): mục *Word Representation*, *word2vec*, *Neural Networks*, *Attention*, *Transformers* · Thầy: [Neural Networks](https://sharing.vinhnguyenthanh.com/courses/intro-ai/19-neural-networks) |

### Dương — phân loại intent và app demo

| Khi nào | Chủ đề | Tài liệu |
|---|---|---|
| Trước CN 04/10 (D03, đợt 1) | Naive Bayes, Laplace (additive) smoothing | [CS50 Lecture 6](https://cs50.harvard.edu/ai/notes/6/): mục *Naive Bayes* |
| Trước CN 04/10 (D03, đợt 1) | Dùng `CountVectorizer`, `MultinomialNB`, `Pipeline` trong scikit-learn | scikit-learn: [Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html) (mục *Multinomial Naive Bayes*) · [CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html) · [MultinomialNB](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html) · [Pipeline](https://scikit-learn.org/stable/modules/compose.html) |
| Trước CN 11/10 (D07, đợt 2) | Xác suất có điều kiện, Bayes' rule, nền của Naive Bayes | [CS50 Lecture 2](https://cs50.harvard.edu/ai/notes/2/): *Conditional Probability*, *Bayes' Rule* · Thầy: [Bất định và xác suất](https://sharing.vinhnguyenthanh.com/courses/intro-ai/12-uncertainty-probability), [Xác suất có điều kiện và Bayes](https://sharing.vinhnguyenthanh.com/courses/intro-ai/13-conditional-probability-bayes) |
| Trước CN 11/10 (D07, đợt 2) | k-NN, Perceptron và Logistic Regression, SVM | [CS50 Lecture 4](https://cs50.harvard.edu/ai/notes/4/) · Thầy: [Supervised Learning](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning-supervised) · scikit-learn: [Linear models](https://scikit-learn.org/stable/modules/linear_model.html), [SVM](https://scikit-learn.org/stable/modules/svm.html), [Nearest Neighbors](https://scikit-learn.org/stable/modules/neighbors.html) |
| Trước CN 11/10 (D06) | Xem một ví dụ đầy đủ: TF-IDF rồi so sánh nhiều bộ phân loại | scikit-learn: [Classification of text documents using sparse features](https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html) |
| Trước T2 12/10 (D08, D09) | Cross-validation phân tầng, ma trận nhầm lẫn, precision, recall, F1 | Thầy: [Evaluating Models](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning-evaluation) §5–§7 · scikit-learn: [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html), [StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html), [Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html) |
| Trước T5 15/10 (D10) | Streamlit cơ bản: ô nhập, nút, hiển thị kết quả | [Streamlit — Get started](https://docs.streamlit.io/get-started) |

### Vinh — đánh giá, ngưỡng và BM25

| Khi nào | Chủ đề | Tài liệu |
|---|---|---|
| Trước T3 06/10 (V07, V08) | Chỉ số đánh giá truy hồi: Precision@k, MRR, Hit@k | Sách IR **chương 8**: [Evaluation in information retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html) |
| Trước CN 11/10 (V13) | BM25: bão hoà tần suất từ (k1), chuẩn hoá độ dài tài liệu (b) | Sách IR **chương 11**: [Okapi BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html) |
| Trước T3 13/10 (V15) | Đánh đổi khi chọn ngưỡng: từ chối đúng và từ chối nhầm; chọn tham số bằng quét lưới | Thầy: [Evaluating Models](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning-evaluation) §6–§7 · [Tối ưu hoá: chọn phương án tốt nhất](https://sharing.vinhnguyenthanh.com/courses/intro-ai/optimization-overview) |
| Liên tục | Đọc lướt phần của hai bạn, để review PR và trả lời câu hỏi chung khi vấn đáp | Các link ở hai bảng trên |

---

## 3. Kỹ năng công cụ — học trong lúc làm

| Kỹ năng | Dùng để | Tài liệu |
|---|---|---|
| Python | Viết mọi thứ | [The Python Tutorial](https://docs.python.org/3/tutorial/) |
| numpy | Vector TF-IDF, tích vô hướng | [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html) |
| pandas | Đọc CSV, lập bảng kết quả | [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) |
| Git và GitHub | Tạo nhánh, commit, mở PR, review | [Pro Git](https://git-scm.com/book/en/v2) (chương 1–3) · [About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) |
| pytest | Viết test theo tiêu chí "xong" trong INTERFACE | [pytest — Get started](https://docs.pytest.org/en/stable/getting-started.html) |

---

## 4. Cập nhật

Bài **Language** trong ghi chú của thầy hiện chưa có nội dung ([link](https://sharing.vinhnguyenthanh.com/courses/intro-ai/20-language)). Mỗi buổi trinh sát thứ Bảy (N03, N05, N09) xem lại trang này; có nội dung mới thì bổ sung vào đây và đồng bộ thuật ngữ trên slide.
