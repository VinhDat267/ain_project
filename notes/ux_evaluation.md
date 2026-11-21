# Đánh giá Trải nghiệm Người dùng, Khả năng Tiếp cận WCAG 2.2 AA & Thiết kế Giao diện Sinh viên

> **Báo cáo Chuyên sâu UX / UI & Khả năng Tiếp cận — Project 12 (Campus FAQ Assistant)**  
> **Chuyên gia phụ trách:** `agency-ux-architect` & `agency-accessibility-auditor`  
> **Phương pháp luận:** **Expert Heuristic Walkthrough** (dựa trên 10 Nguyên tắc Nielsen) kết hợp **WCAG 2.2 Level AA Technical Audit** và **Cognitive Walkthrough cho 3 Persona Sinh viên**.  
> *(Ghi chú học thuật: Báo cáo tuân thủ nguyên tắc trung thực học thuật tuyệt đối; không ngụy tạo kết quả khảo sát người dùng thực nghiệm khi chưa tổ chức user test trên diện rộng).*

---

## 1. Bảng Kiểm kê 14 Vấn đề Trải nghiệm Người dùng (UX Issue Audit: U1 → U14)

Thang điểm mức độ nghiêm trọng (Nielsen Severity Scale):
- **0 = Không có vấn đề (Cosmetic)**
- **1 = Nhẹ (Low):** Gây phiền toái nhỏ, không cản trở hoàn thành tác vụ.
- **2 = Trung bình (Medium):** Gây chậm trễ hoặc bối rối cho người dùng phổ thông.
- **3 = Nghiêm trọng (High):** Người dùng có thể bỏ dở tác vụ hoặc hiểu sai thông tin quan trọng.
- **4 = Thảm họa (Catastrophic):** Phá vỡ luồng người dùng hoặc vi phạm tính toàn vẹn của hệ thống.

