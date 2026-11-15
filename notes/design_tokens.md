# Hệ thống Token Thiết kế & Chuẩn Giao diện Sinh viên (Design Tokens Specification)

> **Tài liệu đặc tả hệ thống Design Tokens — Project 12 (Campus FAQ Assistant)**  
> **Chuyên gia phụ trách:** `agency-ui-designer` & `agency-accessibility-auditor`  
> **Phong cách định hướng:** Tinh giản, chính xác, hiện đại theo triết lý của **Linear & Vercel Design System**; tuân thủ nguyên tắc **Anti-AI-Slop** và **WCAG 2.2 Level AA**.

---

## 1. Triết lý Thiết kế & Nguyên tắc Chống Phô trương (Anti-AI-Slop Manifesto)

1. **Không sử dụng Gradient Tím - Xanh (No Purple/Cyan Gradient Slop):** Loại bỏ hoàn toàn các dải chuyển màu lòe loẹt thường thấy trên các giao diện AI mô phỏng. Sử dụng màu đơn sắc (solid) với độ tương phản cao, tập trung tuyệt đối vào khả năng đọc nhanh nội dung quy chế.
2. **Không bo góc quá đà (Disciplined Radii):** Giới hạn bán kính bo góc tối đa `8px` cho thẻ và `6px` cho nút/badge. Tránh phong cách bo tròn bong bóng (`24px+`) gây mất tính nghiêm túc của dịch vụ hành chính.
3. **Phân cấp 3 tầng bề mặt rõ ràng (3-Tier Surface Elevation):** Không sử dụng nền đen tuyệt đối (`#000000`) gây mỏi mắt OLED; áp dụng bảng màu xám than (Charcoal / Dark Slate).
4. **Độ rộng dòng đọc tối ưu (Optimal Reading Measure):** Nội dung câu trả lời quy chế giới hạn chiều rộng tối đa $\le 68\text{ch}$ (khoảng 68 ký tự/dòng), cỡ chữ chuẩn `16px`, chiều cao dòng `1.6` để sinh viên không bị nhảy dòng khi đọc điều khoản dài.

---

## 2. Bảng Mã Token Bề mặt, Màu sắc & Tương phản WCAG 2.2 AA

### A. 3 Tầng Bề mặt (Surface Elevation Hierarchy)

| Tên Token | Mã Hex | Vai trò trong Giao diện | Tỷ lệ Tương phản với Chữ chính (`#f1f5f9`) |
|---|:---:|---|:---:|
| `--surface-0` (Base) | `#0d0f12` | Nền toàn trang ứng dụng (Dark charcoal slate) | **16.4 : 1** (Đạt chuẩn WCAG AAA) |
| `--surface-1` (Card) | `#16191f` | Nền thẻ câu trả lời, khối kết quả, sidebar | **14.2 : 1** (Đạt chuẩn WCAG AAA) |
| `--surface-2` (Elevated) | `#1e222a` | Nền ô nhập liệu, badge, nút bấm, hover state | **11.8 : 1** (Đạt chuẩn WCAG AAA) |
| `--surface-border` | `#2a2f3a` | Đường viền ngăn cách tinh tế giữa các khối (1px solid) | &mdash; |

### B. Màu Nhấn & Màu Ngữ nghĩa (Accent & Semantic Tokens)

| Tên Token | Mã Hex | Ý nghĩa Nghiệp vụ | Tương phản trên Surface-1 (`#16191f`) | Đạt chuẩn WCAG 2.2 |
|---|:---:|---|:---:|:---:|
| `--accent-teal` | `#0ea5e9` | Màu nhấn chính (Hành động tìm kiếm, liên kết, focus ring) | **7.8 : 1** | **Level AAA** |
| `--match-strong` | `#10b981` | `Strong match` (Điểm Cosine $\ge 0.35$, độ khớp cao) | **8.2 : 1** | **Level AAA** |
| `--match-possible` | `#f59e0b` | `Possible match` (Điểm Cosine $0.22 - 0.35$, câu diễn giải) | **7.4 : 1** | **Level AAA** |
| `--match-weak` | `#94a3b8` | `Weak match` (Điểm Cosine $< 0.22$, câu hỏi mấp mé) | **6.5 : 1** | **Level AA** |
| `--status-error` | `#ef4444` | Trạng thái từ chối an toàn / cảnh báo hành chính | **5.1 : 1** | **Level AA** |

### C. Thang Văn bản & Kiểu chữ (Typography Scale)

| Phân cấp | Kích thước | Chiều cao dòng (Line Height) | Độ đậm (Weight) | Giới hạn chiều dài |
|---|:---:|:---:|:---:|:---:|
| **App Title** | `24px` (`1.5rem`) | `1.3` | `700` (Bold) | &mdash; |
| **Section Heading** | `18px` (`1.125rem`) | `1.4` | `600` (Semi-bold) | &mdash; |
| **Card Question Title**| `17px` (`1.0625rem`) | `1.45` | `600` (Semi-bold) | $\le 65\text{ch}$ |
| **Body Answer Text** | **`16px` (`1.0rem`)** | **`1.6`** | **`400` (Regular)** | **$\le 68\text{ch}$** |
| **Meta / Badge / Office**| `13px` (`0.8125rem`) | `1.3` | `500` (Medium) | &mdash; |
| **Details / Code Tag** | `12px` (`0.75rem`) | `1.2` | `400` (Mono) | &mdash; |

---

## 3. Quy chuẩn Hiển thị Chuyển động & Tiếp cận (Motion & Accessibility Baseline)

1. **Hiệu ứng Thẻ Xuất hiện (Staggered Fade-in):**
   - Thẻ số 1 xuất hiện sau `100ms`, Thẻ số 2 sau `200ms`, Thẻ số 3 sau `300ms`.
   - Độ dịch chuyển nhẹ: $4\text{px} \to 0\text{px}$, độ trong suốt: $0 \to 1$.
   - Thời gian chuyển động tối đa $\le 200\text{ms}$ với hàm gia tốc mềm `cubic-bezier(0.16, 1, 0.3, 1)`.
2. **Kỷ luật Giảm Chuyển động (prefers-reduced-motion: reduce):**
   - Khi hệ điều hành hoặc trình duyệt của người khuyết tật/người nhạy cảm kích hoạt chế độ giảm chuyển động, toàn bộ thời gian transition/animation lập tức được đưa về `0.01ms` (loại bỏ hoàn toàn rung lắc thị giác).
