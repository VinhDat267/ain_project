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
| **U3** | Hộp thông báo từ chối cộc lốc, không hướng dẫn bước tiếp theo khi sinh viên bế tắc | Nielsen #9: Help Users Recognize, Diagnose, and Recover from Errors | **Severity 3** | Cung cấp thông tin điều hướng: văn phòng liên hệ phụ trách chủ đề dự đoán (`office_for_intent`) + 3 gợi ý cách đặt lại câu hỏi. |
| **U4** | Nội dung câu trả lời (`answer`) bị hiển thị trong thẻ `st.caption` (chữ nhỏ màu xám nhạt), gây mỏi mắt | WCAG 2.2 SC 1.4.3: Contrast (Minimum); Nielsen #8: Aesthetic & Minimalist Design | **Severity 3** | Thay `st.caption` bằng `st.markdown` với cỡ chữ chuẩn, tương phản cao, đóng khung thẻ câu trả lời (Card container) nổi bật. |
| **U5** | Điểm số Cosine thô (e.g., `0.306`) gây khó hiểu và bối rối cho sinh viên không chuyên toán | Nielsen #2: Match between System and the Real World | **Severity 2** | Chuyển điểm số thành nhãn định tính thân thiện kèm huy hiệu: `🟢 Strong match` ($\ge 0.35$), `🟡 Possible match` ($0.22 - 0.35$), `⚪ Weak match` ($< 0.22$). |
| **U6** | Không phân biệt trực quan giữa FAQ chung và Thông báo chính thức có hạn định thời gian | Nielsen #1: Visibility of System Status; Institutional Risk | **Severity 2** | Thêm nhãn nguồn: `[FAQ]` vs `[Official Notice · Published: YYYY-MM-DD]` lấy trực tiếp từ trường `date` của `data/notices.json`. |
| **U7** | Thanh trượt ngưỡng kỹ thuật ($\theta_{\text{sim}}$, $\theta_{\text{intent}}$) phơi bày trực tiếp ở giao diện chính | Nielsen #8: Aesthetic & Minimalist Design; Cognitive Load | **Severity 2** | Ẩn các tham số kỹ thuật vào công tắc **`🔬 Research & Inspector Mode`** ở Sidebar; sinh viên chỉ thấy giao diện sạch sẽ. |
| **U8** | Bảng ma trận `explain()` gây nhiễu loạn thị giác cho sinh viên chỉ cần đọc câu trả lời | Nielsen #8: Aesthetic & Minimalist Design | **Severity 1** | Đưa phần bóc tách $n$-gram vào khối Expander kỹ thuật, chỉ mở mặc định khi kích hoạt chế độ Nghiên cứu (`Inspector Mode`). |
| **U9** | Các chỉ số ở Dashboard Đánh giá bị gõ cứng (hardcoded), không tự động đồng bộ từ file kết quả | Data Truth & Integrity Lock; Nielsen #1 | **Severity 2** | Đọc động 100% số liệu từ `business_summary.csv`, `per_intent_business.csv`, `summary.csv`, và `ablation.csv`. |
| **U10** | Danh sách duyệt tài liệu ở Sidebar không có thông tin tổng số và thanh lọc tìm kiếm nhanh | Nielsen #6: Recognition Rather than Recall | **Severity 1** | Hiển thị rõ ràng `"Showing X of 112 documents"` và thêm ô lọc tìm kiếm tài liệu theo từ khóa hoặc intent. |
| **U11** | Thiếu cơ chế thu thập phản hồi của sinh viên về mức độ thỏa đáng của câu trả lời | Nielsen #1: Visibility of System Status; Continuous Feedback | **Severity 1** | Bổ sung nút phản hồi `"👍 Helpful"` / `"👎 Needs clarification"` lưu vào `st.session_state` để ghi nhận trải nghiệm. |
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
  - Hệ thống định tuyến tức thì: `Intent: tuition · Confidence: 90% · Routing: Bursar's Office & Student Accounts`.
  - Thẻ 1 (`faq_tuition_01`): Hiển thị nhãn `🟢 Strong match`, toàn văn câu trả lời rõ nét trong khung nền bo góc chuyên nghiệp.
  - Thẻ 2 (`faq_tuition_02`): Hướng dẫn về kế hoạch trả góp (`installment plan`).
  - Có nút `"👍 Helpful"` để xác nhận câu trả lời đã đáp ứng nhu cầu.

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
    > *Đề xuất văn phòng hỗ trợ: University Administrative Office (Administration Building, Room 101).*  
    > *Gợi ý: Hãy thử đặt câu hỏi tập trung vào quy chế học vụ, lịch thi, đăng ký môn học hoặc học phí."*

---

## 3. Tuân thủ Tiêu chuẩn Tiếp cận Web (WCAG 2.2 Level AA Compliance Checklist)

1. **SC 1.4.1 Use of Color (Level A):** Không bao giờ sử dụng màu sắc làm phương tiện duy nhất để truyền tải thông tin. Mọi nhãn kết quả (`Strong match`, `Possible match`, `Weak match`) đều đi kèm biểu tượng hình học trực quan (`🟢`, `🟡`, `⚪`) và nhãn chữ rõ ràng.
2. **SC 1.4.3 Contrast Minimum (Level AA):** Tỷ lệ tương phản giữa chữ và nền đạt tối thiểu `4.5:1` cho văn bản thông thường và `3:1` cho tiêu đề lớn. Toàn bộ nội dung trả lời chuyển từ chữ xám `st.caption` sang chữ tiêu chuẩn `st.markdown`.
3. **SC 1.3.1 Info and Relationships (Level A):** Các bảng HTML render qua `show_table(df)` được cấu trúc với thẻ `<table role="table">`, `<thead>`, `<tbody>` và caption mô tả ngữ nghĩa rõ ràng cho thiết bị đọc màn hình (Screen Reader).
4. **SC 2.1.1 Keyboard Navigation (Level A):** Mọi thành phần tương tác (ô tìm kiếm, nút bấm, expander, toggle) đều có thể tiếp cận và kích hoạt hoàn toàn bằng phím `Tab` và `Enter`.
5. **SC 2.4.7 Focus Visible (Level AA):** Vùng chọn và tiêu điểm phím được giữ nguyên theo chuẩn thiết kế trình duyệt, không bị che khuất bởi CSS tùy biến.
