# PLAN — Project 12 · Campus Notice & FAQ Assistant

> Môn Trí tuệ nhân tạo (AIN) · Nhóm: **Vinh** (nhóm trưởng), **Việt Anh**, **Dương**
> Đề bài của thầy: [ASSIGNMENT.md](ASSIGNMENT.md) · Hợp đồng kỹ thuật: [INTERFACE.md](INTERFACE.md) · Câu hỏi vấn đáp: [notes/qa_bank.md](notes/qa_bank.md)
>
> 🎯 **Midterm: thuyết trình thứ Bảy 31/10/2026** · Mục tiêu nội bộ: **sẵn sàng từ Chủ nhật 25/10**
> Phiên bản **v2** (sau rà soát) · Cập nhật 01/10/2026

---

## 0. Đọc trong 1 phút

- **Nhóm làm gì?** Một trợ lý trả lời câu hỏi hành chính của sinh viên. Hệ thống đoán **chủ đề** câu hỏi, tìm **tài liệu FAQ hoặc thông báo liên quan nhất**, và **biết từ chối** khi câu hỏi nằm ngoài kho tài liệu.
- **Kỹ thuật:** TF-IDF và cosine similarity (tự viết); phân loại intent bằng Naive Bayes và Logistic Regression (scikit-learn), so sánh thêm với k-NN và SVM. Không được dùng LLM.
- **Phần khó thật sự:** câu **diễn đạt lại** (paraphrase) và việc **chọn ngưỡng từ chối**. Câu gõ sai một chữ gần như không làm hỏng TF-IDF (mục 1.7).
- **Phần quan trọng nhất là Midterm** (40 điểm): code lõi, thí nghiệm, slide và demo trực tiếp, **thuyết trình ngày 31/10**.
- **Gắn với môn học thế nào?** Xem **mục 1.5**. **Bài thuyết trình gồm gì, ai trình bày slide nào?** Xem **mục 1.9**.
- **Hôm nay bạn làm gì?** Xem **mục 3**. **Việc nào hạn khi nào?** Xem **mục 5** (theo người) hoặc **mục 6** (theo ngày).
- **Ba luật cứng:**
  1. Không dùng LLM trong code chạy.
  2. Việt Anh và Dương **không mở `data/queries_test.csv` trước 15/10**.
  3. Tập test **chỉ chạy một lần**, tối T5 15/10.

---

## 1. Tổng quan dự án

### 1.1 Mục tiêu

Sinh viên gõ một câu hỏi tiếng Anh, ví dụ *"When is tuition due for the semester?"*. Hệ thống phải:

1. **Phân loại intent:** câu hỏi thuộc chủ đề nào trong 7 chủ đề: `course_registration`, `exam`, `tuition`, `class_schedule`, `student_services`, `graduation`, `technical_support`. Kèm theo **độ tin cậy %**.
2. **Truy hồi tài liệu:** trả về top-k tài liệu FAQ hoặc thông báo liên quan nhất, kèm **điểm tương đồng** và **nguồn**.
3. **Từ chối trả lời** khi không có tài liệu nào đủ liên quan, ví dụ *"Which bus goes to the city zoo on Sundays?"*. **Không được bịa câu trả lời.**

Hệ thống còn phải chịu được ba kiểu câu khó: câu **diễn đạt lại** (paraphrase), câu **gõ sai** (typo) và câu **ngoài kho tài liệu** (out-of-corpus, viết tắt OOC).

### 1.2 Hệ thống hoạt động thế nào

```text
                    ┌──────────────── retrieval.py (Việt Anh) ─────────────────┐
câu hỏi ──► tokenize ──► vector TF-IDF ──► cosine với 112 tài liệu ──► xếp hạng ──► score top-1 < ngưỡng?
   │                                                                                 ├─ có    → [] (từ chối)
   │                                                                                 └─ không → top-k tài liệu
   │
   └──────► intent.py (Dương): BoW/TF-IDF ──► Naive Bayes / Logistic Regression ──► (intent, độ tin cậy)

student_core.py: retrieve() và classify_intent() — app và chấm điểm gọi 2 hàm này
app.py (Dương): giao diện demo · experiments/ (Vinh, Việt Anh, Dương): chỉ số, bảng, biểu đồ
```

### 1.3 Dữ liệu

| File | Nội dung |
|---|---|
| `data/faq.json` | 84 câu hỏi và trả lời FAQ, mỗi intent 12 câu |
| `data/notices.json` | 28 thông báo, mỗi intent 4 thông báo |
| `data/intents.csv` | 7 intent kèm mô tả |
| `data/queries_test.csv` | **120 câu đánh giá** (35 normal, 35 paraphrase, 35 typo, 15 ngoài kho). **Chỉ chạy một lần vào 15/10** |
| `data/documents.md` | danh sách mọi tài liệu cho người đọc |
| `experiments/dev/` | **tập dev 146 câu của nhóm**, dùng cho mọi việc tinh chỉnh: 98 câu tự sinh (49 normal, 49 typo) và 48 câu viết tay (28 paraphrase, 20 ngoài kho). Chi tiết ở INTERFACE §8 |

Thư mục `data/` của thầy không được sửa.

### 1.4 Midterm nộp gì, chấm thế nào

| Hạng mục chấm | Điểm | Nhóm đáp ứng bằng |
|---|---|---|
| Mô hình không gian vector và retrieval đúng | 15 | `retrieval.py` tự viết, khớp sklearn; `intent.py`; ví dụ tính tay |
| Phân tích độ bền và hiệu chỉnh ngưỡng | 10 | Thí nghiệm E0–E6 (mục 1.6), đường cong suy giảm theo lỗi gõ, đường cong ngưỡng, phân tích lỗi và phân tích câu ngoài kho |
| Thuyết trình và demo trực tiếp | 15 | Slide, app demo, 3 buổi diễn tập, ngân hàng câu hỏi |

**Cần nộp:** code `student_core.py` và các module, script thí nghiệm, `presentation.pdf`, kèm demo trực tiếp.

**Đề bài bắt buộc:** báo cáo MRR, Precision@k, Intent Accuracy, tách theo `normal` / `paraphrase` / `typo`; mô tả mức sụt giảm khi câu hỏi thay đổi từ ngữ; **phân tích lỗi trên câu ngoài kho**.

### 1.5 Ánh xạ với nội dung khoá học

Project 12 thuộc mảng **Language** trong 7 mảng của CS50 AI, nhưng dùng kiến thức của nhiều tuần. Mỗi slide thuật toán phải ghi rõ "kiến thức trong môn" theo bảng này. Bảng đã được đối chiếu với notes CS50 tuần 2, 4, 6 và các trang ghi chú của thầy.

