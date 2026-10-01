# Ngân hàng câu hỏi vấn đáp — Project 12

> Mỗi người tự viết câu trả lời bằng lời của mình (việc **N08**, hạn T6 23/10). Phần B ghi lại sau mỗi buổi trinh sát thứ Bảy.

## A. Câu hỏi dự đoán

| # | Câu hỏi | Người trả lời chính | Trả lời (ngắn gọn) |
|---|---|---|---|
| 1 | Vì sao dùng cosine similarity mà không dùng khoảng cách Euclid? | Việt Anh | |
| 2 | IDF là gì? Vì sao lấy log? Một từ xuất hiện trong mọi tài liệu thì IDF bằng bao nhiêu? | Việt Anh | |
| 3 | Tính tay TF-IDF và cosine cho ví dụ 3 câu trên slide | Cả nhóm | |
| 4 | Naive Bayes "ngây thơ" ở chỗ nào? Laplace smoothing để làm gì? | Dương | |
| 5 | Vì sao chọn Naive Bayes (hoặc Logistic Regression) làm bộ phân loại intent cuối cùng? | Dương | |
| 6 | MRR là gì, khác Hit@1 thế nào? Vì sao P@3 tối đa chỉ là 1/3? | Vinh | |
| 7 | Ngưỡng từ chối chọn thế nào? Có bị overfit vào tập test không? | Vinh | |
| 8 | Câu `normal` chép nguyên văn FAQ, vậy kết quả có bị ảo không? LODO là gì? | Vinh | |
| 9 | Vì sao TF-IDF theo từ yếu với lỗi gõ? N-gram ký tự giải quyết được gì? | Việt Anh | |
| 10 | Theo kết quả của nhóm, câu `paraphrase` hay câu `typo` khó hơn? Vì sao? | Vinh | |
| 11 | Hệ thống này khác gì Project 10 (Ticket Router)? | Cả nhóm | |
| 12 | Thêm 1.000 tài liệu mới thì phải làm gì? Độ phức tạp của mỗi truy vấn là bao nhiêu? | Việt Anh | |
| 13 | Vì sao không dùng LLM hay embedding? Mô hình không gian vector có hạn chế gì? | Cả nhóm | |
| 14 | Hệ thống xử lý câu rỗng, câu toàn ký tự đặc biệt, câu tiếng Việt thế nào? | Dương | |
| 15 | Câu ngoài kho có từ "campus" lọt qua ngưỡng thì xử lý thế nào? | Vinh | |
| 16 | TF-IDF không có trong notes CS50. Nhóm lấy kiến thức từ đâu, và nó nối với nội dung nào của môn? (Gợi ý: mở rộng từ Bag-of-Words W6; xếp hạng theo cosine là nearest-neighbor W4) | Việt Anh | |
| 17 | Ghi chú của thầy viết "k-NN không phù hợp với văn bản thô". Vì sao nhóm vẫn xếp hạng theo kiểu nearest-neighbor trên TF-IDF? (Gợi ý: vector thưa, cosine đo các từ dùng chung chứ không đo khoảng cách Euclid, IDF làm nổi từ hiếm, kết quả thực nghiệm so với Jaccard) | Việt Anh | |
| 18 | Naive Bayes khác Logistic Regression và SVM ở bản chất nào? (mô hình sinh so với mô hình phân biệt) Trên dữ liệu 112 tài liệu, thuật toán nào hợp hơn, và kết quả E5 nói gì? | Dương | |
| 19 | k-NN cho intent (k = 1, 5) so với Naive Bayes thì sao? Vì sao không chọn k-NN làm mô hình cuối? | Dương | |
| 20 | Vì sao xác suất của SVM trong bảng chỉ là softmax của decision function? | Dương | |
| 21 | Nếu dùng word2vec hoặc Transformer (W6) thì câu paraphrase có tốt hơn không? Đổi lại mất gì? | Việt Anh | |
| 22 | Project này dùng kiến thức của những tuần nào trong môn? | Vinh | |
| 23 | Vì sao câu gõ sai một chữ hầu như không làm TF-IDF tìm sai? Khi nào lỗi gõ mới thật sự gây hại? (Gợi ý: các từ còn lại vẫn khớp; xem đường cong E3b khi có 2–3 lỗi) | Việt Anh | |
| 24 | Nhóm chọn cấu hình và ngưỡng thế nào mà không "nhìn trộm" tập test? Vì sao chọn theo 2 bước? | Vinh | |
| 25 | Kết quả 5-fold cross-validation có khớp với kết quả trên câu hỏi dev không? Nếu khác thì vì sao? | Dương | |

## B. Câu thầy đã hỏi các nhóm khác

### T7 10/10 — P01, P02, P03

| Nhóm | Câu hỏi của thầy | Nhóm mình rút ra được gì |
|---|---|---|
| | | |

### T7 17/10 — P04, P05, P06

| Nhóm | Câu hỏi của thầy | Nhóm mình rút ra được gì |
|---|---|---|
| | | |

### T7 24/10 — P07, P08, P09

| Nhóm | Câu hỏi của thầy | Nhóm mình rút ra được gì |
|---|---|---|
| | | |