| Mã | Vấn đề UX Phát hiện | Nguyên tắc Nielsen & WCAG | Mức độ | Giải pháp Kỹ thuật & Hiện thực hóa Mã nguồn |
|---|---|---|:---:|---|
| **U1** | Ô nhập câu hỏi không kích hoạt tìm kiếm khi nhấn Enter; nhãn thiếu hướng dẫn trực quan | Nielsen #7: Flexibility & Efficiency of Use | **Severity 2** | Hỗ trợ bắt sự kiện Enter tự nhiên từ `st.text_input` kết hợp nút bấm; cập nhật placeholder gợi ý ví dụ thực tế. |
| **U2** | Hiện tượng mâu thuẫn thị giác khi từ chối: hộp xanh `st.success` hiển thị cùng lúc với hộp đỏ `st.error` | Nielsen #1: Visibility of System Status; Nielsen #4: Consistency | **Severity 3** | Tái cấu trúc luồng logic: Khi `abstained == True`, **tuyệt đối không hiển thị `st.success`**, chỉ hiển thị `st.error` chuẩn. |
| **U3** | Hộp thông báo từ chối cộc lốc, không hướng dẫn bước tiếp theo khi sinh viên bế tắc | Nielsen #9: Help Users Recognize, Diagnose, and Recover from Errors | **Severity 3** | Hiển thị rõ lý do cổng nào chặn (cosine similarity vs. intent confidence), liệt kê 7 chủ đề được hỗ trợ và 3 gợi ý diễn đạt lại; **không** định tuyến văn phòng theo phỏng đoán của classifier trên câu bị từ chối. |
| **U4** | Nội dung câu trả lời (`answer`) bị hiển thị trong thẻ `st.caption` (chữ nhỏ màu xám nhạt), gây mỏi mắt | WCAG 2.2 SC 1.4.3: Contrast (Minimum); Nielsen #8: Aesthetic & Minimalist Design | **Severity 3** | Thay `st.caption` bằng `st.markdown` với cỡ chữ chuẩn, tương phản cao, đóng khung thẻ câu trả lời (Card container) nổi bật. |
| **U5** | Điểm số Cosine thô (e.g., `0.306`) gây khó hiểu và bối rối cho sinh viên không chuyên toán | Nielsen #2: Match between System and the Real World | **Severity 2** | Chuyển điểm số thành nhãn định tính thân thiện kèm huy hiệu: `🟢 Strong match` ($\ge 0.35$), `🟡 Possible match` ($0.22 - 0.35$), `⚪ Weak match` ($< 0.22$). |
| **U6** | Không phân biệt trực quan giữa FAQ chung và Thông báo chính thức có hạn định thời gian | Nielsen #1: Visibility of System Status; Institutional Risk | **Severity 2** | Thêm nhãn nguồn: `[FAQ]` vs `[Official Notice · Published: YYYY-MM-DD]` lấy trực tiếp từ trường `date` của `data/notices.json`. |
| **U7** | Thanh trượt ngưỡng kỹ thuật ($\theta_{\text{sim}}$, $\theta_{\text{intent}}$) phơi bày trực tiếp ở giao diện chính | Nielsen #8: Aesthetic & Minimalist Design; Cognitive Load | **Severity 2** | Ẩn các tham số kỹ thuật vào công tắc **`🔬 Research & Inspector Mode`** ở Sidebar; sinh viên chỉ thấy giao diện sạch sẽ. |
| **U8** | Bảng ma trận `explain()` gây nhiễu loạn thị giác cho sinh viên chỉ cần đọc câu trả lời | Nielsen #8: Aesthetic & Minimalist Design | **Severity 1** | Đưa phần bóc tách $n$-gram vào khối Expander kỹ thuật, chỉ mở mặc định khi kích hoạt chế độ Nghiên cứu (`Inspector Mode`). |
| **U9** | Các chỉ số ở Dashboard Đánh giá bị gõ cứng (hardcoded), không tự động đồng bộ từ file kết quả | Data Truth & Integrity Lock; Nielsen #1 | **Severity 2** | Đọc động 100% số liệu từ `business_summary.csv`, `per_intent_business.csv`, `summary.csv`, và `ablation.csv`. |
| **U10** | Danh sách duyệt tài liệu ở Sidebar không có thông tin tổng số và thanh lọc tìm kiếm nhanh | Nielsen #6: Recognition Rather than Recall | **Severity 1** | Hiển thị rõ ràng `"Showing X of 112 documents"` và thêm ô lọc tìm kiếm tài liệu theo từ khóa hoặc intent. |
| **U11** | Thiếu cơ chế thu thập phản hồi của sinh viên về mức độ thỏa đáng của câu trả lời | Nielsen #1: Visibility of System Status; Continuous Feedback | **Severity 1** | Bổ sung nút phản hồi `"Helpful"` / `"Needs Clarification"` ghi JSONL vào `output/feedback/feedback.jsonl` (git-ignored). |
| **U12** | Vi phạm WCAG 2.2 AA: màu sắc dùng đơn độc để truyền tải trạng thái; bảng thiếu caption ngữ nghĩa | WCAG 2.2 SC 1.4.1: Use of Color; SC 1.3.1: Info and Relationships | **Severity 3** | Đi kèm biểu tượng icon và nhãn văn bản với mọi màu sắc; thêm thẻ `<caption class="sr-only">` cho bảng HTML `show_table`. |
| **U13** | Giao diện bị khựng đơ khi nạp mô hình lazy trong lần truy vấn đầu tiên | Nielsen #1: Visibility of System Status | **Severity 1** | Sử dụng `st.spinner("Initializing neural-free vector index and calibrated intent models...")` khi khởi tạo. |
| **U14** | Sinh viên gõ tiếng Việt có dấu nhưng hệ thống chỉ xử lý tiếng Anh, gây trả về rỗng không rõ lý do | Nielsen #9: Help Users Recover from Errors | **Severity 2** | Tích hợp hàm `is_non_english_query`: Tự động nhận diện ký tự tiếng Việt và hiển thị lời nhắc song ngữ thân thiện yêu cầu nhập tiếng Anh. |

---

## 2. Walkthrough Nhận thức theo 3 Persona Sinh viên (Cognitive Walkthrough)

### Persona 1: Nguyễn Mai Anh — Sinh viên Năm nhất (Freshman)
- **Bối cảnh:** Vừa nhập học, cần tra cứu thời hạn nộp học phí học kỳ Fall 2026 và thủ tục xin gia hạn đóng học phí.
- **Hành vi & Tác vụ:** Truy cập cổng thông tin, gõ câu hỏi: *"When is tuition due and how do I apply for an installment plan?"*
- **Trải nghiệm hiện tại:** Thấy 2 nút bấm khác nhau ("Classify intent" và "Retrieve documents"), không biết bấm nút nào. Câu trả lời hiện bằng chữ xám nhỏ xíu ở chân trang.
- **Trải nghiệm sau nâng cấp (Orca UX):** 
  - Chỉ cần gõ câu hỏi và nhấn `Enter`.
  - Hệ thống định tuyến tức thì: `Intent: tuition · confidence 88% · Contact: Bursar's Office`.
  - Thẻ 1 (`faq_tuition_01`): Hiển thị nhãn `🟢 Strong match`, toàn văn câu trả lời rõ nét trong khung nền bo góc chuyên nghiệp.
  - Thẻ 2 (`notice_tuition_01` / `faq_tuition_02`): Hiển thị thông báo hạn nộp học phí và câu trả lời liên quan.
  - Có nút `"Helpful"` để ghi nhận phản hồi hữu ích.

