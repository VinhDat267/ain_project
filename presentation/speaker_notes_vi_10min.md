# Lời thuyết trình midterm — 1 người, tiếng Việt, 10 phút

**Bản dùng cùng:** `presentation.html` / `presentation.pdf`, 13 slide đã rà soát.
**Nguồn đối chiếu:** `main` tại `f36d4c5`; kết quả trong `experiments/results/midterm-sample/`.

Chỉ đọc phần trích dẫn. Các dòng **Thao tác**, **Nhấn** và bảng thời gian là
ghi chú cho người trình bày. Xưng “em” khi nói, dùng “nhóm em” để chỉ cả nhóm;
không có phần chuyển người nói.

Khung dưới đây dành **9 phút 30 giây**, gồm **90 giây demo**, để lại **30 giây
dự phòng**. Đây là phân bổ để tập, chưa phải thời lượng đo được từ giọng nói
của bạn. Khi luyện, bấm giờ cả thao tác chuyển cửa sổ và chạy truy vấn.

## Phân bổ thời gian

| Slide | Nội dung | Khoảng thời gian | Số giây |
| --- | --- | --- | ---: |
| 1 | Giới thiệu | 00:00–00:20 | 20 |
| 2 | Bài toán và đầu ra | 00:20–00:50 | 30 |
| 3 | Dữ liệu và thách thức | 00:50–01:25 | 35 |
| 4 | Pipeline | 01:25–02:10 | 45 |
| 5 | TF-IDF, cosine, n-gram | 02:10–03:20 | 70 |
| 6 | So sánh retrieval | 03:20–04:05 | 45 |
| 7 | Phân loại intent | 04:05–04:55 | 50 |
| 8 | Robustness và chỉ số | 04:55–05:35 | 40 |
| 9 | Ngưỡng và ablation | 05:35–06:30 | 55 |
| 10 | Phân tích lỗi | 06:30–07:05 | 35 |
| 11 | Demo sáu câu | 07:05–08:35 | 90 |
| 12 | Kết luận và giới hạn | 08:35–09:20 | 45 |
| 13 | Kết thúc | 09:20–09:30 | 10 |
| — | Dự phòng | 09:30–10:00 | 30 |

## Slide 1 — Giới thiệu · 00:00–00:20

> Em chào thầy và các bạn. Em xin đại diện nhóm trình bày Project 12, Campus FAQ
> Assistant, trợ lý tìm câu trả lời trong các câu hỏi thường gặp và thông báo
> của trường. Bài này sử dụng thuật toán cổ điển chạy offline, với ba việc chính:
> tìm tài liệu, phân loại chủ đề và từ chối khi không đủ liên quan.

**Nhấn:** tên bài toán và ba việc chính. Không đọc danh sách thành viên hoặc mã sinh viên.

## Slide 2 — Bài toán và đầu ra · 00:20–00:50

> Ví dụ, sinh viên hỏi cách đặt lại mật khẩu thì hệ thống cần tìm đúng FAQ.
> Khi câu hỏi bị gõ sai, kết quả vẫn nên giữ nguyên. Còn câu hỏi về quán ăn gần
> trường không có đáp án trong kho thì hệ thống cần từ chối.
>
> Nhóm triển khai hai hàm: classify_intent trả chủ đề cùng độ tin cậy;
> retrieve trả các tài liệu được xếp hạng cùng điểm tương đồng. Khi từ chối,
> retrieve trả danh sách rỗng. Hệ thống lấy nội dung từ kho có sẵn và không gọi API LLM.

**Nhấn:** truy hồi nội dung trong kho; không mô tả đây là mô hình sinh câu trả lời.

## Slide 3 — Dữ liệu và thách thức · 00:50–01:25

