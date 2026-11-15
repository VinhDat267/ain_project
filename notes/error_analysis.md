# Báo cáo Phân tích Lỗi và Cơ chế Phòng thủ Thực tế (Error Analysis & Failure Modes)

> **Tài liệu học thuật & Thuyết trình chuyên sâu — Project 12 (Campus FAQ Assistant)**  
> **Tác giả:** Nhóm đồ án Project 12 — Nguyễn Đạt Vinh (V20), Lương Việt Anh (A12), Nguyễn Ánh Dương (D11)  
> **Dữ liệu thực nghiệm:** Trích xuất trực tiếp từ `experiments/results/midterm-sample/per_query.csv`, `experiments/results/dev/noise_curve.csv`, và hàm `retriever.explain()`.

---

## 1. Tổng quan Kết quả Thực nghiệm và Phân loại Lỗi

Trên bộ 120 câu hỏi benchmark chuẩn (`data/queries_test.csv` gồm 105 câu trong kho và 15 câu ngoài kho), hệ thống đạt:
- **Full MRR:** `0.943`
- **Hit@1 (In-corpus):** `90.5% (95/105)`
- **Intent Accuracy:** `97.1% (102/105)`
- **OOC Rejection (Từ chối câu ngoài kho):** `100.0% (15/15)`
- **Balanced E2E:** `90.0% (108/120)`

Toàn bộ **35 câu Normal** và **35 câu Typo** đều đạt **Hit@1 = 1.000 (35/35)** và **MRR = 1.000**. Mọi sai số xếp hạng và lỗi phân loại đều tập trung tại **35 câu Paraphrase** và các câu hỏi ngoài kho tri thức (**Out-of-Corpus - OOC**).

---

## 2. Phân tích Chi tiết Lỗi Truy hồi Tài liệu bằng `explain()` (Việc A12 — Việt Anh)

Khi người dùng diễn giải lại câu hỏi bằng từ đồng nghĩa hoặc cấu trúc câu khác, các $n$-gram của từ khóa mục tiêu bị thay thế, dẫn đến hiện tượng trôi dạt đặc trưng (feature drift). Dưới đây là 3 trường hợp lỗi thực tế điển hình:

### Lỗi 1: Truy vấn `q_056` — Lệch trọng số do từ hiếm có IDF cao
* **Câu hỏi:** `"How can I tell if my class times conflict with each other?"`
* **Tài liệu đích đúng:** `faq_class_schedule_02` (FAQ về trùng lịch học).
* **Tài liệu Top-1 hệ thống trả về:** `notice_exam_02` (Thông báo về xử lý trùng lịch thi).
* **Thứ hạng tài liệu đúng:** Rank 11.
* **Bóc tách đóng góp đặc trưng qua `retriever.explain()`:**
  - Đối với tài liệu đích đúng (`faq_class_schedule_02`): Các $n$-gram chỉ kích hoạt nhóm từ `"class"` với điểm đóng góp rất nhỏ:
    - `' cla'`: `0.0050`
    - `' clas'`: `0.0050`
    - `'class'`: `0.0050`
  - Đối với tài liệu bị nhầm (`notice_exam_02`): Từ `"conflict"` xuất hiện trực tiếp trong thông báo thi với trọng số IDF cực cao. Chuỗi $n$-gram ký tự của `"conflict"` bùng nổ điểm số:
    - `'ict '`: `0.0182`
    - `'lict '`: `0.0182`
    - `'confl'`: `0.0131`
    - `'flic'`: `0.0131`
* **Kết luận:** Tài liệu `notice_exam_02` chiếm ưu thế áp đảo do từ `"conflict"` mang lượng thông tin đặc trưng (IDF) lớn hơn nhiều so với từ phổ biến `"class"`.

---

### Lỗi 2: Truy vấn `q_111` — Giao thoa từ vựng liên chủ đề (Cross-topic Polysemy)
* **Câu hỏi:** `"My account has a registration hold - what does that mean and how do I remove it?"`
* **Tài liệu đích đúng:** `faq_course_registration_09` (Giải thích về lệnh chặn đăng ký học phần).
* **Tài liệu Top-1 hệ thống trả về:** `faq_tuition_03` (Chặn đăng ký do nợ học phí).
* **Thứ hạng tài liệu đúng:** Rank 2 (Score: `0.298` vs Top-1: `0.306`).
* **Bóc tách đóng góp đặc trưng qua `retriever.explain()`:**
  - Cả hai tài liệu đều chứa từ `"hold"`.
  - Tuy nhiên, trong `faq_tuition_03`, cụm từ `"account"` được nhắc lại nhiều lần đi kèm với `"financial hold"`. Các $n$-gram của `"account"` (`'unt'`, `'accou'`, `'ccou'`) đóng góp thêm `0.0212`, giúp `faq_tuition_03` vượt lên tài liệu đúng với chênh lệch chỉ `0.008`.
* **Kết luận:** Mặc dù xếp rank 2, tài liệu đúng vẫn nằm trong Top-3 kết quả trả về (`Hit@3 = 1`), giúp người dùng vẫn tiếp cận được thông tin chính xác.

---

### Lỗi 3: Truy vấn `q_026` — Lỗ hổng từ vựng địa danh và diễn giải
* **Câu hỏi:** `"What's the process for signing up for courses at Hanoi University?"`
* **Tài liệu đích đúng:** `faq_course_registration_01` (Quy trình đăng ký môn học).
* **Tài liệu Top-1 hệ thống trả về:** `faq_class_schedule_08` (Thời khóa biểu theo ngành).
* **Thứ hạng tài liệu đúng:** Rank 10.
* **Bóc tách đóng góp đặc trưng:** Người dùng dùng cụm từ *"signing up for courses"* thay vì danh từ chuẩn hóa *"course registration"*. Do đó, các $n$-gram của từ `"registration"` hoàn toàn không được kích hoạt. Trong khi đó, các $n$-gram của `"Hanoi University"` (`' univ'`, `'ersit'`, `'iver'`) lại trùng khớp ngẫu nhiên với phần chân trang của `faq_class_schedule_08`.

