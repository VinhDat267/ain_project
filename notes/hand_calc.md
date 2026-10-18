# Ví dụ tính tay TF-IDF và Cosine Similarity

> Tài liệu thực hiện: **Lương Việt Anh** (Việc **A01**, hạn T7 03/10/2026).  
> Phục vụ: **Slide 8**, **Phụ lục P1**, và trả lời vấn đáp câu hỏi 1, 2, 3 trong `notes/qa_bank.md`.

---

## 1. Dữ liệu mẫu (3 tài liệu ngắn và 1 truy vấn)

Xét kho tài liệu gồm $N = 3$ tài liệu ngắn sau khi tiền xử lý (lowercase, bỏ dấu câu và stopwords):

- **Tài liệu 1 ($D_1$):** `"tuition fees due semester"` (4 từ)
- **Tài liệu 2 ($D_2$):** `"exam schedule posted semester"` (4 từ)
- **Tài liệu 3 ($D_3$):** `"tuition payment deadline"` (3 từ)

**Câu hỏi truy vấn ($Q$):** `"tuition semester deadline"` (3 từ)

---

## 2. Bộ từ vựng và Document Frequency ($df$)

Tập hợp tất cả các từ phân biệt tạo thành bộ từ vựng $V$ gồm 9 từ (sắp xếp theo bảng chữ cái):

$$\mathcal{V} = \{\text{deadline}, \text{due}, \text{exam}, \text{fees}, \text{payment}, \text{posted}, \text{schedule}, \text{semester}, \text{tuition}\}$$

Tần số xuất hiện trong tài liệu ($df(t)$ là số lượng tài liệu chứa từ $t$):

| Từ ($t$) | Xuất hiện ở | $df(t)$ |
|---|---|---|
| `deadline` | $D_3$ | 1 |
| `due` | $D_1$ | 1 |
| `exam` | $D_2$ | 1 |
| `fees` | $D_1$ | 1 |
| `payment` | $D_3$ | 1 |
| `posted` | $D_2$ | 1 |
| `schedule` | $D_2$ | 1 |
| `semester` | $D_1, D_2$ | 2 |
| `tuition` | $D_1, D_3$ | 2 |

---

## 3. Công thức tính IDF (Chuẩn scikit-learn & Hợp đồng kỹ thuật)

Áp dụng công thức Smooth IDF với $N = 3$:

$$\text{idf}(t) = \ln\left(\frac{1 + N}{1 + df(t)}\right) + 1.0 = \ln\left(\frac{4}{1 + df(t)}\right) + 1.0$$

- Với các từ có $df(t) = 1$ (`deadline`, `due`, `exam`, `fees`, `payment`, `posted`, `schedule`):
  $$\text{idf} = \ln\left(\frac{4}{2}\right) + 1 = \ln(2) + 1 \approx 0.6931 + 1 = 1.6931$$

- Với các từ có $df(t) = 2$ (`semester`, `tuition`):
  $$\text{idf} = \ln\left(\frac{4}{3}\right) + 1 \approx 0.2877 + 1 = 1.2877$$

> **Nhận xét quan trọng:** Từ xuất hiện ở nhiều tài liệu hơn (`semester`, `tuition`) có trọng số phân biệt $IDF$ thấp hơn ($1.2877$) so với các từ đặc thù chỉ xuất hiện ở 1 tài liệu ($1.6931$).

---

## 4. Vector trọng số TF-IDF thô và Chuẩn hóa $L_2$

Với tần số xuất hiện $tf(t, d)$ (đếm số lần từ xuất hiện trong văn bản), trọng số thô là $w(t) = tf(t) \times idf(t)$.  
Độ dài vector theo chuẩn Euclid: $\|w\|_2 = \sqrt{\sum w(t)^2}$.  
Vector đơn vị sau khi chuẩn hóa: $\hat{w}(t) = \frac{w(t)}{\|w\|_2}$.

### Tài liệu $D_1$: `"tuition fees due semester"`
- $w(\text{due}) = 1 \times 1.6931 = 1.6931$
- $w(\text{fees}) = 1 \times 1.6931 = 1.6931$
- $w(\text{semester}) = 1 \times 1.2877 = 1.2877$
- $w(\text{tuition}) = 1 \times 1.2877 = 1.2877$
- Độ dài: $\|D_1\|_2 = \sqrt{1.6931^2 + 1.6931^2 + 1.2877^2 + 1.2877^2} = \sqrt{9.0500} \approx 3.0083$
- **Vector $\hat{D}_1$:**
  - $\hat{D}_1(\text{due}) = 1.6931 / 3.0083 \approx \mathbf{0.5628}$
  - $\hat{D}_1(\text{fees}) = 1.6931 / 3.0083 \approx \mathbf{0.5628}$
  - $\hat{D}_1(\text{semester}) = 1.2877 / 3.0083 \approx \mathbf{0.4280}$
  - $\hat{D}_1(\text{tuition}) = 1.2877 / 3.0083 \approx \mathbf{0.4280}$

