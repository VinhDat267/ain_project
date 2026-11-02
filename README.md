# Campus Notice & FAQ Assistant

Trợ lý trả lời câu hỏi hành chính cho sinh viên, xây bằng các kỹ thuật **truy hồi thông tin cổ điển**. Đây là Project 12 của môn **Trí tuệ nhân tạo (AIN)**, theo khung nội dung *CS50's Introduction to Artificial Intelligence with Python*.

[![project-12-tests](https://github.com/VinhDat267/ain_project/actions/workflows/project-12-tests.yml/badge.svg)](https://github.com/VinhDat267/ain_project/actions/workflows/project-12-tests.yml)

## Hệ thống làm gì

Người dùng gõ một câu hỏi tiếng Anh, ví dụ *"When is tuition due for the semester?"*. Hệ thống:

1. **Phân loại intent:** câu hỏi thuộc chủ đề nào trong 7 chủ đề (đăng ký học phần, thi, học phí, lịch học, dịch vụ sinh viên, tốt nghiệp, hỗ trợ kỹ thuật), kèm độ tin cậy.
2. **Truy hồi tài liệu:** tìm các FAQ và thông báo liên quan nhất bằng **TF-IDF và cosine similarity**, kèm điểm tương đồng và nguồn.
3. **Từ chối trả lời** khi câu hỏi nằm ngoài kho tài liệu, thay vì bịa ra câu trả lời.

Hệ thống không dùng LLM. Phần truy hồi tự viết bằng Python/numpy; phần phân loại intent dùng scikit-learn (Naive Bayes, Logistic Regression).

```text
câu hỏi ─► tokenize ─► vector TF-IDF ─► cosine với 112 tài liệu ─► xếp hạng ─► dưới ngưỡng? ─► top-k hoặc từ chối
   └─────► BoW / TF-IDF ─► Naive Bayes / Logistic Regression ─► (intent, độ tin cậy)
```

## Cài đặt và chạy

Cần **Python 3.11**.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Trên Windows (PowerShell), tạo venv bằng `py -3.11 -m venv .venv` và thay `.venv/bin/python` bằng `.\.venv\Scripts\python.exe` ở mọi lệnh.

Chạy kiểm thử (hai test kiểm tra stub của đề được deselect trong `pytest.ini`):

```bash
.venv/bin/python -m pytest -q
```

Mở ứng dụng demo:

```bash
.venv/bin/python -m streamlit run starter/app.py
```

## Bản midterm tích hợp từ tài liệu của nhóm

Phần code mẫu ở mục 12 của `Project12_Nghien_cuu_thuat_toan.md` đã được ghép
vào cấu trúc module hiện có:

- Retrieval: **TF-IDF char_wb 3–5, sublinear TF, L2 + cosine**, tự viết bằng numpy;
  được đối chiếu điểm số với scikit-learn.
- Intent: **TF-IDF từ + Logistic Regression, C = 10**, train trên 112 text,
  112 question/title và 7 mô tả intent. NB/SVM vẫn có thể dùng để so sánh.
- Trả kết quả khi **cosine >= 0,15 và max posterior intent >= 0,34**.
- App hiển thị intent/confidence, nội dung top-k, nguồn và cosine; có banner từ chối.

Tái lập số liệu của code đã ghép trên 120 câu benchmark:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate.py
```

Kết quả: full MRR **0,943**, intent accuracy **97,1%**, end-to-end **108/120**,
từ chối **15/15 OOC**. Script lưu `config.json`, `per_query.csv`, `summary.csv` và `ablation.csv`
vào `experiments/results/midterm-sample/`.

Đây là **tái lập cấu hình cố định trên benchmark đã được xem**, không phải kết quả
CV hay ước lượng trên tập test chưa đụng đến. Script báo cáo riêng full MRR của
slide và MRR@10 của bộ thí nghiệm cũ. Các bài so sánh cũ trong `experiments/`
vẫn giữ quy trình riêng; hai stub `intent_cv.py` và `noise_curve.py` không được
coi là đã hoàn thành bởi lần tích hợp này.

Chi tiết cấu hình và thay đổi API tương thích: [notes/midterm_integration.md](notes/midterm_integration.md).

Slide đã rà soát: [HTML tiếng Việt](presentation/presentation.html),
[HTML tiếng Anh](presentation/presentation_en.html),
[PDF tiếng Việt](presentation/presentation.pdf),
[PDF tiếng Anh](presentation/presentation_en.pdf).
Xem [cách xuất PDF và nguồn số liệu](presentation/README.md).

## Cấu trúc repo

| Đường dẫn | Nội dung |
|---|---|
| `starter/` | Code lõi: `retrieval.py` (TF-IDF, cosine), `intent.py` (phân loại intent), `student_core.py` (API công khai), `app.py` (giao diện Streamlit) |
| `experiments/` | Script đánh giá và thí nghiệm, tập câu hỏi dev, kết quả |
| `data/` | Kho tài liệu (84 FAQ, 28 thông báo) và 120 câu hỏi đánh giá của môn học, giữ nguyên bản gốc |
| `tests/` | Kiểm thử, gồm bộ sanity test của môn học |
| `notes/` | Tính tay, phân tích lỗi, ngân hàng câu hỏi vấn đáp |
| `scripts/` | Sinh dữ liệu của môn học và `evaluate.py` tái lập code mẫu midterm |

## Tài liệu của nhóm

- [PLAN.md](PLAN.md): kế hoạch Midterm, phân vai, danh sách việc và hạn chót, dàn ý thuyết trình.
- [INTERFACE.md](INTERFACE.md): hợp đồng kỹ thuật giữa các thành viên (chữ ký hàm, định dạng dữ liệu, cách đánh giá).
- [ASSIGNMENT.md](ASSIGNMENT.md): đề bài gốc của môn học.
- [notes/learning_path.md](notes/learning_path.md): lộ trình học cho từng thành viên, kèm link tài liệu.

## Nhóm

| Thành viên | Vai trò |
|---|---|
| Nguyễn Đạt Vinh (nhóm trưởng) | Đánh giá, thí nghiệm, điều phối |
| Lương Việt Anh | Truy hồi (TF-IDF, cosine) |
| Nguyễn Ánh Dương | Phân loại intent, ứng dụng demo |

## Nguồn

Đề bài, dữ liệu, code khung và bộ sanity test lấy từ bộ đề của môn học: [vinhnt21/ain-projects](https://github.com/vinhnt21/ain-projects).