### Persona 2: Jean-Pierre — Sinh viên Quốc tế trao đổi (Exchange Student)
- **Bối cảnh:** Sử dụng bàn phím điện thoại gõ vội câu hỏi bị dính nhiều lỗi chính tả: *"tution dedline paymnt for upcomng semster"*.
- **Hành vi & Tác vụ:** Tra cứu cứu trợ khẩn cấp để không bị phạt đóng muộn.
- **Trải nghiệm sau nâng cấp (Orca UX):**
  - Nhờ cơ chế `char_wb (3, 5)`, hệ thống không bị lỗi Out-Of-Vocabulary (OOV).
  - Kết quả trả về chính xác `faq_tuition_01` với nhãn `🟢 Strong match`.
  - Từ khóa trùng khớp được làm nổi bật (`highlight_matched_terms`), giúp Jean-Pierre nhận ra hệ thống đã hiểu đúng ý định của mình dù từ ngữ bị gõ sai.

### Persona 3: Trần Quốc Bảo — Sinh viên Hỏi ngoài phạm vi / Gõ tiếng Việt
- **Bối cảnh:** Hỏi về quán ăn chay gần trường hoặc gõ tiếng Việt: *"Học phí kỳ này bao nhiêu tiền?"*
- **Hành vi & Tác vụ:** Nhập câu hỏi tiếng Việt hoặc câu hỏi ngoài kho.
- **Trải nghiệm sau nâng cấp (Orca UX):**
  - Với câu tiếng Việt: Hệ thống phát hiện ký tự có dấu, hiển thị lời nhắc thân thiện:
    > *"💡 Xin chào! Trợ lý quy chế hiện tại hỗ trợ tốt nhất với câu hỏi bằng tiếng Anh. Quý sinh viên vui lòng đặt câu hỏi bằng tiếng Anh (Ví dụ: 'When is the tuition payment deadline?')."*
  - Với câu hỏi ngoài kho (`q_004` quán ăn chay): Hệ thống chặn đứng an toàn, không hiện hộp xanh mâu thuẫn, hiển thị thông báo chuyển tiếp:
    > *"🛡️ Information not found — please contact the administrative office.*  
    > *Outside the indexed documents. Topics it covers: Course Registration, Tuition & Fees, ...*  
    > *Gợi ý: diễn đạt lại bằng thuật ngữ học vụ nếu câu hỏi thuộc 7 chủ đề này; nếu không, hỏi trực tiếp nhà trường."*
  - App **không** gợi ý văn phòng cho câu bị từ chối: intent của câu ngoài kho chỉ là dự đoán bắt buộc của bộ phân loại, và kho dữ liệu không có phòng, tòa nhà hay giờ làm việc nào để chỉ đường.

---

## 3. Tuân thủ Tiêu chuẩn Tiếp cận Web (WCAG 2.2 Level AA Compliance Checklist)

1. **SC 1.4.1 Use of Color (Level A):** Không bao giờ sử dụng màu sắc làm phương tiện duy nhất để truyền tải thông tin. Mọi nhãn kết quả (`Strong match`, `Possible match`, `Weak match`) đều đi kèm biểu tượng hình học trực quan (`🟢`, `🟡`, `⚪`) và nhãn chữ rõ ràng.
2. **SC 1.4.3 Contrast Minimum (Level AA):** Tỷ lệ tương phản giữa chữ và nền đạt tối thiểu `4.5:1` cho văn bản thông thường và `3:1` cho tiêu đề lớn. Toàn bộ nội dung trả lời chuyển từ chữ xám `st.caption` sang chữ tiêu chuẩn `st.markdown`.
3. **SC 1.3.1 Info and Relationships (Level A):** Các bảng HTML render qua `show_table(df)` được cấu trúc với thẻ `<table role="table">`, `<thead>`, `<tbody>` và caption mô tả ngữ nghĩa rõ ràng cho thiết bị đọc màn hình (Screen Reader).
4. **SC 2.1.1 Keyboard Navigation (Level A):** Mọi thành phần tương tác (ô tìm kiếm, nút bấm, expander, toggle) đều có thể tiếp cận và kích hoạt hoàn toàn bằng phím `Tab` và `Enter`.
5. **SC 2.4.7 Focus Visible (Level AA):** Vùng chọn và tiêu điểm phím được giữ nguyên theo chuẩn thiết kế trình duyệt, không bị che khuất bởi CSS tùy biến.

