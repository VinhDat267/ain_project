# Báo cáo Phân tích Lỗi và Cơ chế Phòng thủ Thực tế (Error Analysis & Failure Modes)

> **Tài liệu học thuật & Thuyết trình chuyên sâu — Project 12 (Campus FAQ Assistant)**  
> **Tác giả:** Nhóm đồ án Project 12 — Nguyễn Đạt Vinh (V20), Lương Việt Anh (A12), Nguyễn Ánh Dương (D11)  
> **Dữ liệu thực nghiệm:** Trích xuất trực tiếp từ `experiments/results/midterm-sample/per_query.csv`, `data/queries_test.csv`, và hàm `retriever.explain()`.

---

## 1. Tổng quan Kết quả Thực nghiệm và Phân loại Lỗi

Trên bộ 120 câu hỏi benchmark chuẩn (`data/queries_test.csv` gồm 105 câu trong kho và 15 câu ngoài kho), hệ thống đạt:
- **Full MRR:** `0.943`
- **Hit@1 (In-corpus):** `90.48% (95/105)`
- **Intent Accuracy:** `97.14% (102/105)`
- **OOC Rejection (Từ chối câu ngoài kho):** `100.0% (15/15)`
- **E2E Acc@1 (All):** `90.0% (108/120)` · **Balanced E2E:** `91.4%`

Toàn bộ **35 câu Normal** và **35 câu Typo** đều đạt **Hit@1 = 1.000 (35/35)** và **MRR = 1.000**. Mọi sai số xếp hạng và lỗi phân loại đều tập trung tại **35 câu Paraphrase** (12 ca sai/từ chối) và các câu hỏi ngoài kho tri thức (**Out-of-Corpus - OOC**).

---

## 2. Bảng Thống kê Toàn diện 12 Ca Lỗi Trong Kho (In-Corpus Error Registry)

Trong 105 câu hỏi trong kho, có đúng **12 ca** phát sinh sai sót hoặc từ chối (toàn bộ đều thuộc nhóm `paraphrase`):
- **10 ca Silent Wrong (Hit@1 = 0 nhưng không từ chối):** Trong đó **8/10 ca tài liệu đúng nằm ngay ở Rank 2 hoặc Rank 3 (`Hit@3 = 1`)**, được cứu trợ thành công khi giao diện hiển thị 3 thẻ kết quả. Chỉ có 2 ca (`q_026` và `q_056`) rơi khỏi Top 3.
- **2 ca False Abstention (Tài liệu đúng đạt Rank 1 nhưng bị Intent Gate chặn):** `q_064` và `q_066`.

| STT | Mã câu | Dạng lỗi | Câu hỏi thực tế (`data/queries_test.csv`) | Doc đích | Doc Top-1 trả về | Rank | Cosine | Intent Conf | Hit@3 |
|---|---|---|---|---|---|:---:|:---:|:---:|:---:|
| 1 | `q_017` | Silent Wrong (Top-3 rescued) | *"When does the graduation ceremony take place?"* | `faq_graduation_03` | `notice_graduation_01` | 3 | 0.3352 | 0.7497 | 1 |
| 2 | `q_026` | Silent Wrong (Rank > 3) | *"What's the process for signing up for courses at Hanoi University?"* | `faq_course_registration_01` | `faq_class_schedule_08` | 10 | 0.2608 | 0.5127 | 0 |
| 3 | `q_056` | Silent Wrong (Rank > 3) | *"How can I tell if my class times conflict with each other?"* | `faq_class_schedule_02` | `notice_exam_02` | 11 | 0.2849 | 0.3477 | 0 |
| 4 | `q_064` | **False Abstention** | *"Where do I go to see my current classes and times?"* | `faq_class_schedule_01` | `faq_class_schedule_01` | 1 | 0.2971 | **0.2534** | 1 |
| 5 | `q_065` | Silent Wrong (Top-3 rescued) | *"What are the consequences of paying my tuition bill late?"* | `faq_tuition_03` | `faq_tuition_02` | 2 | 0.1908 | 0.7372 | 1 |
| 6 | `q_066` | **False Abstention** | *"What should I do if the class section I need has no open seats?"* | `faq_course_registration_05` | `faq_course_registration_05` | 1 | 0.2021 | **0.3108** | 1 |
| 7 | `q_080` | Silent Wrong (Top-3 rescued) | *"Two of my finals overlap on the same day - who do I tell?"* | `faq_exam_02` | `faq_class_schedule_02` | 2 | 0.2682 | 0.3666 | 1 |
| 8 | `q_082` | Silent Wrong (Top-3 rescued) | *"If I drop every class this semester, how do refunds work?"* | `faq_tuition_06` | `notice_course_registration_02` | 2 | 0.2867 | 0.3401 | 1 |
| 9 | `q_104` | Silent Wrong (Top-3 rescued) | *"By when do I need to add or drop a class this fall?"* | `faq_course_registration_02` | `notice_course_registration_02` | 2 | 0.2135 | 0.5290 | 1 |
| 10 | `q_111` | Silent Wrong (Top-3 rescued) | *"My account has a registration hold - what does that mean and how do I remove it?"* | `faq_course_registration_09` | `faq_tuition_03` | 2 | 0.3055 | 0.3772 | 1 |
| 11 | `q_115` | Silent Wrong (Top-3 rescued) | *"What's the payment deadline for this semester's tuition?"* | `faq_tuition_01` | `notice_tuition_01` | 2 | 0.4381 | 0.9035 | 1 |
| 12 | `q_117` | Silent Wrong (Top-3 rescued) | *"My laptop won't join the campus Wi-Fi - what should I check?"* | `faq_technical_support_02` | `notice_technical_support_01` | 2 | 0.2052 | 0.9017 | 1 |

