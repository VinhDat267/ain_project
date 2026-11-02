# Midterm presentation

Hai file HTML là nguồn, PDF là bản xuất từ Chromium. Mỗi bản có 13 slide,
giữ thiết kế 1280 × 720 px và font nhúng từ HTML nhóm cung cấp.

| Ngôn ngữ | HTML | PDF |
| --- | --- | --- |
| Tiếng Việt | [presentation.html](presentation.html) | [presentation.pdf](presentation.pdf) |
| English | [presentation_en.html](presentation_en.html) | [presentation_en.pdf](presentation_en.pdf) |

## Xuất lại PDF

Mở HTML bằng Chrome hoặc Edge, chờ biểu đồ hiển thị, nhấn Ctrl+P và chọn
Save as PDF. Bật background graphics, tắt headers/footers, scale 100%, không
thêm margins. CSS `@page` đặt sẵn khổ 1280 × 720 px; kiểm tra đủ 13 trang.
PDF xuất hiện tại có page box 960 × 540 pt, cùng tỷ lệ 16:9.

## Nguồn số liệu

Chạy từ gốc repo:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate.py
```

- `experiments/results/midterm-sample/summary.csv`: MRR, P@k, intent và end-to-end.
- `experiments/results/midterm-sample/per_query.csv`: kết quả từng câu và phân tích lỗi.
- `experiments/results/midterm-sample/ablation.csv`: không từ chối, cosine-only,
  intent-only và hai cổng. Tương ứng 95, 96, 108, 108 câu đúng trên 120.
- `config.json`: cấu hình, phiên bản thư viện, commit nguồn và hash mã nguồn.
- Các bảng so sánh lịch sử trên slide 6–7 được ghi nguồn là tài liệu nghiên cứu
  của nhóm. Script hiện tại tái lập cấu hình mẫu đã chọn và bảng ablation.

Mức 90% là kết quả cấu hình cố định trên benchmark đã được xem, không gắn nhãn
cross-validation. 35 câu normal trùng câu hỏi trong train. 231 mẫu train được
tạo từ 112 tài liệu và 7 mô tả intent; không phải 231 tài liệu độc lập.

## Các điểm đã sửa theo review

- Làm rõ 231 mẫu, posterior intent và hai điều kiện từ chối ở slide 4.
- Thống nhất smoothed IDF trong công thức và ví dụ (cosine D3 = 0,44), thêm
  sublinear TF/L2 và sửa diễn giải cosine ở slide 5.
- Ghi rõ char 2–4 có kết quả benchmark cao hơn; phạm vi kết luận của char 3–5.
- Sửa cách nói về SVM/calibration. Giữ nguyên màu và điểm biểu đồ slide 7.
- Tách fixed benchmark khỏi CV và đưa ablation vào slide 9.
- Dùng ID FAQ đầy đủ và bỏ gạch lượn ở typo trong bảng demo.
- Đồng bộ kết luận 108/120 và giới hạn tổng quát hóa ở cả hai ngôn ngữ.