---

## 4. Quan sát Định tính Trải nghiệm Thử nghiệm (Qualitative Observations, n=1–2)

> [!NOTE]
> **Giới hạn Phương pháp luận Học thuật:**
> Mục này ghi lại các quan sát định tính ban đầu khi cho 1–2 sinh viên trải nghiệm bản thử nghiệm nội bộ để phát hiện nhanh các rào cản thao tác.
> - **KHÔNG** phải là kiểm thử khả năng sử dụng (formal usability test) trên tập mẫu đại diện thống kê.
> - **KHÔNG** tính chỉ số hài lòng SUS (System Usability Scale) do cỡ mẫu không đủ ý nghĩa thống kê.
> - **KHÔNG** báo cáo tỷ lệ hoàn thành tác vụ dạng phần trăm (percentage completion rate).
> - Các ô chưa có kiểm chứng thực tế được giữ nguyên trạng, không tự suy diễn số liệu.

### Bảng Quan sát 5 Nhiệm vụ Cốt lõi (Task Walkthrough Log)

| STT | Nhiệm vụ Yêu cầu | Làm được không? | Vướng mắc / Trở ngại gặp phải | Ghi chú Hành vi & Đề xuất Cải tiến |
|:---:|---|:---:|---|---|
| **T1** | **Tìm hạn đóng học phí** học kỳ Fall (*"When is tuition due?"*) | Hoàn thành | Ban đầu nhìn vào thanh bên thấy nhiều tham số kỹ thuật gây phân tâm trước khi tìm thấy ô nhập câu hỏi. | Sau khi ẩn tham số vào `Inspector Mode`, người thử nghiệm gõ câu hỏi và đọc được câu trả lời ở Thẻ 1 ngay lập tức. |
| **T2** | **Xin hoãn thi / trùng lịch thi** (*"I have two exams overlapping"*) | Hoàn thành | Nhầm lẫn giữa nút *"Classify intent"* và *"Retrieve documents"*, tự hỏi có cần bấm phân loại trước khi tìm kiếm không. | Hỗ trợ nhấn `Enter` trực tiếp ở ô tìm kiếm giúp người dùng hoàn thành tác vụ mà không cần bận tâm về 2 nút bấm riêng biệt. |
| **T3** | **Gõ sai chính tả vội vã** (*"tution dedline paymnt"*) | Hoàn thành | Người thử hơi bất ngờ khi hệ thống vẫn trả về đúng hạn nộp học phí dù gõ sai 3 từ trong câu ngắn. | Cần tô đậm từ khóa trùng khớp (`highlight_matched_terms`) để người dùng an tâm nhận diện rằng hệ thống đã sửa lỗi ngầm. |
| **T4** | **Hỏi ngoài phạm vi** (*"What's the best restaurant near campus?"* hoặc *"Can I rent a kayak..."*) | Hoàn thành | Không nhận được câu trả lời tài liệu (đúng theo thiết kế từ chối an toàn). | Hiển thị thông báo *"Information not found — please contact the administrative office."*, giải thích rõ cổng nào bị trượt (cosine vs. intent confidence), liệt kê 7 chủ đề hỗ trợ và 3 gợi ý; không định tuyến nhầm vào văn phòng đoán bừa. |
| **T5** | **Tìm điểm liên hệ trong kho** khi thắc mắc | Hoàn thành | Trước đây tên kênh hỗ trợ chỉ nằm rải rác trong các câu trả lời FAQ. | Khối liên hệ (`office_for_intent`) chỉ trích xuất tên điểm liên hệ và kênh tự phục vụ có bằng chứng trực tiếp trong kho dữ liệu (`OFFICE_REGISTRY`), không tự suy diễn số phòng hay giờ mở cửa. |

---

## 5. Bằng chứng Nghiệm thu Giao diện Thực tế (Visual Evidence & Interactive Audit)