---

## 3. Bóc tách Đóng góp Đặc trưng qua `explain()` cho các Ca Lỗi Điển hình

### Lỗi 1: Truy vấn `q_056` — Lệch trọng số do từ hiếm có IDF cao
* **Câu hỏi:** `"How can I tell if my class times conflict with each other?"`
* **Tài liệu đích đúng:** `faq_class_schedule_02` (FAQ về trùng lịch học).
* **Tài liệu Top-1 hệ thống trả về:** `notice_exam_02` (Thông báo về xử lý trùng lịch thi).
* **Thứ hạng tài liệu đúng:** Rank 11 (Cosine: `0.1824` vs Top-1: `0.2849`).
* **Bóc tách đóng góp đặc trưng qua `retriever.explain()`:**
  - Đối với tài liệu đích đúng (`faq_class_schedule_02`): Các $n$-gram chỉ kích hoạt nhóm từ `"class"` với điểm đóng góp rất nhỏ (`' cla'`, `' clas'`, `'class'` đóng góp $\approx 0.0050$ mỗi feature).
  - Đối với tài liệu bị nhầm (`notice_exam_02`): Từ `"conflict"` xuất hiện trực tiếp trong thông báo thi với trọng số IDF cực cao. Chuỗi $n$-gram ký tự của `"conflict"` (`'ict '`, `'lict '`, `'confl'`, `'flic'`) đóng góp vượt trội ($> 0.018$ mỗi feature), khiến `notice_exam_02` chiếm ưu thế áp đảo.

### Lỗi 2: Truy vấn `q_111` — Giao thoa từ vựng liên chủ đề (Cross-topic Polysemy)
* **Câu hỏi:** `"My account has a registration hold - what does that mean and how do I remove it?"`
* **Tài liệu đích đúng:** `faq_course_registration_09` (Giải thích về lệnh chặn đăng ký học phần).
* **Tài liệu Top-1 hệ thống trả về:** `faq_tuition_03` (Chặn đăng ký do nợ học phí).
* **Thứ hạng tài liệu đúng:** Rank 2 (Score: `0.2982` vs Top-1: `0.3055`).
* **Bóc tách đóng góp:** Cả hai tài liệu đều chứa từ `"hold"`. Tuy nhiên trong `faq_tuition_03`, từ `"account"` đi kèm `"financial hold"` có tần suất lặp lại cao, giúp `faq_tuition_03` vượt lên với khoảng cách sít sao `0.0073`. Nhờ kiến trúc hiển thị Top-3 thẻ, người dùng vẫn đọc được `faq_course_registration_09` ngay tại thẻ số 2.

### Lỗi 3: Truy vấn `q_026` — Lỗ hổng từ vựng địa danh và diễn giải
* **Câu hỏi:** `"What's the process for signing up for courses at Hanoi University?"`
* **Tài liệu đích đúng:** `faq_course_registration_01` (Quy trình đăng ký môn học).
* **Tài liệu Top-1 hệ thống trả về:** `faq_class_schedule_08` (Thời khóa biểu theo ngành).
* **Thứ hạng tài liệu đúng:** Rank 10.
* **Bóc tách đóng góp:** Người dùng dùng cụm từ *"signing up for courses"* thay vì danh từ chuẩn hóa *"course registration"*. Do đó, các $n$-gram của từ `"registration"` không được kích hoạt. Ngược lại, $n$-gram của `"Hanoi University"` (`' univ'`, `'ersit'`, `'iver'`) lại trùng khớp ngẫu nhiên với phần chữ ký chân trang của `faq_class_schedule_08`.