| Thành phần của project | CS50 AI (notes) | Ghi chú của thầy | Mức gắn |
|---|---|---|---|
| Tokenize, n-gram theo từ và theo ký tự | **W6 Language**: Tokenization, n-grams | (bài Language chưa có nội dung) | Trực tiếp |
| Bag-of-Words; baseline Jaccard | **W6**: Bag-of-Words Model | — | Trực tiếp |
| TF-IDF: vector có trọng số cho tài liệu | **W6**: Bag-of-Words, Word Representation (one-hot so với distributed) | — | **Mở rộng.** TF-IDF là BoW có trọng số; notes CS50 hiện tại **không dạy TF-IDF**, phải nói rõ là phần nhóm tự tìm hiểu thêm |
| Cosine similarity, xếp hạng top-k | **W4 Learning**: Nearest-Neighbor Classification (đổi độ đo Euclid thành cosine) | *Supervised Learning* §2 k-NN; *Unsupervised* (Euclid, Manhattan, Cosine) | **Mở rộng.** Thầy viết "k-NN không phù hợp với văn bản thô", phải giải thích được vì sao cosine trên TF-IDF thưa vẫn dùng được (`qa_bank.md` câu 17) |
| Naive Bayes (intent) | **W2 Uncertainty**: xác suất có điều kiện, Bayes' rule, độc lập; **W6**: Naive Bayes, additive (Laplace) smoothing | *Xác suất có điều kiện và Bayes* (ví dụ lọc spam) | Trực tiếp |
| Logistic Regression (intent) | **W4**: Perceptron learning, Regression, Loss functions, Regularization | *Supervised Learning* §3–§5 (linear classifier, perceptron, sigmoid) | Trực tiếp |
| Linear SVM (intent, để so sánh) | **W4**: Support Vector Machines | *Supervised Learning* §6 | Trực tiếp |
| k-NN cho intent (k = 1 và k = 5) | **W4**: Nearest-Neighbor Classification | *Supervised Learning* §2 | Trực tiếp |
| Tập train/dev/test, rò rỉ dữ liệu, LODO | **W4**: Overfitting, holdout cross-validation | *Evaluating Models* §2, §8 (data leakage) | Trực tiếp |
| 5-fold cross-validation cho intent | **W4**: holdout cross-validation | *Evaluating Models* §5 (k-Fold Cross-Validation) | Trực tiếp |
| Precision, Recall, F1, ma trận nhầm lẫn | — | *Evaluating Models* §6–§7 | Trực tiếp |
| MRR, P@k, Hit@k | — | *Evaluating Models* (precision là nền) | **Mở rộng**: chỉ số chuyên cho bài toán truy hồi |
| Ngưỡng từ chối trả lời | **W4**: ngưỡng của perceptron (phép tương tự) | *Supervised Learning* §5; *Evaluating Models* (đánh đổi precision và recall) | Liên hệ |
| Chọn ngưỡng và α bằng quét lưới | **W3 Optimization**: hàm mục tiêu, tìm phương án tốt nhất | *Tối ưu hoá: chọn phương án tốt nhất* | Liên hệ |
| BM25 (chỉ để so sánh) | — | — | **Ngoài môn** (sách *Introduction to Information Retrieval*, chương 11). Sản phẩm vẫn dùng cosine như đề bài yêu cầu |
| So sánh lý thuyết với word2vec, Transformer, LLM | **W6**: word2vec, Attention, Transformers; **W5**: Neural Networks | *Neural Networks* | So sánh, không cài đặt |

### 1.6 Các thí nghiệm

Tất cả chạy trên **tập dev**, trừ dòng cuối.

| Mã | Thí nghiệm | Câu hỏi cần trả lời | Kiến thức môn | Người chạy | Hạn |
|---|---|---|---|---|---|
| E0 | Baseline: Jaccard (retrieval) và lớp phổ biến nhất (intent) | Mức sàn là bao nhiêu? | W6 BoW | Vinh | 07/10 |
| E1 | Lập chỉ mục chỉ `question` hay `question + answer` | Thêm phần trả lời có giúp câu paraphrase không? | W6 BoW | Vinh | 10/10 |
| E2 | Tuỳ chọn theo từ: stopwords, bigram, sublinear tf | Tuỳ chọn nào có ích? | W6 n-grams | Vinh | 10/10 |
| E3 | TF-IDF n-gram ký tự | Có giúp **câu paraphrase** (biến thể từ như register/registration) và **tách câu ngoài kho** không? | W6 n-grams | Việt Anh | 12/10 |
| E3b | Đường cong suy giảm theo số lỗi gõ, 0 → 3 lỗi mỗi câu | Mỗi phương pháp chịu lỗi gõ tới mức nào? | W6 n-grams | Việt Anh | 13/10 |
| E4 | Kết hợp từ và ký tự, α ∈ {0.3, 0.5, 0.7} | Kết hợp có tốt hơn từng cách riêng không? | W6, W3 | Việt Anh | 12/10 |
| E5 | **So sánh 5 cách phân loại intent** trên câu hỏi: lớp phổ biến nhất, k-NN (k = 1, 5), Naive Bayes, Logistic Regression, Linear SVM; train đầy đủ và LODO | Thuật toán nào tốt nhất? Rò rỉ làm điểm ảo bao nhiêu? | W2, W4, W6 | Vinh | 12/10 |
| E5b | 5-fold cross-validation phân tầng trên 112 tài liệu, cùng các thuật toán | Kết luận của E5 có vững khi đổi cách chia dữ liệu không? | W4 | Dương | 12/10 |
| E6 | Quét ngưỡng từ chối cho cấu hình đã chọn | Ngưỡng nào cân bằng tốt nhất giữa từ chối đúng và từ chối nhầm? | W3, W4 | Vinh | 13/10 |
| E7 | BM25 tự viết so với TF-IDF + cosine | Một thuật toán truy hồi ngoài môn có tốt hơn không? | ngoài môn | Vinh | 11/10 |
| **Test** | **Một mẻ duy nhất trên tập test:** cấu hình cuối và các phương pháp so sánh đã chốt | **Kết quả chính thức đưa vào slide** | | Vinh | **15/10** |

### 1.7 Sáu điều cần biết