> Kho có 112 tài liệu, gồm 84 FAQ và 28 thông báo, thuộc bảy chủ đề hành chính.
> Bộ đánh giá có 120 câu: 35 câu chuẩn, 35 câu diễn đạt lại, 35 câu gõ sai
> và 15 câu ngoài phạm vi, gọi tắt là OOC.
>
> Có ba khó khăn: cùng ý nhưng khác từ; lỗi gõ làm thay đổi từ; và câu ngoài
> phạm vi vẫn tình cờ trùng từ với kho. Vì vậy, điểm tương đồng cao chưa đủ
> để kết luận câu hỏi có đáp án. Nhóm đánh giá riêng từng loại câu để nhìn
> rõ các giới hạn này.

**Thao tác:** chỉ lần lượt ba nhóm thách thức bên phải. Không đọc cả bảy tên intent.

## Slide 4 — Pipeline · 01:25–02:10

> Một câu hỏi được đưa qua hai nhánh. Nhánh retrieval dùng TF-IDF ký tự và
> cosine, cho danh sách tài liệu cùng điểm s. Nhánh phân loại dùng TF-IDF từ
> và Logistic Regression, cho một intent cùng điểm p cao nhất trong bảy lớp.
>
> Bộ phân loại học từ 231 mẫu văn bản: 112 phần nội dung, 112 câu hỏi hoặc
> tiêu đề, và bảy mô tả intent. Các mẫu này được tạo từ 112 tài liệu,
> nên không phải 231 tài liệu độc lập.
>
> Hệ thống chỉ trả tài liệu khi s đạt ít nhất 0,15 và p đạt ít nhất 0,34.
> Hai điểm này phục vụ hai vai trò: độ giống với tài liệu và mức tập trung
> vào một chủ đề. Phần sau sẽ kiểm tra đóng góp của từng cổng.

**Nhấn:** s và p là hai đại lượng khác nhau. Sơ đồ biểu diễn hai nhánh độc lập về chức năng;
không khẳng định chương trình dùng hai luồng chạy đồng thời.

## Slide 5 — TF-IDF, cosine và n-gram · 02:10–03:20

> Để máy tính so sánh được văn bản, nhóm biến mỗi câu thành vector đặc trưng.
> TF-IDF cho trọng số cao hơn với đặc trưng xuất hiện trong tài liệu này
> nhưng ít xuất hiện trong cả kho.
>
> Bản triển khai dùng sublinear TF, tức một cộng log của số lần xuất hiện,
> để giảm tác động của việc lặp từ. IDF dùng công thức có smoothing trên slide.
> Sau đó, mỗi vector được chuẩn hóa L2 về độ dài một.
>
> Cosine so hướng của hai vector. Vì đã chuẩn hóa L2, phép nhân vô hướng
> giữa vector câu hỏi và vector tài liệu chính là điểm cosine.
>
> Trong ví dụ ba tài liệu, câu hỏi khớp D1 được điểm một. D3 chỉ chung một phần
> từ nên được khoảng 0,44; D2 không có đặc trưng chung nên được không.
> Các điểm này đều dùng cùng công thức IDF có smoothing.
>
> Với retrieval, đơn vị đếm là cụm ba đến năm ký tự trong ranh giới từ.
> “Connect” và bản gõ sai “conncet” vẫn chung một số cụm ký tự.
> Vì thế, một lỗi gõ thường chỉ phá một phần đặc trưng của câu.

**Thao tác:** chỉ công thức TF-IDF, công thức cosine, rồi ba thanh điểm.
Không đọc từng ký hiệu của công thức thành tiếng.

## Slide 6 — So sánh retrieval · 03:20–04:05

> Nhóm dùng Bag-of-Words làm mốc và so sánh với TF-IDF từ, ký tự,
> hybrid, BM25 và LSA. MRR đo trung bình nghịch đảo thứ hạng tài liệu đúng,
> nên tài liệu đúng đứng càng cao thì chỉ số càng tốt.
>
> Trong tám cấu hình trên bảng, char ba đến năm đạt MRR 0,943,
> so với khoảng 0,893 của Bag-of-Words và 0,927 của TF-IDF từ.
> P@1 trên câu diễn đạt lại đạt khoảng 71%.
>
> Nhóm cũng ghi nhận char hai đến bốn đạt MRR 0,953 trên cùng benchmark.
> Bản hiện tại giữ ba đến năm để nhất quán với code mẫu và demo.
> Vì đã xem benchmark, nhóm chưa kết luận cấu hình nào tổng quát hóa tốt nhất.

