# IEEE Conference Research Paper — Project 12

Tài liệu báo cáo khoa học hoàn chỉnh theo chuẩn định dạng hội nghị quốc tế IEEE (2 cột, chuẩn font Times New Roman, công thức toán học KaTeX/MathJax, bảng biểu đối chiếu thực nghiệm E0–E7, E3b, E5b, và các hình đồ thị trực quan).

## Các phiên bản tài liệu

| Định dạng | Đường dẫn | Mô tả |
|---|---|---|
| **HTML** | [`ieee_report.html`](ieee_report.html) | Bản nguồn chuẩn web, hỗ trợ responsive, render hình ảnh và định dạng 2 cột theo CSS `@page`. |
| **PDF** | [`report.pdf`](report.pdf) | Bản xuất PDF hoàn chỉnh (517 KB) chất lượng cao xuất từ Chromium headless. |

## Tóm tắt nội dung học thuật chính

1. **Title:** *Deterministic Dual-Gate Information Retrieval and Intent Classification for University Administrative Regulations*
2. **Authors:** Viet-Anh Luong, Vinh-Dat Pham, and Quang-Duong Nguyen (Faculty of Information Technology, VNU-HCM University of Science).
3. **Core Contributions:**
   - **Sparse VSM with Subword N-grams:** Phân tích thực nghiệm tính ưu việt của `char_wb (3,5)` với sublinear TF và smooth IDF, đạt 1.000 Hit@1 và 1.000 MRR@10 trên các câu hỏi in-corpus và typo.
   - **Typographic Resilience (E3b):** Đo lường đường cong suy thoái nhiễu (0 đến 3 lỗi hoán đổi ký tự liền kề). Chứng minh `char_wb` duy trì độ chính xác tuyệt đối ngay cả khi word-level TF-IDF sụp đổ xuống 0.837.
   - **5-Fold Stratified Intent CV (E5b):** Đánh giá 9 mô hình phân loại trên 13 intents. Khẳng định Logistic Regression đạt Macro-F1 cao nhất ($0.872 \pm 0.085$) và cung cấp xác suất hậu nghiệm tin cậy cho cơ chế chặn cổng.
   - **Dual-Gate Abstention Architecture:** Cơ chế kết hợp đồng thời $T_{\text{sim}} \ge 0.15$ và $T_{\text{intent}} \ge 0.34$, loại bỏ 100% các câu hỏi ngoài kho tri thức (OOC) ngay cả khi chứa từ khóa gây nhiễu ("campus", "university").
   - **Explainability:** Cơ chế phân rã điểm tích vô hướng tuyến tính `explain()` phục vụ việc kiểm toán và giải trình minh bạch trong môi trường quy chế học đường.
   - **Performance:** Thời gian phản hồi $< 2\text{ ms}$ trên CPU cơ bản, chi phí vận hành $0\$, loại trừ hoàn toàn nguy cơ ảo giác (Zero-Hallucination).

## Cách xuất lại file PDF từ mã nguồn HTML

Nếu có thay đổi nội dung trong `ieee_report.html`, chạy lệnh sau từ thư mục gốc của repo:

```powershell
$tempPdf = "$env:TEMP\ieee_report_$(Get-Random).pdf"
$htmlPath = "$PWD\report\ieee_report.html"
$destPdf = "$PWD\report\report.pdf"

& "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --headless=new --no-sandbox --disable-gpu "--print-to-pdf=$tempPdf" "$htmlPath"
Copy-Item -Path $tempPdf -Destination $destPdf -Force
Remove-Item -Path $tempPdf -Force
```
