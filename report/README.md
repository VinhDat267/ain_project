# IEEE Conference Research Paper — Project 12

Tài liệu báo cáo khoa học hoàn chỉnh theo chuẩn định dạng hội nghị quốc tế IEEE (2 cột, chuẩn font Times New Roman, công thức toán học MathML thuần chạy offline, bảng biểu đối chiếu thực nghiệm E0–E7, E3b, E5b, và các hình đồ thị trực quan).

## Các phiên bản tài liệu

| Định dạng | Đường dẫn | Mô tả |
|---|---|---|
| **HTML** | [`ieee_report.html`](ieee_report.html) | Bản nguồn chuẩn web, render hình ảnh, MathML và định dạng 2 cột theo CSS `@page`. |
| **PDF** | [`report.pdf`](report.pdf) | Bản xuất PDF hoàn chỉnh (~732 KB, 4 trang) xuất từ Chromium headless (`--no-pdf-header-footer`). |

## Tóm tắt nội dung học thuật chính

1. **Title:** *Deterministic Dual-Gate Information Retrieval and Intent Classification for Academic Administration*
2. **Authors:** Viet-Anh Luong, Dat-Vinh Nguyen, and Anh-Duong Nguyen (Faculty of Information Technology, Hanoi University — HANU).
3. **Core Contributions:**
   - **Sparse VSM with Subword N-grams:** Phân tích thực nghiệm cấu hình mẫu cố định `char_wb (3,5)` với sublinear TF và smooth IDF trên benchmark 120 câu (ghi chú rõ 35 câu `normal` trùng câu hỏi huấn luyện), đạt 0.943 full MRR (1.000 Hit@1 trên `normal` và `typo`).
   - **Typographic Resilience (E3b):** Đo lường đường cong suy thoái nhiễu (0 đến 3 lỗi hoán đổi ký tự liền kề trên 49 câu dev). `char_wb (3,5)` duy trì 1.000 Hit@1 ở $k \in \{0, 1, 3\}$ và 0.959 ở $k = 2$, trong khi word-level TF-IDF giảm xuống 0.837 ở $k = 3$.
   - **5-Fold Stratified Intent CV (E5b):** Đánh giá 9 mô hình phân loại trên 7 intents (112 tài liệu). Khẳng định Logistic Regression đạt Accuracy $0.876 \pm 0.074$ và Macro-F1 cao nhất ($0.872 \pm 0.085$), cung cấp xác suất hậu nghiệm cho cổng thứ hai.
   - **Dual-Gate Abstention Architecture:** Cơ chế kết hợp đồng thời $T_{\text{sim}} \ge 0.15$ và $T_{\text{intent}} \ge 0.34$, loại bỏ 100% (15/15) các câu hỏi ngoài kho tri thức (OOC) ngay cả khi chứa từ khóa gây nhiễu ("campus", "university"), đạt 96.19% (101/105) Top-3 delivered resolution (98.10% raw Hit@3) và 90.0% (108/120) E2E accuracy.
   - **Explainability:** Cơ chế phân rã điểm tích vô hướng tuyến tính `explain()` phục vụ việc kiểm toán và giải trình minh bạch trong môi trường quy chế học đường.
   - **Performance:** Thời gian phản hồi trung bình $1.4\text{ ms}$ cho truy vấn warm trên CPU cơ bản (sau ~361 ms khởi tạo/fit lần đầu), chi phí vận hành \$0, loại trừ hoàn toàn nguy cơ ảo giác (Zero-Hallucination).

## Cách xuất lại file PDF từ mã nguồn HTML

Nếu có thay đổi nội dung trong `ieee_report.html`, chạy lệnh sau từ thư mục gốc của repo:

```powershell
$tempPdf = "$env:TEMP\ieee_report_$(Get-Random).pdf"
$tempProfile = "$env:TEMP\chrome_pdf_profile_$(Get-Random)"
$htmlUrl = "file:///" + ((Resolve-Path "report\ieee_report.html").Path -replace "\\", "/")
$destPdf = "$PWD\report\report.pdf"

& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --no-sandbox --disable-gpu "--user-data-dir=$tempProfile" --no-pdf-header-footer "--print-to-pdf=$tempPdf" "$htmlUrl"
Copy-Item -Path $tempPdf -Destination $destPdf -Force
Remove-Item -Path $tempPdf -Force
Remove-Item -Path $tempProfile -Recurse -Force -ErrorAction SilentlyContinue
```