**Nhấn:** MRR là điểm chất lượng xếp hạng; 0,943 không phải tỉ lệ top-1 đúng 94,3%.
Không đọc cả tám dòng hoặc gọi 3–5 là cấu hình tối ưu tuyệt đối.

## Slide 7 — Phân loại intent · 04:05–04:55

> Với intent, nhóm chọn Logistic Regression. Mô hình học trọng số cho các
> đặc trưng TF-IDF từ, rồi dùng softmax để tạo phân phối trên bảy nhãn.
> Nhãn có điểm cao nhất là kết quả phân loại.
>
> Đây là mô hình phân biệt, học trực tiếp cách phân chia các lớp.
> Naive Bayes là mô hình sinh, dựa trên giả định các đặc trưng độc lập
> khi đã biết lớp. Trên 105 câu trong phạm vi, LR đạt 97,1%,
> còn baseline BoW cộng Naive Bayes đạt 94,3%.
>
> Với LR, confidence trung bình là 0,74 ở câu trong phạm vi và 0,26 ở OOC.
> Sự khác biệt này hữu ích cho từ chối. Tuy nhiên, nhóm chưa đo calibration,
> nên chưa coi confidence là xác suất câu trả lời thực tế đúng.
> LinearSVC có decision score; để có xác suất cần thêm bước calibration.

**Thao tác:** chỉ chấm xanh 0,74 và chấm cam 0,26.
**Nhấn:** p là posterior lớn nhất trong bảy intent, không phải xác suất câu hỏi có đáp án trong kho.

## Slide 8 — Robustness và cách đọc chỉ số · 04:55–05:35

> Khi tách theo loại câu, retrieval đạt P@1 bằng một ở normal và typo,
> nhưng chỉ khoảng 0,714 ở paraphrase. Dù vậy, 33 trên 35 câu paraphrase
> vẫn có tài liệu đúng trong top ba.
>
> P@3 tối đa là một phần ba vì bộ đánh giá chỉ gán một tài liệu đúng
> cho mỗi câu. Vì thế, Hit@3 giúp diễn giải khả năng tìm thấy đáp án dễ hơn.
>
> Hai giới hạn cần lưu ý: 35 câu normal trùng câu hỏi dùng huấn luyện intent;
> còn typo chỉ là một lần đảo hai chữ cái trong một từ.
> Kết quả này cho thấy hệ thống xử lý tốt mức nhiễu đã thử,
> chưa chứng minh độ bền với mọi loại lỗi gõ.

## Slide 9 — Ngưỡng từ chối và ablation · 05:35–06:30

> Đường bên trái cho thấy nâng ngưỡng cosine giúp chặn thêm OOC,
> nhưng cũng làm mất câu hợp lệ. Tại ngưỡng 0,28, hệ thống trả đúng
> 91 trên 105 câu hợp lệ và chặn 11 trên 15 OOC, tổng cộng 102 trên 120.
>
> Bảng bên phải là thí nghiệm tắt từng cổng. Không từ chối thì đúng 95 câu.
> Chỉ dùng sàn cosine 0,15 thì đúng 96 câu. Chỉ dùng confidence 0,34
> và dùng cả hai cổng đều đúng 108 câu, chặn đủ 15 OOC.
>
> Như vậy, cổng intent tạo ra phần cải thiện quan sát được.
> Cosine giữ vai trò mức sàn similarity, đồng thời đáp ứng yêu cầu từ chối
> theo similarity của đề; nó chưa làm tăng thêm accuracy so với chỉ dùng
> intent trong bộ này.
>
> Đây là kết quả cấu hình cố định trên benchmark đã xem,
> không phải kết quả cross-validation hay bảo đảm đạt 90% trên câu hỏi mới.

**Nhấn:** bảng ablation dùng số câu đúng trên 120; đường xanh dùng số câu hợp lệ
trả lời đúng chia 105. Tránh gọi đường xanh là coverage hoặc “tỉ lệ câu được giữ lại”.