### Tài liệu $D_2$: `"exam schedule posted semester"`
- $w(\text{exam}) = w(\text{posted}) = w(\text{schedule}) = 1.6931$
- $w(\text{semester}) = 1.2877$
- Độ dài: $\|D_2\|_2 = \sqrt{3 \times 1.6931^2 + 1.2877^2} = \sqrt{10.2587} \approx 3.2029$
- **Vector $\hat{D}_2$:**
  - $\hat{D}_2(\text{exam}) = \hat{D}_2(\text{posted}) = \hat{D}_2(\text{schedule}) = 1.6931 / 3.2029 \approx \mathbf{0.5286}$
  - $\hat{D}_2(\text{semester}) = 1.2877 / 3.2029 \approx \mathbf{0.4020}$

### Tài liệu $D_3$: `"tuition payment deadline"`
- $w(\text{deadline}) = w(\text{payment}) = 1.6931$
- $w(\text{tuition}) = 1.2877$
- Độ dài: $\|D_3\|_2 = \sqrt{2 \times 1.6931^2 + 1.2877^2} = \sqrt{7.3917} \approx 2.7188$
- **Vector $\hat{D}_3$:**
  - $\hat{D}_3(\text{deadline}) = \hat{D}_3(\text{payment}) = 1.6931 / 2.7188 \approx \mathbf{0.6228}$
  - $\hat{D}_3(\text{tuition}) = 1.2877 / 2.7188 \approx \mathbf{0.4736}$

### Câu hỏi truy vấn $Q$: `"tuition semester deadline"`
- $w(\text{deadline}) = 1.6931$
- $w(\text{semester}) = 1.2877$
- $w(\text{tuition}) = 1.2877$
- Độ dài: $\|Q\|_2 = \sqrt{1.6931^2 + 2 \times 1.2877^2} = \sqrt{6.1834} \approx 2.4866$
- **Vector $\hat{Q}$:**
  - $\hat{Q}(\text{deadline}) = 1.6931 / 2.4866 \approx \mathbf{0.6809}$
  - $\hat{Q}(\text{semester}) = 1.2877 / 2.4866 \approx \mathbf{0.5179}$
  - $\hat{Q}(\text{tuition}) = 1.2877 / 2.4866 \approx \mathbf{0.5179}$

---

## 5. Tính Cosine Similarity (Tích vô hướng)

Vì các vector đã được chuẩn hóa $L_2$ về độ dài bằng $1$, Cosine Similarity chính là tích vô hướng:

$$\cos(Q, D) = \hat{Q} \cdot \hat{D} = \sum_{t \in \mathcal{V}} \hat{Q}(t) \times \hat{D}(t)$$

### Tính $\cos(Q, D_1)$:
- Từ chung: `semester`, `tuition`
- $\cos(Q, D_1) = \hat{Q}(\text{semester})\hat{D}_1(\text{semester}) + \hat{Q}(\text{tuition})\hat{D}_1(\text{tuition})$
- $\cos(Q, D_1) = (0.5179 \times 0.4280) + (0.5179 \times 0.4280) = 0.2217 + 0.2217 = \mathbf{0.4433}$

### Tính $\cos(Q, D_2)$:
- Từ chung: `semester`
- $\cos(Q, D_2) = \hat{Q}(\text{semester})\hat{D}_2(\text{semester})$
- $\cos(Q, D_2) = 0.5179 \times 0.4020 = \mathbf{0.2082}$

### Tính $\cos(Q, D_3)$:
- Từ chung: `deadline`, `tuition`
- $\cos(Q, D_3) = \hat{Q}(\text{deadline})\hat{D}_3(\text{deadline}) + \hat{Q}(\text{tuition})\hat{D}_3(\text{tuition})$
- $\cos(Q, D_3) = (0.6809 \times 0.6228) + (0.5179 \times 0.4736) = 0.4241 + 0.2453 = \mathbf{0.6693}$

---

## 6. Kết quả Xếp hạng (Ranking) và Phân tích bản chất

| Thứ hạng | Tài liệu | Điểm tương đồng $\cos(Q, D)$ | Các từ khớp |
|---|---|---|---|
| **Top 1** | **$D_3$** | **0.6693** | `deadline`, `tuition` |
| **Top 2** | **$D_1$** | **0.4433** | `semester`, `tuition` |
| **Top 3** | **$D_2$** | **0.2082** | `semester` |

### 💡 Bài học rút ra (Dùng để thuyết trình Slide 8 & Vấn đáp):
1. **Vì sao $D_3$ xếp trên $D_1$ dù cả hai đều khớp đúng 2 từ?**  
   - $D_1$ khớp `tuition` và `semester` (đều có $df = 2$, từ phổ biến hơn trong kho, $IDF = 1.2877$).
   - $D_3$ khớp `tuition` ($IDF = 1.2877$) và `deadline` ($df = 1$, từ hiếm và đặc thù hơn, $IDF = 1.6931$).  
   $\to$ **Cơ chế IDF giúp hệ thống đánh giá cao tài liệu khớp các từ khóa hiếm và mang nhiều thông tin định danh hơn.**
2. **Vì sao dùng Cosine Similarity thay cho Khoảng cách Euclid?**  
   - Khoảng cách Euclid bị phụ thuộc nặng vào độ dài văn bản (văn bản dài chứa nhiều từ sẽ bị đẩy ra xa trong không gian vector).
   - Cosine Similarity chia độ dài cho chuẩn $L_2$, chỉ đo góc giữa hai vector $\to$ **so sánh độ tương đồng ngữ nghĩa bất kể câu hỏi ngắn hay văn bản dài**.
