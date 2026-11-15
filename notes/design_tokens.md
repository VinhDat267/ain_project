# Hệ thống Token Thiết kế & Chuẩn Giao diện Sinh viên (Design Tokens Specification)

> **Tài liệu đặc tả hệ thống Design Tokens — Project 12 (Campus FAQ Assistant)**  
> **Chuyên gia phụ trách:** `agency-ui-designer` & `agency-accessibility-auditor`  
> **Phong cách định hướng:** Tinh giản, học thuật, trang nhã theo triết lý của **Claude / Editorial Academic Light (`od-design-systems`)**; tuân thủ nghiêm ngặt nguyên tắc **Anti-AI-Slop** và **WCAG 2.2 Level AA**.

---

## 1. Triết lý Thiết kế & Nguyên tắc Chống Phô trương (Anti-AI-Slop Manifesto)

1. **Không sử dụng Nền đen xì dập khuôn (No Pitch-Black Slop):** Loại bỏ hoàn toàn nền tối đen đặc `#000000` hay `#0d0f12`. Sử dụng hệ màu **Parchment Warm Light (`#F5F4ED`)** kết hợp thẻ nổi trắng ngà Ivory (`#FAF9F5`), mô phỏng trang sổ tay học vụ đại học sang trọng, dịu mắt và nghiêm túc.
2. **Không sử dụng Gradient Tím - Xanh (No Purple/Cyan Gradient Slop):** Loại bỏ các dải màu neon AI-slop. Toàn bộ nền là bề mặt phẳng (flat surface) với viền ấm `#E8E6DC` tinh tế.
3. **Typography mang bản sắc Học thuật (Editorial Typography):** Tiêu đề trang và câu hỏi chính sử dụng font có chân (Serif: `Georgia, "Times New Roman", serif`), tạo cảm giác tin cậy và trang trọng của văn bản quy chế ban hành chính thức.
4. **Không bo góc kèm viền trái màu (Anti-AI-Slop Sin #5):** Loại bỏ hoàn toàn định dạng "thẻ bo tròn kèm viền trái màu cam/xanh" (AI dashboard tile). Sử dụng thẻ nguyên khối đối xứng, phân cấp bằng badge và typographic hierarchy.
5. **Không dùng Emoji làm biểu tượng tiêu đề (Anti-AI-Slop Sin #3):** Tiêu đề tab, nhãn danh mục và nút thao tác dùng ngôn ngữ và nhãn văn bản chuẩn, sạch sẽ.
6. **Độ rộng dòng đọc tối ưu (Optimal Reading Measure):** Nội dung câu trả lời quy chế giới hạn chiều rộng tối đa $\le 68\text{ch}$ (khoảng 68 ký tự/dòng), cỡ chữ chuẩn `16px`, chiều cao dòng `1.65` để sinh viên đọc dễ dàng trên cả máy tính và thiết bị di động.

---

## 2. Bảng Mã Token Bề mặt, Màu sắc & Tương phản WCAG 2.2 AA

### A. 3 Tầng Bề mặt (Surface Elevation Hierarchy)

| Tên Token | Mã Hex | Vai trò trong Giao diện | Tỷ lệ Tương phản với Chữ chính (`#141413`) |
|---|:---:|---|:---:|
| `--surface-0` (Canvas) | `#f5f4ed` | Nền toàn trang ứng dụng (Warm Parchment) | **16.7 : 1** (Đạt chuẩn WCAG AAA) |
| `--surface-1` (Card) | `#faf9f5` | Nền thẻ câu trả lời, khối kết quả, directory card (Ivory) | **17.5 : 1** (Đạt chuẩn WCAG AAA) |
| `--surface-2` (Elevated) | `#e8e6dc` | Nền thanh bên (Sidebar), bảng header, ô input (Warm Sand) | **14.7 : 1** (Đạt chuẩn WCAG AAA) |
| `--surface-border` | `#d6d3c4` | Đường viền ngăn cách tinh tế giữa các khối (1px solid) | &mdash; |

### B. Màu Nhấn & Màu Ngữ nghĩa (Accent & Semantic Tokens)

| Tên Token | Mã Hex | Ý nghĩa Nghiệp vụ | Tương phản trên Surface-1 (`#faf9f5`) | Đạt chuẩn WCAG 2.2 |
|---|:---:|---|:---:|:---:|
| `--accent-teal` | `#b45309` | Màu nhấn hành chính (Liên kết, focus ring, action highlight) | **4.8 : 1** | **Level AA** |
| `--match-strong` | `#166534` | `Strong match` (Điểm Cosine $\ge 0.35$, độ khớp cao) | **6.8 : 1** | **Level AAA** |
| `--match-possible` | `#b45309` | `Possible match` (Điểm Cosine $0.22 - 0.35$, câu diễn giải) | **4.8 : 1** | **Level AA** |
| `--match-weak` | `#5e5d59` | `Weak match` (Điểm Cosine $< 0.22$, câu hỏi mấp mé) | **6.3 : 1** | **Level AAA** |
| `--status-error` | `#b91c1c` | Trạng thái từ chối an toàn / cảnh báo hành chính | **6.1 : 1** | **Level AAA** |

### C. Thang Văn bản & Kiểu chữ (Typography Scale)

| Phân cấp | Kích thước | Chiều cao dòng (Line Height) | Kiểu chữ (Font Family) | Độ đậm (Weight) |
|---|:---:|:---:|:---:|:---:|
| **Overline Category** | `12px` (`0.75rem`) | `1.2` | Sans-serif uppercase | `700` (Bold) |
| **App Title** | `32px` (`2.0rem`) | `1.25` | `Georgia, serif` | `600` (Semi-bold) |
| **Section Heading** | `20px` (`1.25rem`) | `1.35` | `Georgia, serif` | `600` (Semi-bold) |
| **Card Question Title**| `18px` (`1.15rem`) | `1.4` | `Georgia, serif` | `600` (Semi-bold) |
| **Body Answer Text** | **`16px` (`1.0rem`)** | **`1.65`** | **`system-ui, sans-serif`** | **`400` (Regular)** |
| **Meta / Badge / Office**| `13px` (`0.8125rem`) | `1.3` | `system-ui, sans-serif` | `600` (Semi-bold) |
| **Details / Code Tag** | `12px` (`0.75rem`) | `1.2` | `ui-monospace, monospace` | `400` (Regular) |

---

## 3. Quy chuẩn Hiển thị Chuyển động & Tiếp cận (Motion & Accessibility Baseline)

1. **Hiệu ứng Thẻ Xuất hiện (Staggered Fade-in):**
   - Thẻ số 1 xuất hiện sau `50ms`, Thẻ số 2 sau `150ms`, Thẻ số 3 sau `250ms`.
   - Độ dịch chuyển nhẹ: $6\text{px} \to 0\text{px}$, độ trong suốt: $0 \to 1$.
   - Thời gian chuyển động tối đa $\le 200\text{ms}$ với hàm gia tốc mềm `cubic-bezier(0.16, 1, 0.3, 1)`.
2. **Kỷ luật Giảm Chuyển động (prefers-reduced-motion: reduce):**
   - Khi hệ điều hành hoặc trình duyệt của người khuyết tật/người nhạy cảm kích hoạt chế độ giảm chuyển động, toàn bộ thời gian transition/animation lập tức được đưa về `0.01ms` (loại bỏ hoàn toàn rung lắc thị giác, tuân thủ WCAG 2.2 SC 2.3.3).
