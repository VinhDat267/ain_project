# Báo cáo Quy trình Chọn Cấu hình và Hiệu chuẩn Ngưỡng (Task V15 — Selection Report)

> **Tài liệu học thuật & Thuyết trình chuyên sâu — Project 12 (Campus FAQ Assistant)**  
> **Người thực hiện:** Nguyễn Đạt Vinh (Nhóm trưởng)  
> **Lịch sử tích hợp:** Chuẩn hóa theo `notes/midterm_integration.md` và nghiên cứu thuật toán nhóm (`Project12_Nghien_cuu_thuat_toan.md` mục 12).

---

## 1. Nguyên tắc Chọn Cấu hình và Nguồn gốc Thuật toán (Integration & Historical Truth)

Căn cứ biên bản làm việc nhóm ngày 02/11/2026 (`notes/midterm_integration.md`), kiến trúc giải pháp chính thức của Project 12 được tích hợp từ thuật toán hoàn chỉnh trong mục 12 của `Project12_Nghien_cuu_thuat_toan.md`, không chọn lại cấu hình hay cherry-pick ngưỡng từ tập kiểm thử:

1. **Biểu diễn truy hồi (Retrieval Engine):**
   - Bộ trích xuất `char_wb (3, 5)` với ranh giới từ và giữ dấu câu theo chuẩn scikit-learn.
   - Trọng số TF dưới dạng log phi tuyến (Sublinear Term Frequency: $1 + \ln(tf)$ khi $tf > 0$, ngược lại $0$).
   - Nghịch đảo tần suất văn bản mượt (Smooth IDF): $\text{IDF} = \ln\left(\frac{1 + N}{1 + df}\right) + 1.0$.
   - Chuẩn hóa vector văn bản và truy vấn lên mặt cầu đơn vị qua $L_2$-norm.
   - Ngưỡng cosine cơ sở $T_{\text{sim}} = 0.15$.

2. **Bộ phân loại ý định (Supervised Intent Classifier):**
   - Mô hình **Multinomial Logistic Regression** ($C = 10$, penalty $L_2$, max_iter = 2000) trên vector TF-IDF sublinear cấp độ từ.
   - Tập dữ liệu huấn luyện mở rộng: 112 text toàn văn + 112 tiêu đề/câu hỏi + 7 mô tả nghiệp vụ = **231 mẫu huấn luyện**.
   - Ngưỡng tin cậy hậu nghiệm (posterior probability gate) $T_{\text{intent}} = 0.34$.

3. **Cơ chế kiểm chứng độc lập và Sweep Ngưỡng (E6):**
   - Script `experiments/sweep_threshold.py` (E6) kiểm chứng độ nhạy 1 chiều của ngưỡng tương đồng $T_{\text{sim}}$ trên dải $[0.10, 0.45]$, xác nhận điểm cắt $T_{\text{sim}} = 0.15$ mang lại sự cân bằng tối ưu giữa việc giữ lại các câu paraphrase ngắn và loại bỏ văn bản không trùng khớp.
   - Kết quả đo lường trên 120 câu hỏi của `data/queries_test.csv` (Full MRR: 0.943, Intent Accuracy: 97.1%, E2E: 90.0%) là **Fixed-Configuration Benchmark (đã được khảo sát và ghi nhận trong quá trình tích hợp thuật toán mẫu)**, không gắn nhãn sai lệch là kết quả blind test hay k-fold CV.
   - Năng lực tổng quát hóa độc lập (unseen generalizability) của mô hình phân loại được bảo chứng qua 5-Fold Stratified Cross-Validation (`experiments/results/dev/intent_cv.csv`), đạt độ chính xác $87.63\% \pm 7.37\%$ và Macro-F1 $87.19\% \pm 8.49\%$.

---

## 2. Dữ liệu Đối chiếu Thực nghiệm trên Tập Phát triển (Dev Set 146 câu)

### A. Khảo sát Biểu diễn Truy hồi (E1 — E4, E7)

| Nhóm | Cấu hình | MRR Normal | MRR Para | MRR Typo | Mean (Para+Typo) | Ghi chú & Đánh giá |
|---|---|:---:|:---:|:---:|:---:|---|
| **E0** | `baseline_jaccard` | 1.000 | 0.247 | 0.990 | 0.619 | Mức sàn cơ bản (token overlap) |
| **E1** | `word_text` | 0.980 | 0.244 | 0.990 | 0.617 | Lập chỉ mục `text = question + answer` |
| **E1** | `word_question` | 1.000 | 0.106 | 1.000 | 0.553 | Chỉ mục ngắn làm tụt điểm paraphrase (-57%) |
| **E2** | `sublinear_tf` | 1.000 | 0.260 | 0.990 | 0.625 | Nén log TF giúp tăng mạnh câu paraphrase |
| **E3** | `char_3_5` | 0.986 | 0.258 | 0.990 | 0.624 | N-gram ký tự thuần túy không ranh giới từ |
| **E3** | **`char_wb_3_5`** | **1.000** | **0.299** | **1.000** | **0.650** | Đạt điểm tuyệt đối 1.000 trên Normal & Typo |
| **E3** | `char_wb_2_4` | 1.000 | 0.344 | 1.000 | **0.672** | N-gram ngắn nhạy cảm hơn với paraphrase ngắn |
| **E4** | `hybrid_0.5` | 0.986 | 0.267 | 0.980 | 0.623 | Kết hợp tuyến tính không vượt trội char_wb |
| **E7** | `bm25` | 1.000 | 0.270 | 1.000 | 0.635 | Nhỉnh hơn word TF-IDF nhưng điểm không bị chặn [0, 1] |

*Ghi chú (20/11): mọi dòng trên được chạy lại trên cùng 146 câu dev (`run_ablation.py --split dev --group …`). Bản trước lấy E0/E1/E2/E7 từ các run 18/10 chỉ có 122 câu, nên không so sánh được với E3/E4.*

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

---

### C. Quét Ngưỡng và Bào mòn Cổng Kép (Ablation Analysis)

Dữ liệu bào mòn trên 120 câu hỏi benchmark (`midterm-sample/ablation.csv`):

| Quy tắc Cổng (Ablation Rule) | $T_{\text{sim}}$ | $T_{\text{intent}}$ | Số câu đúng | Số câu OOC bị chặn | Tỷ lệ chặn OOC |
|---|:---:|:---:|:---:|:---:|:---:|
| Không dùng cổng (`no_gate`) | None | None | 95 / 120 | 0 / 15 | 0.0% |
| Chỉ dùng Cosine (`cosine_only`) | 0.15 | None | 96 / 120 | 1 / 15 | 6.7% |
| Chỉ dùng Intent (`intent_only`) | None | 0.34 | 108 / 120 | 15 / 15 | 100.0% |
| **Cổng kép kết hợp (`dual_gate`)** | **0.15** | **0.34** | **108 / 120** | **15 / 15** | **100.0%** |

**Nhận định kiến trúc:**
- Cổng Cosine đơn lẻ không đủ khả năng chặn câu OOC chứa từ khóa khuôn viên trường (14/15 câu OOC vượt qua $0.15$).
- Cổng Intent đóng vai trò bộ lọc an toàn tối quan trọng: san phẳng phân phối xác suất đối với câu lạ và kích hoạt từ chối an toàn.
- Ngưỡng kép $(T_{\text{sim}}=0.15, T_{\text{intent}}=0.34)$ là chốt chặn cân bằng hoàn hảo cho môi trường hành chính đại học.
