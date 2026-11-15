# Ví dụ tính tay TF-IDF, Cosine Similarity và Naive Bayes

> Tài liệu thực hiện: **Lương Việt Anh** (Việc **A01**) & **Nguyễn Ánh Dương** (Việc **D04**).  
> Phục vụ: **Slide 8, 11**, **Phụ lục P1, P2**, và trả lời vấn đáp câu hỏi 1, 2, 3, 4 trong `notes/qa_bank.md`.

---

## PHẦN I: TÍNH TAY TF-IDF VÀ COSINE SIMILARITY (VIỆT ANH — A01)

### 1. Dữ liệu mẫu (3 tài liệu ngắn và 1 truy vấn)

Xét kho tài liệu gồm $N = 3$ tài liệu ngắn sau khi tiền xử lý (lowercase, bỏ dấu câu và stopwords):

- **Tài liệu 1 ($D_1$):** `"tuition fees due semester"` (4 từ)
- **Tài liệu 2 ($D_2$):** `"exam schedule posted semester"` (4 từ)
- **Tài liệu 3 ($D_3$):** `"tuition payment deadline"` (3 từ)

**Câu hỏi truy vấn ($Q$):** `"tuition semester deadline"` (3 từ)

---

### 2. Bộ từ vựng và Document Frequency ($df$)

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

### 3. Công thức tính IDF (Chuẩn scikit-learn & Hợp đồng kỹ thuật)

Áp dụng công thức Smooth IDF với $N = 3$:

$$\text{idf}(t) = \ln\left(\frac{1 + N}{1 + df(t)}\right) + 1.0 = \ln\left(\frac{4}{1 + df(t)}\right) + 1.0$$

- Với các từ có $df(t) = 1$ (`deadline`, `due`, `exam`, `fees`, `payment`, `posted`, `schedule`):
  $$\text{idf} = \ln\left(\frac{4}{2}\right) + 1 = \ln(2) + 1 \approx 0.6931 + 1 = 1.6931$$

- Với các từ có $df(t) = 2$ (`semester`, `tuition`):
  $$\text{idf} = \ln\left(\frac{4}{3}\right) + 1 \approx 0.2877 + 1 = 1.2877$$

> **Nhận xét quan trọng:** Từ xuất hiện ở nhiều tài liệu hơn (`semester`, `tuition`) có trọng số phân biệt $IDF$ thấp hơn ($1.2877$) so với các từ đặc thù chỉ xuất hiện ở 1 tài liệu ($1.6931$).

---

### 4. Vector trọng số TF-IDF thô và Chuẩn hóa $L_2$

Với tần số xuất hiện $tf(t, d)$ (đếm số lần từ xuất hiện trong văn bản), trọng số thô là $w(t) = tf(t) \times idf(t)$.  
Độ dài vector theo chuẩn Euclid: $\|w\|_2 = \sqrt{\sum w(t)^2}$.  
Vector đơn vị sau khi chuẩn hóa: $\hat{w}(t) = \frac{w(t)}{\|w\|_2}$.

#### Tài liệu $D_1$: `"tuition fees due semester"`
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

#### Tài liệu $D_2$: `"exam schedule posted semester"`
- $w(\text{exam}) = w(\text{posted}) = w(\text{schedule}) = 1.6931$
- $w(\text{semester}) = 1.2877$
- Độ dài: $\|D_2\|_2 = \sqrt{3 \times 1.6931^2 + 1.2877^2} = \sqrt{10.2587} \approx 3.2029$
- **Vector $\hat{D}_2$:**
  - $\hat{D}_2(\text{exam}) = \hat{D}_2(\text{posted}) = \hat{D}_2(\text{schedule}) = 1.6931 / 3.2029 \approx \mathbf{0.5286}$
  - $\hat{D}_2(\text{semester}) = 1.2877 / 3.2029 \approx \mathbf{0.4020}$

#### Tài liệu $D_3$: `"tuition payment deadline"`
- $w(\text{deadline}) = w(\text{payment}) = 1.6931$
- $w(\text{tuition}) = 1.2877$
- Độ dài: $\|D_3\|_2 = \sqrt{2 \times 1.6931^2 + 1.2877^2} = \sqrt{7.3917} \approx 2.7188$
- **Vector $\hat{D}_3$:**
  - $\hat{D}_3(\text{deadline}) = \hat{D}_3(\text{payment}) = 1.6931 / 2.7188 \approx \mathbf{0.6228}$
  - $\hat{D}_3(\text{tuition}) = 1.2877 / 2.7188 \approx \mathbf{0.4736}$

