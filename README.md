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

Mở ứng dụng demo (Streamlit gốc):

```bash
.venv/bin/python -m streamlit run starter/app.py
```

Mở ứng dụng web độc lập (FastAPI + React/TypeScript, chạy song song với `starter/app.py` trên port `8000`):

```powershell
# Chạy 1 lệnh local (tự build frontend nếu chưa có và phục vụ tại http://127.0.0.1:8000)
.\scripts\run_webapp.ps1

# Hoặc chế độ dev (FastAPI reload + Vite HMR tại http://127.0.0.1:5173)
.\scripts\run_webapp.ps1 -Dev

# Hoặc đóng gói và chạy bằng Docker (port 8000)
docker compose up --build
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
slide và MRR@10 của bộ thí nghiệm cũ. Toàn bộ các bài thực nghiệm so sánh trong `experiments/`
đã được hoàn thiện đầy đủ:
- `experiments/noise_curve.py` (E3b): Đo lường suy thoái nhiễu chính tả 0..3 lỗi gõ, lưu tại `experiments/results/dev/noise_curve.csv` và hình vẽ `experiments/results/figures/noise_curve.png`.
- `experiments/intent_cv.py` (E5b): 5-fold Stratified Cross-Validation cho 9 mô hình phân loại intent, lưu tại `experiments/results/dev/intent_cv.csv`.
- `experiments/run_ablation.py`: Chạy đầy đủ các nhóm E0, E1, E2, E3 (char_wb), E4 (hybrid) và E7 (BM25).

Chi tiết cấu hình và thay đổi API tương thích: [notes/midterm_integration.md](notes/midterm_integration.md).

Slide đã rà soát: [HTML tiếng Việt](presentation/presentation.html),
[HTML tiếng Anh](presentation/presentation_en.html),
[PDF tiếng Việt](presentation/presentation.pdf),
[PDF tiếng Anh](presentation/presentation_en.pdf).
Xem [cách xuất PDF và nguồn số liệu](presentation/README.md), [lời dẫn thuyết trình 10 phút](presentation/speaker_notes_vi_10min.md), cùng [kịch bản live demo 90s](presentation/LIVE_DEMO.md) ([danh sách câu hỏi demo](presentation/demo_queries.txt)).

Bài báo nghiên cứu chuẩn IEEE: [Bản PDF](report/report.pdf) · [Bản nguồn HTML](report/ieee_report.html) · [README](report/README.md).

## Tái lập số liệu của báo cáo cuối kỳ

Repo GitHub: <https://github.com/VinhDat267/ain_project>. Cần Python 3.11; trên Windows thay
`.venv/bin/python` bằng `.\.venv\Scripts\python.exe`. Các lệnh dưới đây khớp với Phụ lục A của báo cáo.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q                         # 133 passed, 2 deselected
.venv/bin/python -m streamlit run starter/app.py      # 1 lệnh chạy ứng dụng
.venv/bin/python scripts/evaluate.py                  # Bảng 3 và 5 (benchmark 120 câu)
.venv/bin/python scripts/evaluate.py --split dev      # Bảng 3 và 5 (tập dev 146 câu)
.venv/bin/python experiments/run_ablation.py --split test --final   # baseline của Bảng 3
.venv/bin/python experiments/run_ablation.py --split dev --group E0 # tương tự E1, E2, E3, E4, E5, E7
.venv/bin/python experiments/intent_cv.py             # Bảng 4
.venv/bin/python experiments/noise_curve.py           # đường cong lỗi chính tả, mục 4.3
.venv/bin/python experiments/scenarios.py             # Bảng 6 (14 kịch bản)
.venv/bin/python experiments/business_metrics.py      # top-3 trả đúng 101/105
```

Batch `--split test --final` đã chạy một lần và ghi `experiments/results/test/LOCK`; muốn chạy lại phải thêm
`--rerun-reason "<lý do>"`. File Word của báo cáo được dựng bằng `report/build_final_report.py`
(nội dung ở `report/report_content.py`), rồi `report/finalize_report.ps1` để Word cập nhật mục lục.

## Cấu trúc repo

| Đường dẫn | Nội dung |
|---|---|
| `starter/` | Code lõi: `retrieval.py` (TF-IDF, cosine, `explain`), `intent.py` (phân loại intent), `student_core.py` (API công khai), `app.py` (giao diện Streamlit) |
| `webapp/` | Ứng dụng web độc lập: backend FastAPI (`webapp/backend/`) và giao diện React/TypeScript (`webapp/frontend/`), đóng gói qua `Dockerfile` và `docker-compose.yml` |
| `experiments/` | Script đánh giá và thí nghiệm (E0–E7, E3b, E5b), tập câu hỏi dev (146 câu), kết quả và biểu đồ |
| `data/` | Kho tài liệu (84 FAQ, 28 thông báo) và 120 câu hỏi đánh giá của môn học, giữ nguyên bản gốc |
| `report/` | Bộ sinh báo cáo cuối kỳ Word theo template chính thức (`build_final_report.py`, `report_content.py`, `finalize_report.ps1`) và bài báo chuẩn IEEE (`ieee_report.html`, `report.pdf`) |
| `tests/` | Kiểm thử tự động (133 active unit & integration tests, 2 deselected sanity stub tests) |
| `notes/` | Tính tay (TF-IDF & Naive Bayes), phân tích lỗi, phân tích kho dữ liệu, quy trình chọn cấu hình, ngân hàng câu hỏi vấn đáp |
| `scripts/` | Sinh dữ liệu của môn học, `evaluate.py` tái lập code mẫu midterm và `run_webapp.ps1` |

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