## Slide 10 — Phân tích lỗi · 06:30–07:05

> Trước khi áp dụng cổng từ chối, cả mười lỗi xếp hạng đều nằm ở paraphrase.
> Ví dụ người dùng hỏi hai bài thi cuối kỳ trùng giờ,
> hệ thống lại trả FAQ về hai lớp học trùng lịch.
> Đây là trường hợp khớp cụm chữ nhưng chưa phân biệt đúng ngữ cảnh.
>
> Bảy trong mười lỗi có tài liệu đúng ở hạng hai, nên hiển thị top ba
> giúp người dùng tiếp cận đáp án trong nhiều trường hợp.
> Hướng cải thiện là từ điển đồng nghĩa theo domain và trọng số riêng
> cho phần câu hỏi. Sau đây em minh họa cả kết quả đúng và một lỗi này.

## Slide 11 — Demo trực tiếp · 07:05–08:35

**Chuẩn bị trước giờ nói:** khởi động app, mở sẵn trình duyệt và file
`demo_queries.txt`. Thử một truy vấn để model/chỉ mục đã được nạp.
Giữ hai cửa sổ slide và app sẵn để chuyển bằng Alt+Tab.

**Thao tác chung cho mỗi câu:** copy một dòng từ file, dán vào ô câu hỏi,
bấm **Retrieve documents**. Nút này hiển thị cả intent/confidence và kết quả
truy hồi; không cần bấm thêm nút phân loại.

### 07:05–07:17 — Câu chuẩn

```text
How do I reset my Student Portal password?
```

> Câu chuẩn tìm đúng FAQ đặt lại mật khẩu, với cosine khoảng 0,54.

**Đối chiếu trên màn hình:** `faq_technical_support_01`; intent `technical_support`.

### 07:17–07:29 — Câu gõ sai

```text
How do I reset my Sutdent Portal password?
```

> Em đổi “Student” thành “Sutdent”. Hệ thống vẫn tìm đúng FAQ đó,
> điểm giảm nhẹ còn khoảng 0,53.

### 07:29–07:41 — Câu diễn đạt lại

```text
I forgot my Student Portal password - how do I reset it?
```

> Cách diễn đạt thay đổi nhưng vẫn còn đủ đặc trưng chung,
> nên kết quả này đúng, với điểm khoảng 0,51.

### 07:41–07:55 — Câu ngoài phạm vi

```text
What's the best restaurant near campus for vegan food?
```

> Câu về quán ăn bị từ chối. Confidence intent khoảng 31%,
> thấp hơn ngưỡng 34%.

### 07:55–08:11 — OOC có cosine khá cao

```text
Can I rent a kayak from the campus recreation center?
```

> Câu này có cosine khoảng 0,39 nên qua được sàn cosine 0,15.
> Confidence chỉ khoảng 29%, vì vậy cổng intent chặn nó.

### 08:11–08:29 — Câu sai có chủ đích

```text
Two of my finals overlap on the same day - who do I tell?
```

> Câu cuối bị trả sai FAQ về lịch học. FAQ đúng về lịch thi nằm ở hạng hai.
> Trường hợp này cho thấy vượt qua hai cổng vẫn chưa bảo đảm top một đúng.

**Đối chiếu:** top-1 `faq_class_schedule_02`, top-2 `faq_exam_02`.

### 08:29–08:35 — Trở lại slide

**Thao tác:** chuyển về slide 12.

**Nếu demo bị gián đoạn:** dành tối đa khoảng 10 giây xử lý. Nếu chưa khắc phục
được, nói rõ “App đang gặp trục trặc trong lượt demo này, em xin đối chiếu
các kết quả đã đo ở bảng trên slide” và quay lại slide. Không gọi bảng số liệu
hoặc video dự phòng là kết quả vừa chạy trực tiếp.

## Slide 12 — Kết luận và giới hạn · 08:35–09:20

