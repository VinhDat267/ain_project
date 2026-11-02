# Tích hợp code mẫu midterm — 02/11/2026

Theo yêu cầu của nhóm, dùng thuật toán hoàn chỉnh trong mục 12 của
`Project12_Nghien_cuu_thuat_toan.md` làm nguồn cho bản tích hợp. Không chọn lại
thuật toán hoặc ngưỡng từ các kết quả test. Hạn nhóm xác nhận: 14/11/2026.

## Cấu hình đang chạy

- `student_core.DEFAULT_RETRIEVAL_CONFIG`: char_wb 3–5, sublinear TF,
  smooth IDF `ln((1+N)/(1+df))+1`, chuẩn hóa L2, cosine sàn 0,15.
- `student_core.DEFAULT_INTENT_CONFIG`: word TF-IDF sublinear,
  LogisticRegression C=10, max_iter=2000.
- Train: 112 text + 112 question/title + 7 mô tả intent = 231 mẫu.
- `retrieve()` trả top-k chỉ khi cosine >= 0,15 và confidence >= 0,34.
- Model và chỉ mục được dựng lazy một lần cho mỗi tiến trình.

Retrieval tiếp tục tự viết bằng Python/numpy. Analyzer `char_wb` được thêm
riêng để khớp việc padding dấu cách và giữ dấu câu của code mẫu sklearn;
analyzer `char` cũ vẫn giữ nguyên cho các thí nghiệm trước.

## API bổ sung, tương thích lời gọi cũ

```python
retrieve(query, top_k=3, threshold=None, intent_threshold=0.34)
```

`threshold=None` dùng ngưỡng trong cấu hình retrieval. Để lấy thứ hạng đầy đủ
cho đánh giá, gọi `retrieve(query, 112, threshold=-1, intent_threshold=None)`.
Confidence từ `classify_intent` là posterior của LR; fallback cosine cũ đã được
gỡ để lỗi huấn luyện được báo trực tiếp.

`IntentConfig` thêm `include_questions=False` và `sublinear_tf=False`.
`build_training_data` thêm `include_questions=False`; khi đánh giá LODO,
cả text và question của tài liệu bị giữ lại đều được bỏ khỏi train.
Mặc định riêng của bản sample bật questions, descriptions và sublinear TF.
NB/LR cho posterior; SVM chỉ dùng điểm softmax chuẩn hóa để so sánh,
chưa được calibration thành xác suất.

`experiments.evaluate.evaluate_run` thêm `intent_threshold=None`. Giá trị mặc
định giữ quy tắc cosine-only của thí nghiệm cũ; script `scripts/evaluate.py`
truyền rõ 0,34 để đánh giá đúng hai cổng của bản mẫu.

## Tái lập

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/evaluate.py
.\.venv\Scripts\python.exe -m streamlit run starter/app.py
```

Script đánh giá lưu per-query, summary, bảng ablation hai cổng và metadata gồm phiên bản thư viện,
cấu hình, ngưỡng intent, số mẫu train, overlap normal/train và SHA-256 source.
Full MRR của slide khác MRR@10 ở việc tài liệu đúng hạng 11 vẫn nhận 1/11.

Kết quả cấu hình cố định: full MRR 0,943088; intent accuracy 102/105;
end-to-end 108/120 gồm 93 câu hợp lệ trả đúng và 15 OOC bị từ chối.
35 câu normal trùng câu hỏi trong train. Đây là benchmark đã được kiểm tra,
không gắn nhãn kết quả này là CV hoặc unseen-test estimate.

Hai HTML/PDF trong `presentation/` đã cập nhật các điểm review: dữ liệu train,
sublinear TF, ví dụ IDF thống nhất, giới hạn lựa chọn n-gram, calibration/SVM,
fixed benchmark thay cho nhãn CV, và ablation hai cổng. Biểu đồ confidence
slide 7 giữ nguyên. CV gốc và đường cong nhiễu của kế hoạch cũ vẫn được tách
khỏi bản tích hợp thuật toán mẫu.