#### Câu hỏi truy vấn $Q$: `"tuition semester deadline"`
- $w(\text{deadline}) = 1.6931$
- $w(\text{semester}) = 1.2877$
- $w(\text{tuition}) = 1.2877$
- Độ dài: $\|Q\|_2 = \sqrt{1.6931^2 + 2 \times 1.2877^2} = \sqrt{6.1834} \approx 2.4866$
- **Vector $\hat{Q}$:**
  - $\hat{Q}(\text{deadline}) = 1.6931 / 2.4866 \approx \mathbf{0.6809}$
  - $\hat{Q}(\text{semester}) = 1.2877 / 2.4866 \approx \mathbf{0.5179}$
  - $\hat{Q}(\text{tuition}) = 1.2877 / 2.4866 \approx \mathbf{0.5179}$

---

### 5. Tính Cosine Similarity (Tích vô hướng)

Vì các vector đã được chuẩn hóa $L_2$ về độ dài bằng $1$, Cosine Similarity chính là tích vô hướng:

$$\cos(Q, D) = \hat{Q} \cdot \hat{D} = \sum_{t \in \mathcal{V}} \hat{Q}(t) \times \hat{D}(t)$$

- **$\cos(Q, D_1)$:**  
  Từ chung: `semester`, `tuition`  
  $\cos(Q, D_1) = (0.5179 \times 0.4280) + (0.5179 \times 0.4280) = 0.2217 + 0.2217 = \mathbf{0.4433}$

- **$\cos(Q, D_2)$:**  
  Từ chung: `semester`  
  $\cos(Q, D_2) = 0.5179 \times 0.4020 = \mathbf{0.2082}$

- **$\cos(Q, D_3)$:**  
  Từ chung: `deadline`, `tuition`  
  $\cos(Q, D_3) = (0.6809 \times 0.6228) + (0.5179 \times 0.4736) = 0.4241 + 0.2453 = \mathbf{0.6693}$

**Bảng xếp hạng cuối cùng:**
1. Top 1: **$D_3$** (Cosine = **0.6693**)
2. Top 2: **$D_1$** (Cosine = **0.4433**)
3. Top 3: **$D_2$** (Cosine = **0.2082**)

---

## PHẦN II: TÍNH TAY NAIVE BAYES VÀ LAPLACE SMOOTHING (DƯƠNG — D04 / PHỤ LỤC P2)

### 6. Bài toán Phân loại Ý định mẫu

Xét bài toán phân loại câu hỏi vào $K = 2$ chủ đề: $c_1 = \text{tuition}$ và $c_2 = \text{exam}$.  
Tập dữ liệu huấn luyện gồm 4 văn bản ngắn:

- **Lớp $c_1$ (`tuition`) có 2 câu:**
  - $T_1$: `"pay tuition fee"` (3 từ)
  - $T_2$: `"tuition deadline payment"` (3 từ)
  $\implies$ Tổng số từ của lớp $c_1$: $N_{c_1} = 6$ từ.
- **Lớp $c_2$ (`exam`) có 2 câu:**
  - $T_3$: `"exam schedule room"` (3 từ)
  - $T_4$: `"final exam schedule"` (3 từ)
  $\implies$ Tổng số từ của lớp $c_2$: $N_{c_2} = 6$ từ.

**Kích thước tập huấn luyện:** $N = 4$ câu.  
**Bộ từ vựng chung:**
$$\mathcal{V} = \{\text{deadline}, \text{exam}, \text{fee}, \text{final}, \text{pay}, \text{payment}, \text{room}, \text{schedule}, \text{tuition}\} \implies |\mathcal{V}| = 9$$

**Câu truy vấn kiểm thử:** $Q =$ `"exam fee deadline"` (3 từ)

---

### 7. Tính Xác suất Tiên nghiệm (Prior Probability)

Vì mỗi lớp có 2 trên tổng số 4 câu:
$$P(c_1) = \frac{2}{4} = 0.5, \quad P(c_2) = \frac{2}{4} = 0.5$$

---

### 8. Tính Xác suất Có điều kiện với Làm mượt Laplace (Additive Smoothing, $\alpha = 1$)

Công thức Multinomial Naive Bayes với Laplace smoothing:
$$P(w \mid c) = \frac{\text{count}(w, c) + \alpha}{\sum_{w' \in \mathcal{V}} \text{count}(w', c) + \alpha \cdot |\mathcal{V}|} = \frac{\text{count}(w, c) + 1}{N_c + 9}$$