1. **Lỗi gõ đảo một cặp chữ gần như không làm hỏng TF-IDF.** Câu hỏi có nhiều từ, sai một từ thì các từ còn lại vẫn đủ để tìm đúng. Đây là kết quả chạy thử sơ bộ ngày 01/10 trên 49 FAQ không thuộc tập test: TF-IDF theo từ đúng 48/49 câu typo. Vì vậy E3b đo thêm 2 và 3 lỗi mỗi câu để có câu chuyện độ bền thật.
2. **Phần khó là paraphrase và ngưỡng.** Cũng theo lần chạy thử đó, câu paraphrase chỉ đúng khoảng một nửa, và score của chúng *chồng lên* score của câu ngoài kho. Không có ngưỡng nào tách hoàn toàn hai loại, chỉ có điểm đánh đổi tốt nhất. Các số này chỉ để định hướng, không đưa vào báo cáo.
3. **Rò rỉ dữ liệu:** câu `normal` chép nguyên văn câu hỏi FAQ, mà mô hình intent lại train trên FAQ, nên điểm câu `normal` cao ảo. Vì vậy báo cáo thêm **Intent Acc (LODO)**.
4. **P@3 tối đa chỉ là 1/3**, vì mỗi câu chỉ có 1 tài liệu đúng. Báo cáo thêm **Hit@k** và giải thích trên slide.
5. **Câu ngoài kho cố ý chứa các từ "campus", "university"**, nên ngưỡng phải chọn có phương pháp (E6, INTERFACE §7.5).
6. **Không tinh chỉnh trên tập test.** Tập test có khoá `LOCK`, chỉ chạy một mẻ, chỉ được chạy lại để sửa bug code đánh giá (INTERFACE §7.4).

### 1.8 Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| **TF-IDF** | trọng số của một từ trong tài liệu: từ xuất hiện nhiều trong tài liệu này (TF) và hiếm ở các tài liệu khác (IDF) thì trọng số cao |
| **Cosine similarity** | độ giống nhau giữa 2 vector, tính bằng cos góc giữa chúng, nằm trong [0, 1] |
| **Tập dev / tập test** | dev: câu nhóm tự có, dùng để tinh chỉnh · test: `queries_test.csv`, chỉ dùng để báo cáo kết quả cuối |
| **OOC, từ chối (abstain)** | câu hỏi ngoài kho tài liệu · `retrieve` trả về `[]` |
| **LODO** | leave-one-document-out: train lại sau khi bỏ tài liệu đích, để đánh giá không rò rỉ |
| **MRR, Hit@k** | trung bình của 1/(vị trí tài liệu đúng) · tài liệu đúng có nằm trong top-k hay không |
| **Balanced E2E** | trung bình độ chính xác đầu-cuối của 4 loại câu (normal, paraphrase, typo, ngoài kho), mỗi loại ¼ |
| **Đóng băng** | từ 14/10, không đổi bất kỳ tham số nào |

### 1.9 Bài thuyết trình Midterm

**Bốn phần đầu đi theo đúng thứ tự môn yêu cầu:**
1. Project làm gì.
2. Team đã làm gì, làm như thế nào.
3. Dùng thuật toán gì.
4. So sánh với các thuật toán khác.

Phần ⑤ Kết quả và ⑥ Kết luận là nhóm bổ sung. Nếu thầy có template riêng thì Vinh chỉnh lại dàn ý này.

**Nguyên tắc:**
- **17 slide nội dung, kèm 6 slide phụ lục** chỉ dùng khi hỏi đáp. Nếu thời lượng ngắn (10–15 phút), cắt bớt từ phần ⑤.
- **Demo xuất hiện hai lần:** một demo nhanh ngay sau phần ①, và demo các câu khó ở cuối. Có thiếu giờ thì demo vẫn đã diễn ra.
- **Mỗi slide thuật toán (8–11) theo khung 4 ô:** Ý tưởng · Công thức · Ví dụ nhỏ · Kiến thức trong môn (lấy từ mục 1.5).