Ảnh chụp kiểm chứng giao diện Light Mode hiện tại (sau PR #19) được chụp trực tiếp qua Playwright tại [`output/playwright/live-demo/`](../output/playwright/live-demo/) cùng log đối chiếu [`observations.json`](../output/playwright/live-demo/observations.json) (0 lỗi, 0 cảnh báo console). Các ảnh tại `notes/ux_evidence/screenshot_01..04.png` là bản lưu trữ lịch sử của đợt audit Dark Mode trước PR #14.

### 5.1 Danh mục Ảnh chụp Kiểm chứng Hiện hành (Playwright Live Demo — Light Editorial Theme)

1. **[01-normal.png](../output/playwright/live-demo/01-normal.png) — In-corpus Query với Answer Cards & Contact**
   - *Tác vụ:* Sinh viên tra cứu đặt lại mật khẩu (*"How do I reset my Student Portal password?"*).
   - *Kết quả trực quan:* Banner xanh lá `Intent: technical_support · confidence 88% · Contact: IT Help Desk`, thẻ #1 `faq_technical_support_01` với huy hiệu `🟢 Strong match` (0.539), thanh đo độ khớp, highlight từ khóa và trích nguồn/ngày ban hành của notice #2.

2. **[02-typo.png](../output/playwright/live-demo/02-typo.png) — Typo Robustness Query**
   - *Tác vụ:* Sinh viên gõ nhầm *"How do I reset my Sutdent Portal password?"*.
   - *Kết quả trực quan:* Nhờ `char_wb (3,5)`, hệ thống vẫn xếp hạng đúng `faq_technical_support_01` ở #1 (cosine 0.528, intent confidence 90%).

3. **[03-paraphrase.png](../output/playwright/live-demo/03-paraphrase.png) — Paraphrase Query**
   - *Tác vụ:* Diễn đạt lại *"I forgot my Student Portal password - how do I reset it?"*.
   - *Kết quả trực quan:* Trả về đúng `faq_technical_support_01` ở #1 (cosine 0.514, intent confidence 85%).

4. **[04-restaurant.png](../output/playwright/live-demo/04-restaurant.png) & [05-kayak.png](../output/playwright/live-demo/05-kayak.png) — Out-of-Corpus Safe Abstention**
   - *Tác vụ:* Sinh viên hỏi câu ngoài kho (*"What's the best restaurant near campus for vegan food?"* và *"Can I rent a kayak from the campus recreation center?"*).
   - *Kết quả trực quan:* Hệ thống từ chối an toàn với thông báo `Information not found — please contact the administrative office.`, **tuyệt đối không** xuất hiện banner `st.success` hay tên văn phòng đoán bừa, và ghi rõ `Why it was rejected` (ví dụ câu kayak: cosine 0.39 vượt ngưỡng 0.15, nhưng intent confidence 29% trượt ngưỡng 34%).

5. **[06-known-failure.png](../output/playwright/live-demo/06-known-failure.png) — Known Failure & Top-3 Rescue Demo**
   - *Tác vụ:* Câu hỏi trùng lịch thi cuối kỳ (*"Two of my finals overlap on the same day - who do I tell?"*).
   - *Kết quả trực quan:* Minh bạch cho thấy hạn chế của khớp từ vựng: #1 trả nhầm `faq_class_schedule_02` (0.268), nhưng FAQ đúng `faq_exam_02` vẫn hiện ở thẻ #2 (0.189).

---

### 5.2 Biên bản Kiểm thử Bàn phím & Tiếp cận (Keyboard Navigation & Accessibility Audit)

- **Chuỗi Tiêu điểm Phím (Focus Order):**
  1. `Tab 1` -> Ô nhập liệu câu hỏi (`text_input[0]`).
  2. `Tab 2` -> Nút *"Classify intent"* (`button[0]`).
  3. `Tab 3` -> Nút *"Retrieve documents"* (`button[1]`).
  4. `Tab 4..n` -> Các thẻ kết quả và khối chi tiết expander.
- **Vòng sáng Tiêu điểm (Focus Ring Visibility):** Ô nhập liệu có viền focus rõ nét (`#2563eb` kết hợp `box-shadow` trong `starter/theme.py`), các thành phần tương tác giữ nguyên tiêu điểm chuẩn trình duyệt.
- **Kẹt phím (No Keyboard Trap):** Người dùng có thể di chuyển ra vào toàn bộ các phần tử tương tác bằng phím `Tab` / `Shift+Tab` và kích hoạt bằng `Enter` / `Space`. Phím `Esc` đóng mở các phần tử trượt/expander mà không làm kẹt con trỏ.
- **Tương phản Màu (Contrast Ratios):** Toàn bộ các cặp màu văn bản và bề mặt nền đều vượt ngưỡng tối thiểu WCAG 2.2 Level AA ($\ge 4.5:1$ đối với body text, $\ge 3.0:1$ đối với large text và badge UI) theo kiểm thử tự động tại `tests/test_theme.py`.


