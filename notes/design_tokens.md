# Hệ thống Token Thiết kế & Chuẩn Giao diện Sinh viên (Design Tokens Specification)

> **Tài liệu đặc tả hệ thống Design Tokens — Project 12 (Campus FAQ Assistant)**  
> **Chuyên gia phụ trách:** `agency-ui-designer` & `agency-accessibility-auditor`  
> **Phong cách định hướng:** Tinh giản, học thuật, trang nhã theo triết lý của **Oxford Navy & Claude Daylight Chromatic (`od-design-systems`)**; tuân thủ nghiêm ngặt nguyên tắc **Anti-AI-Slop** và **WCAG 2.2 Level AA**.

---

## 1. Triết lý Thiết kế & Nguyên tắc Chống Phô trương (Anti-AI-Slop Manifesto)

1. **Phá vỡ Sự Đơn điệu (Monotone) bằng Neo Thị giác:** Nền toàn trang giữ sự sáng sủa ấm áp (`#F5F4ED`), kết hợp với **Hero Banner Xanh Navy Đậm Oxford (`#0F172A` → `#1E293B`)** và các thẻ thông tin nổi trắng ngà (`#FAF9F5`). Sự tương phản này tạo điểm neo thị giác mạnh mẽ ngay khi tải trang.
2. **Hệ màu Định danh cho 7 Chủ đề Học vụ (7-Domain Chromatic Coding):** Mỗi lĩnh vực trong 7 `INTENTS` thật của trường được gán một dải màu riêng biệt (Xanh hoàng gia, Ngọc lục bảo, Đỏ học thuật, Tím chàm, Hổ phách, Mận chín, Xanh da trời) với đường viền đỉnh thẻ `3.5px` và huy hiệu màu nhạt tương phản cao.
3. **Phân cấp Rõ rệt Thẻ Kết quả (Featured Rank #1 vs Supporting Cards):** Thẻ Top #1 được viền nổi bật `2px` với huy hiệu `★ TOP RECOMMENDED ANSWER` và **Thanh đo độ khớp trực quan (Relevance Meter Bar)**, giúp sinh viên nhận diện ngay đáp án trọng tâm.
4. **Typography mang bản sắc Học thuật (Editorial Typography):** Tiêu đề trang và câu hỏi chính sử dụng font có chân (Serif: `Georgia, "Times New Roman", serif`), tạo cảm giác tin cậy và trang trọng của văn bản quy chế ban hành chính thức.
5. **Không bo góc kèm viền trái màu (Anti-AI-Slop Sin #5):** Thẻ được thiết kế nguyên khối đối xứng, phân định trạng thái bằng viền đỉnh và badge ngữ nghĩa.
6. **Không dùng Emoji làm biểu tượng tiêu đề (Anti-AI-Slop Sin #3):** Tiêu đề tab, nhãn danh mục và nút thao tác dùng ngôn ngữ và nhãn văn bản chuẩn, sạch sẽ.
7. **Độ rộng dòng đọc tối ưu (Optimal Reading Measure):** Nội dung câu trả lời quy chế giới hạn chiều rộng tối đa $\le 68\text{ch}$ (khoảng 68 ký tự/dòng), cỡ chữ chuẩn `16px`, chiều cao dòng `1.65`.

---

## 2. Bảng Mã Token Bề mặt, Màu sắc & Tương phản WCAG 2.2 AA

### A. 3 Tầng Bề mặt & Hero Banner

| Tên Token | Mã Hex | Vai trò trong Giao diện | Tỷ lệ Tương phản với Chữ |
|---|:---:|---|:---:|
| `--hero-navy-bg` | `#0f172a` → `#1e293b` | Hero Masthead Banner đầu trang | **16.5 : 1** với chữ trắng kem `#F8FAFC` (AAA) |
| `--surface-0` (Canvas) | `#f5f4ed` | Nền toàn trang ứng dụng (Warm Parchment) | **16.7 : 1** với chữ mực `#141413` (AAA) |
| `--surface-1` (Card) | `#faf9f5` | Nền thẻ câu trả lời, khối kết quả, directory card (Ivory) | **17.5 : 1** với chữ mực `#141413` (AAA) |
| `--surface-2` (Elevated) | `#e8e6dc` | Nền thanh bên (Sidebar), bảng header, ô input (Warm Sand) | **14.7 : 1** với chữ mực `#141413` (AAA) |
| `--surface-border` | `#d6d3c4` | Đường viền ngăn cách tinh tế giữa các khối (1px solid) | &mdash; |

### B. 7 Bảng màu Định danh Chủ đề Học vụ (7-Domain Chromatic Palette)

| Chủ đề (`intent`) | Văn phòng Phụ trách | Màu Chủ đạo | Nền Huy hiệu | Chữ Huy hiệu | Chuẩn WCAG |
|---|---|:---:|:---:|:---:|:---:|
| `course_registration` | Registrar's Office | `#2563eb` (Royal Blue) | `#dbeafe` | `#1e40af` | **5.4 : 1 (AA)** |
| `tuition` | Bursar's Office | `#059669` (Emerald Teal) | `#d1fae5` | `#065f46` | **6.1 : 1 (AAA)** |
| `exam` | Registrar's Office | `#e11d48` (Academic Crimson)| `#ffe4e6` | `#9f1239` | **5.8 : 1 (AA)** |
| `class_schedule` | Registrar's Office | `#4f46e5` (Indigo Violet) | `#e0e7ff` | `#3730a3` | **6.9 : 1 (AAA)** |
| `student_services` | Advising Center | `#d97706` (Warm Amber) | `#fef3c7` | `#92400e` | **5.3 : 1 (AA)** |
| `graduation` | Registrar's Office | `#9333ea` (Burgundy Plum) | `#f3e8ff` | `#6b21a8` | **5.7 : 1 (AA)** |
| `technical_support` | IT Help Desk | `#0284c7` (Sky Cyan) | `#e0f2fe` | `#075985` | **5.6 : 1 (AA)** |

### C. Màu Nhấn & Màu Ngữ nghĩa (Accent & Semantic Tokens)

| Tên Token | Mã Hex | Ý nghĩa Nghiệp vụ | Tương phản trên Surface-1 (`#faf9f5`) | Đạt chuẩn WCAG 2.2 |
|---|:---:|---|:---:|:---:|
| `--accent-teal` | `#b45309` | Màu nhấn hành chính (Liên kết, focus ring, action highlight) | **4.8 : 1** | **Level AA** |
| `--match-strong` | `#166534` | `Strong match` (Điểm Cosine $\ge 0.35$, độ khớp cao) | **6.8 : 1** | **Level AAA** |
| `--match-possible` | `#b45309` | `Possible match` (Điểm Cosine $0.22 - 0.35$, câu diễn giải) | **4.8 : 1** | **Level AA** |
| `--match-weak` | `#5e5d59` | `Weak match` (Điểm Cosine $< 0.22$, câu hỏi mấp mé) | **6.3 : 1** | **Level AAA** |
| `--status-error` | `#b91c1c` | Trạng thái từ chối an toàn / cảnh báo hành chính | **6.1 : 1** | **Level AAA** |

---

## 3. Quy chuẩn Hiển thị Chuyển động & Tiếp cận (Motion & Accessibility Baseline)

1. **Hiệu ứng Thẻ Xuất hiện (Staggered Fade-in):**
   - Thẻ Top #1 xuất hiện sau `40ms`, Thẻ số 2 sau `120ms`, Thẻ số 3 sau `200ms`.
   - Độ dịch chuyển nhẹ: $6\text{px} \to 0\text{px}$, độ trong suốt: $0 \to 1$.
   - Thời gian chuyển động tối đa $\le 200\text{ms}$ với hàm gia tốc mềm `cubic-bezier(0.16, 1, 0.3, 1)`.
2. **Kỷ luật Giảm Chuyển động (prefers-reduced-motion: reduce):**
   - Khi hệ điều hành hoặc trình duyệt của người khuyết tật/người nhạy cảm kích hoạt chế độ giảm chuyển động, toàn bộ thời gian transition/animation lập tức được đưa về `0.01ms` (loại bỏ hoàn toàn rung lắc thị giác, tuân thủ WCAG 2.2 SC 2.3.3).