| # | Phần | Nội dung slide | Kiến thức môn | Trình bày | Lấy từ việc |
|---|---|---|---|---|---|
| 1 | Mở đầu | Tên project, thành viên, dàn ý bài | — | Vinh | V16 |
| 2 | **① Project làm gì** | Bài toán trợ lý FAQ: đầu vào, đầu ra, 3 yêu cầu (phân loại intent, truy hồi, từ chối) | W6 | Dương | ASSIGNMENT.md |
| 3 | ① | Dữ liệu: 112 tài liệu, 7 intent, 120 câu test chia theo 4 loại; thống kê corpus | — | Dương | D05 |
| 4 | ① | **Demo nhanh**: một câu bình thường chạy trên app | — | Dương | D10 |
| 5 | **② Team đã làm gì, làm thế nào** | Sơ đồ hệ thống, ai làm phần nào; quy trình dev/test, đóng băng, khoá tập test | W4 holdout, overfitting | Vinh | V08, V17 |
| 6 | ② | Cách đo: MRR, P@k, Hit@k, Intent Acc, Balanced E2E; vì sao P@3 tối đa là 1/3 | *Evaluating Models* | Vinh | V07 |
| 7 | ② | Ánh xạ kiến thức môn học (bảng rút gọn của mục 1.5) | W2–W6 | Vinh | mục 1.5 |
| 8 | **③ Thuật toán** | TF-IDF và cosine: công thức, ví dụ tính tay, vì sao dùng cosine thay cho Euclid | W6 (mở rộng), W4 | Việt Anh | A01, A04 |
| 9 | ③ | N-gram ký tự và kết hợp với n-gram từ | W6 | Việt Anh | A07 |
| 10 | ③ | Quy tắc từ chối: ngưỡng trên score top-1 | W4 (liên hệ) | Việt Anh | A04, V15 |
| 11 | ③ | Naive Bayes (Bayes' rule, giả định độc lập, Laplace smoothing) và Logistic Regression | W2, W4, W6 | Dương | D04, D06 |
| 12 | **④ So sánh** | Retrieval: Jaccard, TF-IDF theo từ, n-gram ký tự, kết hợp, BM25; so sánh lý thuyết với word2vec, Transformer, LLM | W5, W6 | Việt Anh | A08, A10, V13 |
| 13 | ④ | Intent: lớp phổ biến nhất, k-NN, NB, LR, SVM; train đầy đủ và LODO; 5-fold CV. NB là mô hình sinh, LR và SVM là mô hình phân biệt | W2, W4 | Dương | V14, D08, D09 |
| 14 | **⑤ Kết quả** | Kết quả chính thức trên tập test theo loại câu; đường cong suy giảm theo số lỗi gõ | — | Vinh | V18, V19, A09 |
| 15 | ⑤ | Chọn ngưỡng: đường cong đánh đổi; phân tích câu ngoài kho lọt ngưỡng và câu bị từ chối nhầm | W3 | Vinh | V15, V20 |
| 16 | ⑤ | Phân tích lỗi: retrieval (giải thích bằng `explain()`) và intent | — | Việt Anh, Dương | A12, D11 |
| 17 | **⑥ Kết luận** | **Demo các câu khó**: paraphrase, typo, ngoài kho | — | Vinh | D10 |
| 18 | ⑥ | Hạn chế; hướng làm cho Final (đóng gói thành app) | — | Vinh | — |
| 19 | | Hỏi đáp | | Cả nhóm | `qa_bank.md` |
| P1 | Phụ lục | Tính tay TF-IDF đầy đủ | | Việt Anh | A01 |
| P2 | Phụ lục | Tính tay Naive Bayes | | Dương | D04 |
| P3 | Phụ lục | Bảng đầy đủ E1–E4, E7 | | Việt Anh | A08 |
| P4 | Phụ lục | Bảng đầy đủ E5 và E5b | | Dương | D08 |
| P5 | Phụ lục | So sánh lý thuyết chi tiết | | Việt Anh | A10 |
| P6 | Phụ lục | Cấu hình đóng băng (`config.json`) và quy trình chọn | | Vinh | V17 |

**Chia thời gian gợi ý:** ① kèm demo nhanh 15% · ② 15% · ③ 25% · ④ 15% · ⑤ 20% · ⑥ 10%. Chốt lại khi thầy trả lời về thời lượng (mục 8).

---

## 2. Phân vai

| Người | Midterm | Final |
|---|---|---|
| **Vinh** (nhóm trưởng) | **Code:** `metrics.py`, `evaluate.py`, `baselines.py` (Jaccard, majority, k-NN), **`bm25.py` (BM25 tự viết)**, `run_ablation.py` (chạy tập test một mẻ có khoá), `sweep_threshold.py` (hiệu chỉnh ngưỡng từ chối), `make_auto_dev.py`. **Thí nghiệm:** E0–E2, E5, E6, E7; chọn cấu hình; chạy tập test; phân tích câu ngoài kho. Ghép slide; **điều phối; review toàn bộ bài của Việt Anh và Dương** | App Streamlit (phát triển từ bản demo của Dương), tab Evaluation dashboard, README |
| **Việt Anh** | `preprocess.py`, **`retrieval.py`** (TF-IDF và cosine tự viết, `explain`), wiring `student_core`, **chạy E3, E3b, E4**, so sánh lý thuyết; review PR của Vinh | Chủ biên báo cáo IEEE, test tự động, tối ưu tốc độ |
| **Dương** | **`intent.py`** (NB, LR, SVM), **cross-validation E5b**, ma trận nhầm lẫn, thống kê corpus, **app demo**, video demo dự phòng | Các thành phần nhỏ của app, kiểm thử thủ công |

---

## 3. Bắt đầu ngay

### Vinh: hôm nay T6 02/10
1. **[V01]** Repo và CI đã xong; còn mời Việt Anh, Dương làm collaborator và bật bảo vệ nhánh `main`.
2. **[V02]** Gửi thầy các câu hỏi ở mục 8.
3. **[V03]** Gửi nhóm tin nhắn kế hoạch: link repo và link trang kế hoạch.

### Việt Anh: từ hôm nay T6 02/10
1. **[N01]** Đọc mục 0–3 của file này, phần của mình ở mục 5.3, và INTERFACE §1–§5, §7.8–§7.9, §8. **Hạn: tối nay 23:59.**
2. **[A01]** Tính tay TF-IDF và cosine trên 3 câu ngắn, ghi vào `notes/hand_calc.md`.
3. **[A02]** Viết 14 câu paraphrase và 10 câu ngoài kho vào `experiments/dev/queries_dev_vietanh.csv`, theo INTERFACE §8. **Không mở `queries_test.csv`.**

### Dương: từ hôm nay T6 02/10
1. **[D01]** Cài môi trường theo các bước ở mục 5.4. Gặp lỗi thì chụp màn hình gửi nhóm chat, Vinh hỗ trợ.
2. **[N01]** Đọc mục 0–3 của file này, phần của mình ở mục 5.4, và INTERFACE §1–§4, §6, §7.10, §8.
3. **[D02]** Viết 14 câu paraphrase và 10 câu ngoài kho vào `experiments/dev/queries_dev_duong.csv`, theo INTERFACE §8. **Không mở `queries_test.csv`.**

### Cả nhóm
- **[N02] Xác nhận qua nhóm chat, không họp: trước T7 03/10 10:00.** Nội dung cần nhắn ở mục 5.1.

---

## 4. Quy ước về hạn chót

- **Mọi hạn là 23:59 giờ Việt Nam**, trừ khi ghi giờ khác.
- **"Xong" nghĩa là:**
  - PR đã mở;
  - `pytest -q` (chạy ở gốc repo) xanh hoàn toàn và CI xanh;
  - đạt tiêu chí "xong" ghi trong việc.
- **Review:**
  - Vinh review PR của Việt Anh và Dương; Việt Anh review PR của Vinh.
  - **12 giờ** với PR nằm trên tiến độ chung (A03, A04, A05, V08); **24 giờ** với PR khác.
  - Người nhận góp ý sửa trong vòng 24 giờ.
  - Việc lớn mở **PR nháp sớm** để kịp 2 vòng góp ý trước hạn.
- **Thấy sắp trễ thì báo vào nhóm chat ít nhất 24 giờ trước hạn**, kèm lý do và ngày dự kiến xong.
- **⛔ Quá hạn cứng:** Vinh xử lý hoặc chuyển sang phương án dự phòng. Người phụ trách sau đó đọc lại phần đã sửa để giải thích được khi vấn đáp.
- **🏁 là mốc của cả nhóm.** Trễ mốc thì Vinh dời kế hoạch và báo cả nhóm qua chat.
- **Khi trễ, cắt việc theo thứ tự này:**
  1. bớt các biến thể trong E2;
  2. lưới α của E4, chỉ giữ α = 0.5;
  3. E7 BM25 (V13);
  4. `explain()` (A11) dời sang Final, phân tích lỗi làm bằng tay.

  **Không bao giờ cắt:** E0, E5, E6, E3b, phân tích câu ngoài kho, diễn tập.

---

## 5. Danh sách việc chi tiết

Mã việc đánh theo thứ tự thời gian: việc tiếp theo của mỗi người là số kế tiếp.

### 5.1 Cả nhóm (N)

| Mã | Việc | Hạn |
|---|---|---|
| N01 | Đọc phần của mình trong PLAN và INTERFACE (mục 3) | T6 02/10 |
| N02 | 🏁 **Xác nhận qua nhóm chat** (không họp), nội dung bên dưới | **T7 03/10 10:00** |
| N03 | Trinh sát buổi 10/10 (P01–P03): ghi câu thầy hỏi vào `notes/qa_bank.md` phần B; xem trang Language của thầy đã có nội dung chưa | CN 11/10 12:00 |
| N04 | Cập nhật tuần qua nhóm chat: việc đã xong, việc trễ, lịch bận tuần tới, điều rút ra từ buổi trinh sát | CN 11/10 21:00 |
| N05 | Trinh sát buổi 17/10 (P04–P06), ghi vào `qa_bank.md`; xem trang Language | CN 18/10 12:00 |
| N06 | 🏁 **Diễn tập lần 1**, mỗi người trình bày phần của mình | **CN 18/10 20:00** |
| N07 | **Diễn tập lần 2**, trình bày chéo (mỗi người trình bày phần của người khác) | **T4 21/10 20:00** |
| N08 | Mỗi người viết câu trả lời cho các câu được giao trong `qa_bank.md` phần A | T6 23/10 |
| N09 | Trinh sát buổi 24/10 (P07–P09), xem trang Language; cập nhật tuần qua nhóm chat | CN 25/10 21:00 |
| N10 | **Diễn tập lần 3**, có bấm giờ, có người đóng vai thầy hỏi vặn | **T4 28/10 20:00** |
| N11 | **Tổng duyệt** theo checklist ở mục 10 | **T6 30/10 20:00** |
| N12 | 🎯 **Thuyết trình Midterm** | **T7 31/10** |

**Nội dung xác nhận N02:** nhóm không họp kick-off. Mỗi người nhắn vào nhóm chat:
1. Đã đọc xong phần của mình.
2. **INTERFACE:** đồng ý, hoặc góp ý cụ thể. Góp ý được thì Vinh sửa qua PR.
3. **Hạn việc của mình đến 07/10:** xác nhận, hoặc đề xuất ngày khác kèm lý do.
4. **Lịch bận trong tháng 10:** môn khác, đi làm, thực tập, thi.

Ai cài môi trường bị lỗi thì gửi ảnh chụp màn hình vào nhóm chat.

### 5.2 Vinh (V)

| Mã | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| V01 | Tạo repo, push code, kiểm tra CI xanh *(đã xong)*; mời Việt Anh và Dương; bật bảo vệ nhánh `main` | **T5 01/10** | — |
| V02 | Gửi thầy các câu hỏi ở mục 8 | T6 02/10 | — |
| V03 | Gửi nhóm tin nhắn kế hoạch (link repo, link trang kế hoạch) | T6 02/10 | — |
| V04 | Tạo GitHub Issues **sau khi cả nhóm xác nhận (N02)**, theo hạn đã chốt; chỉ tạo cho việc có sản phẩm trong repo (khoảng 35 việc); cập nhật tuần và trinh sát giữ ở checklist | T7 03/10 12:00 | N02 |
| V05 | `make_auto_dev.py`: sinh `queries_dev_auto.csv` gồm 49 normal và 49 typo (INTERFACE §8) | T7 03/10 | — |
| V06 | Kiểm tra câu dev viết tay của Việt Anh và Dương: đúng định dạng, đúng tài liệu đích, câu ngoài kho thật sự ngoài kho | CN 04/10 18:00 | A02, D02 |
| V07 | `metrics.py` và `tests/test_metrics.py` | CN 04/10 | — |
| V08 | `evaluate.py`: đọc câu hỏi, `evaluate_run`, `summarize`, Balanced E2E, dòng lệnh | T3 06/10 | V07 |
| V09 | `baselines.py`: `JaccardRetriever`, `majority_intent`, `knn_intent` | T4 07/10 12:00 | A03 |
| V10 | 🏁 **Mốc 1:** chạy E0 và v1 trên tập dev, gửi bảng `summary.csv` vào nhóm chat | **T4 07/10** | V05, V08, V09, A05 |
| V11 | `run_ablation.py`: các nhóm thí nghiệm, `FROZEN_COMPARISONS`, batch tập test có khoá (INTERFACE §7.4, §7.8) | T6 09/10 | V08 |
| V12 | Chạy **E1, E2** | T7 10/10 | V11, A06 |
| V13 | `starter/bm25.py`: **BM25 tự viết** (cùng `rank`/`search` như `Retriever`, INTERFACE §5.5) và test; chạy **E7** trên tập dev | CN 11/10 | A03, V11 |
| V14 | Chạy **E5** (5 cách phân loại intent, full và LODO) | T2 12/10 | V11, D06 |
| V15 | **Chọn cấu hình theo 2 bước** (INTERFACE §7.5): chọn retrieval, rồi `sweep_threshold.py` và **E6**; chọn mô hình intent | T3 13/10 | V12, V14, A08 |
| V16 | Khung slide theo **dàn ý mục 1.9**: template, slide trống có tiêu đề, tên người phụ trách từng slide | T3 13/10 | — |
| V17 | 🏁 **Đóng băng:** PR đặt `DEFAULT_*_CONFIG` và `FROZEN_COMPARISONS`, Việt Anh duyệt, gắn tag `midterm-freeze` | **T4 14/10** ⛔ | V15, V13 |
| V18 | 🏁 **Chạy tập test một mẻ** (`run_ablation.py --split test --final`), gửi kết quả vào nhóm chat | **T5 15/10 21:00** ⛔ | V17 |
| V19 | Bảng và biểu đồ: theo loại câu, E3b, đường cong ngưỡng, ma trận nhầm lẫn; lưu vào `results/figures/` | T6 16/10 | V18, A09 |
| V20 | **Phân tích câu ngoài kho**: câu lọt ngưỡng và câu trong kho bị từ chối nhầm, ghi vào `notes/error_analysis.md` | T7 17/10 | V18 |
| V21 | Duyệt phân tích lỗi, slide và app demo của hai bạn (A12, A13, D05, D10, D11, D12) | CN 18/10 12:00 | — |
| V22 | Làm slide 1, 5–7, 14–15, 17–18, P6 và ghép slide v1 | CN 18/10 18:00 | V21 |
| V23 | Slide v2 theo góp ý của diễn tập lần 1 | T3 20/10 | N06 |
| V24 | 🏁 **Bản cuối:** `presentation.pdf` có số liệu khớp kết quả test, demo chạy ổn, push toàn bộ, gắn tag `midterm-submission` | **CN 25/10** ⛔ | — |
| V25 | Chuẩn bị checklist và chủ trì tổng duyệt N11 | T6 30/10 20:00 | — |
| V26 | Review PR của Việt Anh và Dương | 12 giờ / 24 giờ (mục 4) | — |

**Cách làm các việc chính của Vinh**

- **V05 `make_auto_dev.py`**
  - Đọc cột `expected_doc_id` của `queries_test.csv` để lấy 35 id cần loại; không đọc các cột khác.
  - Với 49 FAQ còn lại (sắp theo `id`), ghi 1 dòng `normal` và 1 dòng `typo`. Câu typo tạo bằng `_make_typo` nạp từ `scripts/generate_corpus.py` qua `importlib`, như sanity test của thầy đang làm.
- **V08 `evaluate.py`**
  - Viết theo INTERFACE §7.2–§7.4 và §7.7.
  - Trong lúc chờ Việt Anh, dùng một retriever giả: một class có `rank()` trả về tài liệu theo thứ tự cố định.
  - Với mỗi câu hỏi:
    - gọi `rank()` để lấy thứ hạng và điểm;
    - gọi `search(q, 3) == []` để biết có bị từ chối không;
    - lấy intent, tính các chỉ số, đo latency.
  - `summarize`: gom nhóm theo `type`, cộng một dòng tổng; Balanced E2E lấy trung bình theo 4 loại câu.
- **V15 chọn cấu hình:** làm đúng 3 bước của INTERFACE §7.5, ghi lại lý do từng lựa chọn vào `notes/selection.md`. Slide 15 và phụ lục P6 lấy từ file này.

### 5.3 Việt Anh (A)

| Mã | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| A01 | Tính tay TF-IDF và cosine trên 3 câu ngắn, ghi vào `notes/hand_calc.md` | T7 03/10 | — |
| A02 | 14 câu paraphrase và 10 câu ngoài kho (`queries_dev_vietanh.csv`, INTERFACE §8) | CN 04/10 12:00 | — |
| A03 | `preprocess.py` (`tokenize`, `STOPWORDS`) và test | **CN 04/10** | — |
| A04 | `Retriever` với `analyzer="word"` (`rank`, `search`), `tests/test_retrieval.py`, đối chiếu sklearn. PR nháp từ T2 05/10 | **T3 06/10 12:00** | A03 |
| A05 | Wiring `student_core.py`: khởi tạo lười (lazy), phương án dự phòng `top1_doc` khi chưa có intent | **T4 07/10 12:00** ⛔ | A04 |
| A06 | Các tuỳ chọn theo từ: `word_ngram_range`, `remove_stopwords`, `sublinear_tf`, `index_field` | T6 09/10 | A04 |
| A07 | `analyzer="char"` và `"hybrid"`, kèm test | CN 11/10 | A06 |
| A08 | Chạy **E3, E4** trên tập dev bằng `run_ablation.py --group E3/E4`. Ghi nhận xét: n-gram ký tự giúp câu paraphrase ở đâu, tách câu ngoài kho ra sao | T2 12/10 | A07, V11 |
| A09 | `noise_curve.py`: **E3b**, đường cong suy giảm theo 0–3 lỗi gõ (INTERFACE §7.9) | T3 13/10 | A07, V05 |
| A10 | Đọc CS50 W6 notes (Word Representation, word2vec, Attention, Transformers); viết so sánh lý thuyết TF-IDF với word2vec, Transformer, LLM vào `notes/theory_comparison.md` | T4 14/10 | — |
| A11 | `explain()` kèm test (tổng contribution bằng score) | T5 15/10 | A07 |
| A12 | Phân tích ít nhất 3 lỗi retrieval bằng `explain()`, ghi vào `notes/error_analysis.md` | T6 16/10 | A11, V18 |
| A13 | Slide 8, 9, 10, 12, phần retrieval của slide 16, phụ lục P1, P3, P5 | T7 17/10 | V16, A10 |
| A14 | Luyện phần trình bày, trả lời các câu được giao trong `qa_bank.md` | CN 25/10 | — |
| A15 | Review PR của Vinh | 12 giờ với V08, 24 giờ với PR khác | — |

**Cách làm A04 (TF-IDF và cosine tự viết)**
1. Tokenize mọi tài liệu theo `index_field` để lập bộ từ vựng, rồi đếm `df(t)` là số tài liệu chứa từ t.
2. Tính `idf(t) = ln((1 + N) / (1 + df(t))) + 1`, với N = 112. Đây là công thức mặc định của sklearn, dùng nó để đối chiếu được.
3. Vector tài liệu là `tf(t, d) · idf(t)`, rồi chuẩn hoá L2.
4. Vector câu hỏi tính cùng cách. Từ không có trong bộ từ vựng thì bỏ qua.
5. Vì hai vector đã chuẩn hoá, **cosine chính là tích vô hướng**. Sắp xếp theo score giảm dần; bằng điểm thì theo `id` tăng dần.
6. **Đối chiếu** với `TfidfVectorizer(tokenizer=tokenize, lowercase=False, token_pattern=None, smooth_idf=True, norm="l2")`. Cấu hình này đã kiểm chứng chạy được trên sklearn 1.5.2. Sai số phải dưới `1e-6`.
7. Test theo INTERFACE §5.4, rồi mở PR từ nhánh `vietanh/A04-retriever`.

### 5.4 Dương (D)

| Mã | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| D01 | Cài môi trường; `pytest` ra `15 passed, 2 deselected`; mở được app. *Hạn mềm: vướng thì nhắn nhóm chat* | T7 03/10 | V01 |
| D02 | 14 câu paraphrase và 10 câu ngoài kho (`queries_dev_duong.csv`, INTERFACE §8) | CN 04/10 12:00 | — |
| D03 | Đọc tài liệu **đợt 1** (danh sách bên dưới) | CN 04/10 | — |
| D04 | `intent.py`: `build_training_data`, `IntentClassifier` (NB + BoW), `tests/test_intent.py`. PR nháp T2 05/10 | **T3 06/10** · ⛔ **T5 08/10** | D03 |
| D05 | Thống kê corpus (`notebooks/corpus_stats.ipynb`): số tài liệu mỗi intent, độ dài trung bình, kích thước bộ từ vựng, 10 từ phổ biến nhất mỗi intent | T6 09/10 | — |
| D06 | Thêm `model="logreg"`, `model="svm"`, `features="tfidf"`, `include_descriptions`, kèm test (INTERFACE §6) | CN 11/10 | D04 |
| D07 | Đọc tài liệu **đợt 2** | CN 11/10 | — |
| D08 | `intent_cv.py`: **E5b**, 5-fold cross-validation (INTERFACE §7.10) | T2 12/10 | D06, A04, V09 |
| D09 | Ma trận nhầm lẫn 7×7 trên tập dev (`notebooks/intent_confusion.ipynb`) | T3 13/10 | V14 |
| D10 | **App demo tối thiểu** (sửa `starter/app.py`) | T5 15/10 | A05 |
| D11 | Phân tích ít nhất 2 lỗi intent, ghi vào `notes/error_analysis.md` | T6 16/10 | V18 |
| D12 | Slide 2, 3, 4, 11, 13, phần intent của slide 16, phụ lục P2, P4 | T7 17/10 | V16 |
| D13 | Quay video demo dự phòng 2–3 phút, đủ 4 loại câu | T5 22/10 | D10 |
| D14 | Luyện trình bày; tính tay được TF-IDF, Naive Bayes, MRR | CN 25/10 | — |

**Cách làm D01 (cài môi trường, Windows)**

1. Nếu máy chưa có Python 3.11: tải bộ cài **Python 3.11** từ python.org, khi cài **tick "Add python.exe to PATH"**.
2. Chạy trong PowerShell. **Không cần "kích hoạt" venv**, vì PowerShell mặc định chặn script `Activate.ps1`; gọi thẳng `python.exe` trong `.venv`:

```powershell
git clone <link-repo-nhóm>
cd <tên-repo>
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q        # phải ra: 15 passed, 2 deselected
.\.venv\Scripts\python.exe -m streamlit run starter/app.py
```

macOS/Linux: `python3.11 -m venv .venv`, rồi thay `.\.venv\Scripts\python.exe` bằng `.venv/bin/python`.

Gặp lỗi thì chụp màn hình và gửi vào nhóm chat.

**Tài liệu đọc**
- **Đợt 1 (D03, trước CN 04/10), đủ để làm D04:**
  1. [CS50 AI, Lecture 6 notes](https://cs50.harvard.edu/ai/notes/6/): phần *Bag-of-Words Model*, *Naive Bayes* (có additive smoothing).
  2. scikit-learn tutorial [Working With Text Data](https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html): `CountVectorizer`, `MultinomialNB`, `Pipeline`.
- **Đợt 2 (D07, trước CN 11/10), cho E5 và slide:**
  1. [CS50 AI, Lecture 2 notes](https://cs50.harvard.edu/ai/notes/2/): *Conditional Probability*, *Bayes' Rule*.
  2. [CS50 AI, Lecture 4 notes](https://cs50.harvard.edu/ai/notes/4/): *Nearest-Neighbor*, *Perceptron*, *Support Vector Machines*, *Overfitting*.
  3. Ghi chú của thầy: [Xác suất có điều kiện và Bayes](https://sharing.vinhnguyenthanh.com/courses/intro-ai/13-conditional-probability-bayes), [Supervised Learning](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning-supervised), [Evaluating Models](https://sharing.vinhnguyenthanh.com/courses/intro-ai/09-learning-evaluation) (nhất là §5 k-Fold).

**Cách làm D04**
1. Đọc kỹ INTERFACE §6.
2. **`build_training_data`:** duyệt danh sách tài liệu, bỏ các tài liệu có `id` nằm trong `exclude_ids`. Lấy `doc["text"]` làm text, `doc["intent"]` làm nhãn.
3. **`fit`:** *import sklearn bên trong hàm*. Tạo `Pipeline` gồm `CountVectorizer(ngram_range=...)` và `MultinomialNB(alpha=nb_alpha)`, gọi `.fit(texts, labels)`, lưu lại, rồi `return self`.
4. **`predict_proba`:**
   - Chưa `fit` thì raise `RuntimeError`.
   - Lấy kết quả `pipeline.predict_proba([query])[0]`, ghép với `pipeline.classes_` để tạo dict. `classes_` xếp theo bảng chữ cái, không theo thứ tự `INTENTS`.
   - Đảm bảo dict **có đủ 7 intent**; intent nào thiếu thì gán 0.
5. **`predict`:** lấy intent có xác suất lớn nhất.
6. Viết `tests/test_intent.py` theo đủ 5 ý ở INTERFACE §6.1.
7. Chạy `pytest`, rồi mở PR từ nhánh `duong/D04-intent-nb`. Vinh review trong 24 giờ.

**Cách làm D10 (app demo)**
1. Đọc `starter/app.py` hiện có để hiểu cấu trúc.
2. Thêm ô nhập câu hỏi (`st.text_input`) và nút hỏi.
3. Gọi `classify_intent` và `retrieve` từ `student_core`.
4. Hiển thị:
   - nhãn intent kèm phần trăm độ tin cậy;
   - mỗi tài liệu tìm được là một khung gồm câu hỏi/tiêu đề, câu trả lời, nguồn (`faq.json` hay `notices.json`) và score.
5. Khi `retrieve` trả về `[]`, hiện thông báo *"Information not found — please contact the administrative office"*.
6. Thử đủ 4 loại câu, rồi mở PR. Được nhờ AI hỗ trợ viết giao diện vì đây không phải phần lõi.

---

## 6. Lịch theo ngày

| Ngày | Hạn chót và sự kiện |
|---|---|
| **T5 01/10** | V01 |
| **T6 02/10** | V02 · V03 · N01 |
| **T7 03/10** | 🏁 **N02: xác nhận qua nhóm chat (10:00)** · V04 (12:00) · V05 · A01 · D01 |
| **CN 04/10** | A02, D02 (12:00) · V06 (18:00) · V07 · A03 · D03 |
| T2 05/10 | *PR nháp của A04 và D04* |
| **T3 06/10** | A04 (12:00) · V08 · D04 |
| **T4 07/10** | V09, A05 (12:00) · 🏁 **V10: Mốc 1, chạy được toàn bộ pipeline** |
| T5 08/10 | ⛔ D04 hạn cứng |
| T6 09/10 | V11 · A06 · D05 |
| **T7 10/10** | 👀 Trinh sát P01–P03 · V12 (E1, E2) |
| **CN 11/10** | N03 (12:00) · V13 (BM25, E7) · A07 · D06 · D07 · N04 cập nhật tuần qua chat (21:00) |
| T2 12/10 | V14 (E5) · A08 (E3, E4) · D08 (E5b) |
| T3 13/10 | V15 (chọn cấu hình, E6) · V16 · A09 (E3b) · D09 |
| **T4 14/10** | 🏁 ⛔ **V17: đóng băng** · A10 |
| **T5 15/10** | 🏁 ⛔ **V18: chạy tập test lúc 21:00** · A11 · D10 |
| T6 16/10 | V19 · A12 · D11 |
| **T7 17/10** | 👀 Trinh sát P04–P06 · V20 · A13 · D12 |
| **CN 18/10** | N05, V21 (12:00) · V22 (18:00) · **N06 diễn tập lần 1 (20:00)** |
| T3 20/10 | V23 |
| **T4 21/10** | **N07 diễn tập lần 2 (20:00)** |
| T5 22/10 | D13 |
| T6 23/10 | N08 |
| **T7 24/10** | 👀 Trinh sát P07–P09 |
| **CN 25/10** | 🏁 ⛔ **V24: bản cuối, tag `midterm-submission`** · A14 · D14 · N09 (21:00) |
| T4 28/10 | **N10 diễn tập lần 3 (20:00)** |
| T6 30/10 | **N11 tổng duyệt, V25 chủ trì (20:00)** |
| **T7 31/10** | 🎯 **N12: THUYẾT TRÌNH MIDTERM** |

---

## 7. Cách làm việc

- **Báo tiến độ hằng ngày trước 22:00**, qua nhóm chat, mỗi người 3 dòng: *đã xong · đang làm · vướng gì*.
- **Không họp định kỳ.** Mỗi Chủ nhật 21:00, mỗi người cập nhật tuần qua nhóm chat: việc đã xong, việc trễ, lịch bận tuần tới, điều rút ra từ buổi trinh sát. Chỉ các buổi diễn tập thuyết trình (N06, N07, N10, N11) mới cần gặp, online hoặc trực tiếp.
- **Git:** theo INTERFACE §9. Mỗi việc một nhánh; tên PR bắt đầu bằng mã việc, ví dụ `A04: word-level retriever`. Không push thẳng `main`.
- **CI:** GitHub Actions tự chạy pytest cho mọi PR. PR đỏ thì chưa review.
- **Review:** Vinh duyệt toàn bộ bài của Việt Anh và Dương, gồm code, phân tích lỗi, slide và app demo. Việt Anh duyệt PR của Vinh. Thời hạn xem mục 4.
- **Tập test:**
  - Việt Anh và Dương không mở `queries_test.csv` trước 15/10.
  - Vinh không viết câu dev loại paraphrase và ngoài kho.
  - Mọi việc tinh chỉnh chỉ làm trên tập dev; tập test chỉ chạy một mẻ vào 15/10. Sau đóng băng vẫn được thêm phân tích, nhưng không được đổi tham số.
- **AI:**
  - Không dùng LLM trong code chạy.
  - Phần lõi (`retrieval.py`, `intent.py`) phải tự viết.
  - Có thể nhờ AI hỗ trợ ở phần không phải lõi (script đánh giá, biểu đồ, app), theo đúng quy định của môn.
- **Trinh sát thứ Bảy:**
  - Ghi câu thầy hỏi, thời lượng mỗi nhóm, phần được khen, phần bị chê.
  - Xem trang [Language](https://sharing.vinhnguyenthanh.com/courses/intro-ai/20-language) của thầy đã có nội dung chưa; có thì đồng bộ thuật ngữ trên slide.
  - Chú ý **P10 Ticket Router**, nhóm thuyết trình cùng buổi 31/10 và dùng kỹ thuật gần giống nhóm mình. Câu trả lời cho "khác gì P10?": P10 chỉ **phân loại**, còn P12 **truy hồi tài liệu, xếp hạng và biết từ chối**.

---

## 8. Câu hỏi cho thầy (V02)

1. Thứ tự thuyết trình có đúng theo số topic không? P12 có chắc là thứ Bảy 31/10?
2. Mỗi nhóm có bao nhiêu phút, chia giữa thuyết trình và hỏi đáp thế nào? Có template slide không? Slide viết tiếng Anh hay tiếng Việt?
3. Midterm có phải nộp code, script, `presentation.pdf` lên hệ thống trước không? Hạn lúc nào? *(Nếu trước 31/10 thì dời V24 lên sớm hơn.)*
4. Nhóm bỏ qua 2 test stub bằng `pytest.ini` thay vì sửa file test có được không?
5. Có được dùng mô hình embedding chạy local không?
6. Hạn nộp Final là khi nào? Báo cáo IEEE viết bằng tiếng Anh hay tiếng Việt?

---

## 9. Rủi ro

| Rủi ro | Cách phòng |
|---|---|
| D04 trễ hạn | Không chặn ai: A05 có phương án dự phòng `top1_doc`. PR nháp T2 05/10; hạn cứng T5 08/10, quá hạn thì Vinh xử lý |
| A04 trễ hạn, chặn Mốc 1 | PR nháp từ T2 05/10, review trong 12 giờ; nếu vẫn trễ, tạm dùng `TfidfVectorizer` của sklearn (đề bài cho phép) để không chặn Mốc 1, bản tự viết thay vào sau |
| Vinh quá tải, là điểm nghẽn | E3, E3b, E4 do Việt Anh chạy; app demo do Dương làm; CI giảm việc review; Việt Anh hiểu `evaluate.py` qua việc review V08 |
| Lộ tập test | Việt Anh và Dương không mở `queries_test.csv`; Vinh không viết câu paraphrase và ngoài kho cho tập dev |
| Ngưỡng chọn trên tập dev không hợp với tập test | Tập dev có 20 câu ngoài kho đủ hai kiểu; Balanced E2E lấy trung bình theo loại; báo cáo trung thực nếu lệch |
| Điểm câu `normal` cao ảo | Báo cáo thêm Intent Acc (LODO) và giải thích trên slide |
| Kết quả so sánh nhiễu vì mẫu nhỏ | Ghi số câu (31/35) thay vì chỉ phần trăm; E5b cross-validation; các phương pháp so sánh cũng chấm trên tập test trong cùng mẻ |
| Lần chạy test hỏng giữa chừng | `LOCK` chỉ ghi khi chạy xong; được chạy lại có lý do nếu là bug code đánh giá |
| Demo hỏng khi lên lớp | Tổng duyệt trên đúng laptop, tắt mạng; video dự phòng D13; `presentation.pdf` để sẵn trên USB |
| Có thành viên vắng ngày thuyết trình | Diễn tập chéo N07: ai cũng trình bày được phần của người khác |

---

## 10. Checklist tổng duyệt (N11, T6 30/10)

- [ ] Laptop trình bày: `.venv` chạy được, app mở được **khi đã tắt mạng**
- [ ] Demo nhanh (slide 4) và demo câu khó (slide 17) có câu chuẩn bị sẵn, cộng thêm sẵn sàng nhận câu thầy tự gõ
- [ ] `presentation.pdf` có trên laptop và trên USB; video D13 mở sẵn
- [ ] Số liệu trên slide khớp `experiments/results/test/*/summary.csv`
- [ ] Mỗi người trả lời trôi chảy các câu trong `notes/qa_bank.md`
- [ ] Thuyết trình vừa thời lượng thầy quy định (đo ở N10); biết slide nào sẽ bỏ nếu thiếu giờ
- [ ] Repo có tag `midterm-submission`

---

## 11. Final (sơ bộ, chi tiết hoá khi có hạn nộp)

Final là đóng gói thành app hoàn chỉnh và nộp `report.pdf` theo định dạng IEEE.

| Người | Việc |
|---|---|
| **Vinh** | App Streamlit phát triển từ bản demo D10, gồm: ô hỏi, nhãn intent kèm %, thẻ top-k có ghi nguồn và score, thanh chỉnh ngưỡng, banner *"Information not found — please contact the administrative office"*, tab Evaluation dashboard. Lưu ý: `retrieve()` không nhận ngưỡng, nên thanh chỉnh ngưỡng phải dùng `Retriever` trực tiếp |
| **Việt Anh** | Báo cáo IEEE; đưa `explain()` lên giao diện (tô đậm từ khoá); test tự động cho đầu vào dị |
| **Dương** | Nhãn intent, câu hỏi mẫu, trình duyệt tài liệu; kiểm thử thủ công |