---

## 4. Phân tích Cơ chế Cổng Kép và Câu Ngoài Kho (Out-of-Corpus — OOC)

### A. Tại sao cổng Cosine đơn lẻ thất bại trước câu OOC?
Tập benchmark có **15 câu ngoài kho (OOC)**. Trong đó, 14 câu chứa các từ vựng học đường đánh lừa cosine:
- `q_004`: *"What's the best restaurant near campus for vegan food?"* (chứa `"campus"`, top1 cosine: `0.2406`)
- `q_010`: *"Does the university offer a shuttle to the airport on weekends?"* (chứa `"university"`, top1 cosine: `0.2854`)
- `q_024`: *"Can I bring my dog to live with me in the dorm?"* (chứa `"dorm"`, top1 cosine: `0.2393`)
- `q_050`: *"What time does the campus coffee shop close on Fridays?"* (chứa `"campus"`, top1 cosine: `0.2811`)
- `q_086`: *"Can I rent a kayak from the campus recreation center?"* (chứa `"campus"`, `"center"`, top1 cosine: `0.3939`)

> [!WARNING]
> Điểm Cosine top-1 của 14/15 câu này đều dao động từ `0.16` đến `0.39`, **vượt qua ngưỡng Cosine $T_{\text{sim}} = 0.15$**. Nếu chỉ dùng cổng Cosine đơn lẻ (`cosine_only`), hệ thống chỉ chặn được đúng **1/15 câu OOC** (tỷ lệ rò rỉ thông tin sai lệch lên tới 93.3%!).
>
> *(Lưu ý câu `q_020` trong benchmark thực tế là câu typo trong kho `faq_student_services_03` với câu hỏi "What mental health support is avaliable on campus?", được hệ thống trả về đúng ở Rank 1 với cosine 0.4333).*

### B. Cổng Ý định (Intent Confidence Gate $\ge 0.34$) giải cứu hệ thống
Khi các câu OOC vượt qua cổng Cosine $0.15$, chúng bắt buộc phải vượt qua Cổng Ý định:
- Vì các thực thể chính (`"vegan restaurant"`, `"airport shuttle"`, `"dog in dorm"`, `"kayak"`) không nằm trong bất kỳ intent nào của 7 lớp nghiệp vụ, mô hình Logistic Regression san phẳng phân phối xác suất hậu nghiệm: mỗi lớp chỉ nhận xác suất phân tán $\approx 0.12 - 0.28$.
- Giá trị độ tin cậy cực đại $\max P(c \mid q) < 0.34$ (ví dụ: `q_004` đạt 0.3071, `q_010` đạt 0.2171, `q_024` đạt 0.2630), lập tức kích hoạt điều kiện từ chối:
  $$\text{Action} = \text{Abstain } ([])$$
- Nhờ cơ chế liên hiệp $(\text{Cosine} \ge 0.15 \land \text{Intent} \ge 0.34)$, hệ thống đạt **tỷ lệ chặn 100.0% (15/15 câu OOC)**.

---

## 5. Phân tích 2 Ca Từ chối nhầm (False Abstentions)

1. **Truy vấn `q_064`:** *"Where do I go to see my current classes and times?"*
   - Tài liệu đích đúng: `faq_class_schedule_01`.
   - Kết quả xếp hạng: **Rank 1 (Hit@1 = 1)**, Cosine: `0.2971` (vượt ngưỡng `0.15`).
   - Độ tin cậy Intent: `0.2534` (dưới ngưỡng `0.34`).
   - *Nguyên nhân:* Câu hỏi phân tán giữa `class_schedule` (0.253) và `course_registration` (0.241), khiến Intent Gate kích hoạt từ chối nhầm.
2. **Truy vấn `q_066`:** *"What should I do if the class section I need has no open seats?"*
   - Tài liệu đích đúng: `faq_course_registration_05`.
   - Kết quả xếp hạng: **Rank 1 (Hit@1 = 1)**, Cosine: `0.2021` (vượt ngưỡng `0.15`).
   - Độ tin cậy Intent: `0.3108` (tiệm cận ngưỡng `0.34` nhưng bị chặn).

> **Đánh đổi Nghiệp vụ:** Tỷ lệ từ chối nhầm $2/105 = 1.90\%$ là một cái giá rất nhỏ và hoàn toàn chấp nhận được để đổi lấy sự an toàn tuyệt đối ($0.0\%$ phát tán câu trả lời sai ngoài kho tri thức).