---

## 3. Phân tích Lỗi Phân loại Ý định (Việc D11 — Dương)

Trong 105 câu hỏi trong kho, mô hình **Logistic Regression + TF-IDF** phân loại chính xác **102 câu (97.1%)**. Chỉ có duy nhất 3 câu bị phân loại nhầm, đều nằm ở nhóm Paraphrase:

| Mã câu | Câu hỏi người dùng | Nhãn đúng | Nhãn dự đoán | Độ tin cậy (Conf) | Phân tích nguyên nhân |
|---|---|:---:|:---:|:---:|---|
| `q_062` | *"Where can I find free tutoring if I'm behind in a class?"* | `student_services` | `class_schedule` | `0.437` | Từ `"class"` xuất hiện ở cuối câu làm tăng xác suất của nhóm lịch học; từ `"tutoring"` không có trong tập mô tả intent cơ bản. |
| `q_080` | *"Two of my finals overlap on the same day - who do I tell?"* | `exam` | `class_schedule` | `0.367` | Người dùng dùng từ lóng `"finals"` (thay vì `"final exam"`), kết hợp với các từ chỉ thời gian `"day"`, `"overlap"` khiến mô hình nghiêng về xung đột thời khóa biểu. |
| `q_082` | *"If I drop every class this semester, how do refunds work?"* | `tuition` | `course_registration` | `0.340` | Hành động `"drop every class"` kích hoạt mạnh các trọng số thuộc nhóm đăng ký/hủy môn học, làm phân tán xác suất của nhóm học phí hoàn trả (`refunds`). |

---

## 4. Phân tích Cơ chế Cổng Kép và Câu Ngoài Kho (Việc V20 — Vinh)

### A. Tại sao cổng Cosine đơn lẻ thất bại trước câu OOC?
Tập benchmark có **15 câu ngoài kho (OOC)**. Trong đó có tới **14 câu** cố tình chèn các từ vựng học đường:
- Ví dụ:
  - `q_004`: *"Is there a lost and found on campus for student IDs?"* (chứa `"campus"`, `"student"`, `"id"`)
  - `q_010`: *"Can I reserve a campus tennis court on weekends?"* (chứa `"campus"`)
  - `q_020`: *"Are dorm rooms co-ed at Hanoi University?"* (chứa `"dorm"`, `"university"`)
- **Hậu quả:** Điểm Cosine top-1 của 14 câu này đều dao động từ `0.16` đến `0.28`, **vượt qua ngưỡng Cosine $0.15$**. Nếu chỉ dùng cổng Cosine đơn lẻ (`cosine_only`), hệ thống chỉ chặn được đúng **1/15 câu OOC** (thất bại 93.3%!).

### B. Vai trò cứu tinh của Cổng Ý định (Intent Confidence Gate $\ge 0.34$)
Khi câu OOC lọt qua cổng Cosine, nó được đưa qua bộ phân loại ý định:
- Vì các từ khóa chính (`"tennis"`, `"kayak"`, `"lost and found"`, `"co-ed"`) không thuộc bất kỳ nhóm nghiệp vụ nào trong 7 intent, phân phối xác suất dự đoán bị san phẳng ra toàn bộ 7 lớp (mỗi lớp chỉ nhận $\approx 0.14 - 0.22$).
- Độ tin cậy cực đại $\max P(c \mid q) < 0.34$, lập tức kích hoạt điều kiện từ chối:
  $$\text{Action} = \text{Abstain } ([])$$
- Nhờ đó, hệ thống chặn đứng **15/15 câu OOC (100%)**, bảo vệ uy tín thông tin hành chính của nhà trường.

---

## 5. Phân tích 2 Câu trong kho bị Từ chối nhầm (False Abstentions)

Cơ chế phòng thủ nghiêm ngặt làm phát sinh **2 trường hợp bị từ chối nhầm** (tỷ lệ $2/105 = 1.90\%$):

1. **Truy vấn `q_064`:** *"Where do I go to see my current classes and times?"*
   - Tài liệu đích: `faq_class_schedule_01`.
   - Điểm Cosine: `0.297` (vượt ngưỡng `0.15`).
   - Độ tin cậy Intent: `0.253` (dưới ngưỡng `0.34`).
   - *Nguyên nhân:* Câu hỏi quá ngắn và từ ngữ phân tán giữa `class_schedule` (0.253) và `course_registration` (0.241), khiến Intent Gate kích hoạt từ chối nhầm.
2. **Truy vấn `q_066`:** *"What should I do if the class section I need has no open seats?"*
   - Tài liệu đích: `faq_course_registration_05`.
   - Điểm Cosine: `0.202` (vượt ngưỡng `0.15`).
   - Độ tin cậy Intent: `0.311` (tiệm cận ngưỡng `0.34` nhưng vẫn bị chặn).

> **Đánh giá đánh đổi (Trade-off Decision):**
> Trong nghiệp vụ hành chính đại học, việc chấp nhận từ chối nhầm **1.9%** câu hỏi mập mờ để đổi lấy **100% khả năng miễn nhiễm trước câu hỏi rác và ảo giác** là một quyết định kiến trúc hoàn toàn đúng đắn và chuẩn mực.