Với $N_{c_1} = 6$ và $N_{c_2} = 6$, mẫu số cho cả hai lớp là: $6 + 9 = 15$.

#### Tần số xuất hiện của các từ trong $Q$ theo từng lớp:
- Từ `"exam"`:
  - Trong $c_1$: xuất hiện 0 lần $\implies P(\text{exam} \mid c_1) = \frac{0 + 1}{15} = \frac{1}{15}$
  - Trong $c_2$: xuất hiện 2 lần $\implies P(\text{exam} \mid c_2) = \frac{2 + 1}{15} = \frac{3}{15}$

- Từ `"fee"`:
  - Trong $c_1$: xuất hiện 1 lần $\implies P(\text{fee} \mid c_1) = \frac{1 + 1}{15} = \frac{2}{15}$
  - Trong $c_2$: xuất hiện 0 lần $\implies P(\text{fee} \mid c_2) = \frac{0 + 1}{15} = \frac{1}{15}$

- Từ `"deadline"`:
  - Trong $c_1$: xuất hiện 1 lần $\implies P(\text{deadline} \mid c_1) = \frac{1 + 1}{15} = \frac{2}{15}$
  - Trong $c_2$: xuất hiện 0 lần $\implies P(\text{deadline} \mid c_2) = \frac{0 + 1}{15} = \frac{1}{15}$

---

### 9. Tính Xác suất Hậu nghiệm (Posterior Probability)

Theo định lý Bayes và giả định độc lập có điều kiện của Naive Bayes:
$$P(c \mid Q) \propto P(c) \times \prod_{w \in Q} P(w \mid c)$$

#### Điểm chưa chuẩn hóa cho lớp $c_1$ (`tuition`):
$$\text{Score}(c_1) = P(c_1) \times P(\text{exam} \mid c_1) \times P(\text{fee} \mid c_1) \times P(\text{deadline} \mid c_1)$$
$$\text{Score}(c_1) = 0.5 \times \frac{1}{15} \times \frac{2}{15} \times \frac{2}{15} = 0.5 \times \frac{4}{3375} = \frac{2}{3375} \approx \mathbf{0.0005926}$$

#### Điểm chưa chuẩn hóa cho lớp $c_2$ (`exam`):
$$\text{Score}(c_2) = P(c_2) \times P(\text{exam} \mid c_2) \times P(\text{fee} \mid c_2) \times P(\text{deadline} \mid c_2)$$
$$\text{Score}(c_2) = 0.5 \times \frac{3}{15} \times \frac{1}{15} \times \frac{1}{15} = 0.5 \times \frac{3}{3375} = \frac{1.5}{3375} \approx \mathbf{0.0004444}$$

#### Chuẩn hóa Softmax/Tổng xác suất bằng 1:
$$\text{Tổng} = \text{Score}(c_1) + \text{Score}(c_2) = \frac{2 + 1.5}{3375} = \frac{3.5}{3375}$$
$$P(c_1 = \text{tuition} \mid Q) = \frac{2}{3.5} = \frac{4}{7} \approx \mathbf{57.14\%}$$
$$P(c_2 = \text{exam} \mid Q) = \frac{1.5}{3.5} = \frac{3}{7} \approx \mathbf{42.86\%}$$

---

### 10. Quyết định Dự đoán và Ý nghĩa của Laplace Smoothing

1. **Kết quả:** Mô hình dự đoán câu hỏi $Q$ thuộc nhãn **`tuition`** với độ tin cậy **$57.1\%$**.
2. **Vai trò cốt tử của Laplace Smoothing ($\alpha = 1$):**
   - Nếu không có Laplace smoothing ($\alpha = 0$), từ `"exam"` không xuất hiện trong $c_1$ sẽ làm $P(\text{exam} \mid c_1) = 0 \implies \text{Score}(c_1) = 0$.
   - Tương tự, từ `"fee"` và `"deadline"` không có trong $c_2$ làm $\text{Score}(c_2) = 0$.
   - Cả hai lớp đều nhận điểm 0, khiến mô hình hoàn toàn bất lực!
   - Laplace smoothing gán một phần xác suất nhỏ (pseudo-counts) cho mọi từ chưa thấy, bảo vệ tích xác suất không bị triệt tiêu và cho phép các từ còn lại đưa ra quyết định dựa trên bằng chứng thống kê.
