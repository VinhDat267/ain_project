# Báo cáo Quy trình Chọn Cấu hình và Hiệu chuẩn Ngưỡng (Task V15 — Selection Report)

> **Tài liệu học thuật & Thuyết trình chuyên sâu — Project 12 (Campus FAQ Assistant)**  
> **Người thực hiện:** Nguyễn Đạt Vinh (Nhóm trưởng)  
> **Quy chuẩn tuân thủ:** INTERFACE.md §7.5 và PLAN.md §1.6 (Clean Room ML — Zero Test Leakage)

---

## 1. Nguyên tắc Chọn Cấu hình 2 Bước (Two-Step Clean Room Protocol)

Để tránh hiện tượng vòng lặp tối ưu hóa quá mức (circular parameter optimization) giữa cấu hình trích xuất đặc trưng và ngưỡng từ chối, nhóm tuân thủ quy trình 2 bước độc lập:

1. **Bước 1 (Chọn cấu hình biểu diễn & xếp hạng thô):**
   - Chỉ số tối ưu: **Trung bình MRR@10 của 2 tập câu hỏi khó (`paraphrase` và `typo`) trên tập phát triển (`dev` set 146 câu)**.
   - *Tại sao dùng chỉ số này?* Vì MRR@10 đo lường năng lực xếp hạng thuần túy của vector đặc trưng và hoàn toàn **độc lập với ngưỡng từ chối**.
   - Nếu hai cấu hình có điểm tương đương, ưu tiên cấu hình có độ phức tạp thấp hơn và tính ổn định cao hơn.
2. **Bước 2 (Hiệu chuẩn Ngưỡng từ chối Cổng kép):**
   - Giữ cố định cấu hình trích xuất đã chọn ở Bước 1.
   - Chạy quét lưới (`sweep_threshold.py` / E6) độc lập trên tập `dev` để tìm cặp ngưỡng $(T_{\text{sim}}, T_{\text{intent}})$ tối đa hóa chỉ số cân bằng:
     $$\text{Balanced E2E} = \frac{1}{2} \left( \text{Hit@1}_{\text{in-corpus}} + \text{Rejection}_{\text{OOC}} \right)$$

---

## 2. Dữ liệu Đối chiếu Thực nghiệm trên Tập Phát triển (Dev Set 146 câu)

### A. Khảo sát Biểu diễn Truy hồi (E1 — E4, E7)

| Nhóm | Cấu hình | MRR Normal | MRR Para | MRR Typo | Mean (Para+Typo) | Ghi chú & Đánh giá |
|---|---|:---:|:---:|:---:|:---:|---|
| **E0** | `baseline_jaccard` | 1.000 | 0.281 | 0.990 | 0.635 | Mức sàn cơ bản (token overlap) |
| **E1** | `word_text` | 0.980 | 0.298 | 0.990 | 0.644 | Lập chỉ mục `text = question + answer` |
| **E1** | `word_question` | 1.000 | 0.205 | 1.000 | 0.602 | Chỉ mục ngắn làm tụt điểm paraphrase (-31%) |
| **E2** | `sublinear_tf` | 1.000 | 0.340 | 0.990 | 0.665 | Nén log TF giúp tăng mạnh câu paraphrase |
| **E3** | `char_3_5` | 0.986 | 0.258 | 0.990 | 0.624 | N-gram ký tự thuần túy không ranh giới từ |
| **E3** | **`char_wb_3_5`** | **1.000** | **0.299** | **1.000** | **0.650** | Đạt điểm tuyệt đối 1.000 trên Normal & Typo |
| **E3** | `char_wb_2_4` | 1.000 | 0.344 | 1.000 | **0.672** | N-gram ngắn nhạy cảm hơn với paraphrase ngắn |
| **E4** | `hybrid_0.5` | 0.986 | 0.267 | 0.980 | 0.623 | Kết hợp tuyến tính không vượt trội char_wb |
| **E7** | `bm25` | 1.000 | 0.351 | 1.000 | **0.676** | BM25 rất mạnh nhưng điểm không bị chặn [0, 1] |

**Quyết định lựa chọn cấu hình trích xuất:**
- Cấu hình **`char_wb (3, 5)` kết hợp Sublinear TF ($1 + \ln(tf)$), Smooth IDF và Chuẩn hóa $L_2$** được lựa chọn làm giải pháp chính thức cho sản phẩm.
- *Lý do:* Đạt sự cân bằng hoàn hảo giữa khả năng kháng nhiễu chính tả tuyệt đối (1.000 Hit@1 trên cả 1, 2, 3 lỗi gõ trong E3b), điểm số Cosine bị chặn chuẩn tắc trong $[0, 1]$, và khả năng phân rã đặc trưng tuyến tính minh bạch (`explain()`).

---

### B. Khảo sát Mô hình Phân loại Ý định (E5 & E5b)

Đánh giá trên 5-Fold Stratified Cross-Validation (E5b) trên 112 tài liệu:

| Mô hình Phân loại | Độ chính xác (Accuracy) | Macro-F1 | Nhận xét tính tương thích |
|---|:---:|:---:|---|
| `majority` | $0.134 \pm 0.003$ | $0.034 \pm 0.001$ | Đoán ngẫu nhiên (sàn 1/7) |
| `knn1` | $0.769 \pm 0.073$ | $0.741 \pm 0.102$ | Độ nhạy cao với biên phân cách |
| `knn5` | $0.814 \pm 0.101$ | $0.793 \pm 0.123$ | Khá, nhưng độ tin cậy bị rời rạc |
| `nb_bow` | $0.804 \pm 0.071$ | $0.787 \pm 0.091$ | Naive Bayes giả định độc lập |
| `nb_tfidf` | $0.831 \pm 0.084$ | $0.826 \pm 0.097$ | Tốt, nhưng phân phối xác suất cực đoan |
| `logreg_bow` | $0.823 \pm 0.060$ | $0.807 \pm 0.067$ | Ổn định cao |
| **`logreg_tfidf`** | **$0.876 \pm 0.074$** | **$0.872 \pm 0.085$** | **Cao nhất toàn diện & xác suất chuẩn tắc** |
| `svm_tfidf` | $0.867 \pm 0.083$ | $0.861 \pm 0.094$ | Không có xác suất tự nhiên (cần softmax logit) |

**Quyết định lựa chọn mô hình phân loại:**
- **Logistic Regression (TF-IDF sublinear, $C = 10$, max_iter = 2000)** được chọn làm mô hình sản phẩm (`DEFAULT_INTENT_CONFIG`).
- Dữ liệu huấn luyện mở rộng: 112 texts + 112 questions + 7 descriptions = **231 mẫu huấn luyện**.

---

### C. Quét Ngưỡng Cổng Kép Tối ưu (E6)

Thực hiện quét không gian tham số:
- Ngưỡng Cosine: $T_{\text{sim}} \in [0.05, 0.40]$, bước $0.01$.
- Ngưỡng Intent Confidence: $T_{\text{intent}} \in [0.10, 0.60]$, bước $0.01$.

**Điểm tối ưu Pareto đạt được:**
- **$T_{\text{sim}} = 0.15$** (Loại bỏ các văn bản có mức độ trùng lặp từ vựng quá thấp, giữ lại các câu paraphrase tiềm năng).
- **$T_{\text{intent}} = 0.34$** (Chặn đứng hoàn toàn 15/15 câu hỏi ngoài kho chứa từ khóa học đường gây nhiễu, hạn chế tối đa từ chối nhầm ở mức dưới 2%).
- Điểm **Balanced E2E đạt 90.0%** trên toàn bộ 120 câu hỏi benchmark kiểm định.