> Nhóm chọn TF-IDF ký tự cộng cosine cho retrieval, TF-IDF từ cộng
> Logistic Regression cho intent, và hai điều kiện từ chối.
> Các kết quả chính đã tái lập từ code: MRR khoảng 0,943,
> intent accuracy 97,1%, và đầu-cuối 108 trên 120, tương đương 90%.
>
> Điểm mạnh là mô hình gọn, chạy offline và giải thích được cách xếp hạng.
> Giới hạn lớn nhất vẫn là paraphrase. Bộ OOC chỉ có 15 câu,
> và confidence cao nhất khoảng 0,33, sát ngưỡng 0,34.
> Vì cấu hình đã được nghiên cứu trên benchmark này,
> nhóm cần câu hỏi mới để đánh giá khả năng tổng quát hóa.
>
> Với bản final, nhóm dự kiến thử từ điển đồng nghĩa theo domain,
> trọng số riêng cho câu hỏi và hoàn thiện giao diện có thanh trượt ngưỡng.

## Slide 13 — Kết thúc · 09:20–09:30

> Phần trình bày của em đến đây là kết thúc. Em cảm ơn thầy và các bạn
> đã lắng nghe. Em xin nhận câu hỏi cho nhóm.

## Thẻ nhắc nhanh khi tập

| Slide | Chỉ cần nhớ |
| --- | --- |
| 1–2 | Tìm tài liệu, phân loại, từ chối. Hai API. |
| 3 | 112 tài liệu; 120 câu; khác từ, lỗi gõ, trùng từ tình cờ. |
| 4 | Hai nhánh; 231 mẫu; s = 0,15 và p = 0,34. |
| 5 | Sublinear TF, smoothed IDF, L2, dot = cosine; D3 = 0,44; char 3–5. |
| 6 | MRR 0,943; 2–4 có 0,953; giới hạn kết luận. |
| 7 | LR 97,1%; NB 94,3%; confidence 0,74/0,26; chưa đo calibration. |
| 8 | P@1: 1 / 0,714 / 1; paraphrase Hit@3 = 33/35; normal đã có trong train. |
| 9 | Đúng 95 / 96 / 108 / 108; cổng intent tạo cải thiện; fixed benchmark. |
| 10 | 10 lỗi paraphrase; 7 lỗi có đáp án hạng 2. |
| 11 | Chuẩn, typo, paraphrase, quán ăn, kayak, finals. |
| 12–13 | 108/120; giới hạn OOC và benchmark; cảm ơn. |

## Nếu tập bị quá giờ

Giữ phần công thức cốt lõi, ablation, demo và các giới hạn. Có thể rút:

- Slide 3: đọc số lượng chung rồi chỉ ba thách thức, tiết kiệm khoảng 10 giây.
- Slide 6: giữ BoW, TF-IDF từ và char; nhắc BM25/LSA là đối thủ đã so sánh,
  tiết kiệm khoảng 10 giây.
- Slide 10: chỉ kể ví dụ trùng lịch thi và số 7/10, tiết kiệm khoảng 10 giây.

Các mức tiết kiệm là ước lượng để tập lại, không cộng dồn như thời gian đã đo.

## Mở code khi được hỏi — không đọc trong bài 10 phút

- `starter/retrieval.py`: `_extract_char_tokens` tạo char_wb;
  `_build_tfidf_matrix` tính TF-IDF/L2; `rank` nhân vector và xếp hạng.
- `starter/intent.py`: `build_training_data` tạo mẫu; `fit` huấn luyện;
  `predict_proba` lấy phân phối nhãn.
- `starter/student_core.py`: cấu hình mẫu, cache model/index và hai cổng trong `retrieve`.
- `scripts/evaluate.py`: báo cáo ranking, end-to-end, metadata và ablation;
  script này không chạy cross-validation.

**Phân biệt khi trả lời:** 25/35 paraphrase đúng top-1 trước cổng; sau khi
áp dụng hai cổng, 23/35 paraphrase được trả đúng. Tổng 108/120 gồm 93 câu
trong phạm vi trả đúng và 15 OOC từ chối đúng.
