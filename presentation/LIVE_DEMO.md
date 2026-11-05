# Demo live trên trình duyệt — 90 giây

## Mở app

Từ PowerShell tại gốc repo:

```powershell
Set-Location -LiteralPath 'D:\Môn Học\AIN\ProjectAIN'
.\.venv\Scripts\python.exe -m streamlit run starter/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Mở <http://127.0.0.1:8501/> bằng Chrome/Edge. Giữ terminal chạy trong lúc demo.
Nếu app đang chạy ở địa chỉ trên thì dùng luôn phiên hiện tại.
Nhập câu hỏi tiếng Anh rồi bấm **Retrieve documents**. Nút này hiển thị cả intent
và tài liệu; không cần bấm **Classify intent** trước.

Đây là app chạy thuật toán Python trên dữ liệu repo: thay nội dung câu hỏi và
bấm nút sẽ tính lại kết quả. Không cần API key hoặc dịch vụ AI bên ngoài.

## Thứ tự demo

Copy từng dòng từ [demo_queries.txt](demo_queries.txt), thay câu cũ trong ô nhập,
rồi bấm **Retrieve documents**. Lời dẫn chi tiết nằm trong
[speaker_notes_vi_10min.md](speaker_notes_vi_10min.md).

| Thời gian | Tình huống | Kết quả đã thấy trên trình duyệt |
| --- | --- | --- |
| 0–15 giây | Câu chuẩn về mật khẩu | technical_support 88%; faq_technical_support_01 đứng đầu, cosine 0.54 |
| 15–25 giây | Gõ sai Student thành Sutdent | Vẫn cùng FAQ; intent 90%, cosine 0.53 |
| 25–40 giây | Diễn đạt lại câu mật khẩu | Vẫn cùng FAQ; intent 85%, cosine 0.51 |
| 40–50 giây | Hỏi nhà hàng chay | Intent 31%; hiện “Information not found — please contact the administrative office.” |
| 50–65 giây | Hỏi thuê kayak trong campus | Intent 29%; cũng từ chối dù có từ campus |
| 65–90 giây | Trùng lịch thi cuối kỳ | Sai top-1: faq_class_schedule_02, cosine 0.27; FAQ đúng faq_exam_02 ở hạng 2, cosine 0.19 |

Với hai câu ngoài phạm vi, giải thích rằng độ tin cậy intent thấp hơn ngưỡng 0.34.
Với câu cuối, chỉ rõ hệ thống còn nhầm “lịch học” với “lịch thi”; không gọi đây là
câu trả lời đúng. Điểm cosine và posterior intent đo hai khía cạnh khác nhau,
không phải xác suất câu trả lời đúng.

## Kiểm tra thực tế

Đã nhập và bấm nút cả sáu câu trên trình duyệt ngày 03/11/2026.
Sáu tình huống khớp kịch bản, gồm cả lỗi xếp hạng cố ý trình bày ở cuối.
Không ghi nhận lỗi hoặc cảnh báo JavaScript trong phiên kiểm tra.
Đây là kiểm tra sáu tình huống demo, không thay thế đánh giá toàn bộ benchmark.

Ảnh và nội dung hiển thị được lưu tại
[output/playwright/live-demo](../output/playwright/live-demo/);
[observations.json](../output/playwright/live-demo/observations.json) chứa câu hỏi
và nội dung trả về đã đọc từ trang.

Nếu máy vừa khởi động lại, chạy lại lệnh trên trước giờ thuyết trình.
Khi trình chiếu, chuyển từ slide demo sang tab app bằng Alt+Tab, rồi quay lại slide.

