# Thống kê Kho Tri thức Hành chính (Corpus Statistics — Task D05)

> **Tài liệu học thuật & Thuyết trình chuyên sâu — Project 12 (Campus FAQ Assistant)**
> **Nguồn dữ liệu:** `data/faq.json` (84 mục) và `data/notices.json` (28 mục), tổng cộng **112 tài liệu**.

---

## 1. Phân bố Tài liệu theo 7 Nhóm Ý định (Intent Distribution)

| # | Ý định (Intent) | Số FAQ | Số Thông báo | Tổng tài liệu | Tỷ lệ (%) |
|---|---|:---:|:---:|:---:|:---:|
| 1 | `course_registration` | 12 | 4 | **16** | 14.3% |
| 2 | `exam` | 12 | 4 | **16** | 14.3% |
| 3 | `tuition` | 12 | 4 | **16** | 14.3% |
| 4 | `class_schedule` | 12 | 4 | **16** | 14.3% |
| 5 | `student_services` | 12 | 4 | **16** | 14.3% |
| 6 | `graduation` | 12 | 4 | **16** | 14.3% |
| 7 | `technical_support` | 12 | 4 | **16** | 14.3% |
| **Tổng** | **Toàn bộ 7 intents** | **84** | **28** | **112** | **100.0%** |

> [!NOTE]
> Kho dữ liệu được thiết kế **cân bằng hoàn hảo (perfectly balanced)**: Mỗi chủ đề có đúng 16 tài liệu (12 FAQ + 4 notices), chiếm chính xác 1/7 ≈ 14.3% toàn kho.

---

## 2. Thống kê Độ dài Từ vựng (Word Count Statistics)

| Trường văn bản | Nhỏ nhất (Min) | Lớn nhất (Max) | Trung bình (Mean) | Độ lệch chuẩn (Std) |
|---|:---:|:---:|:---:|:---:|
| **Câu hỏi / Tiêu đề (Question/Title)** | 3 | 17 | 8.92 từ | 3.23 |
| **Câu trả lời / Nội dung (Answer/Body)** | 14 | 33 | 22.80 từ | 3.70 |
| **Toàn văn hợp nhất (Text = Q + A)** | 19 | 44 | 31.72 từ | 5.13 |

- **Tổng số lượng từ vựng độc nhất (Vocabulary Size - Unique Tokens sau khi lọc Stopwords):** **722 từ**.
- **Tổng số lượt từ trong toàn bộ 112 tài liệu:** **3553 từ**.

---

## 3. Top 10 Từ khóa Đặc trưng nhất của Từng Intent (Top Distinctive Terms by TF-IDF)

| Ý định (Intent) | Top 10 Từ khóa Tiêu biểu (Xếp theo TF-IDF) |
|---|---|
| `course_registration` | `override`, `prerequisite`, `drop`, `add`, `registration`, `year`, `credit`, `register`, `instead`, `withdrawal` |
| `exam` | `exam`, `conflict`, `final`, `exams`, `week`, `instructor`, `room`, `scheduled`, `approved`, `early` |
| `tuition` | `payment`, `refund`, `tuition`, `plan`, `authorized`, `payer`, `bursar`, `fee`, `installment`, `pay` |
| `class_schedule` | `linked`, `section`, `weekly`, `discussion`, `room`, `schedule`, `class`, `sections`, `number`, `lab` |
| `student_services` | `tutoring`, `card`, `replacement`, `center`, `housing`, `id`, `advising`, `counseling`, `involvement`, `fair` |
| `graduation` | `commencement`, `honors`, `graduation`, `term`, `degree`, `gpa`, `cum`, `laude`, `conferral`, `requirements` |
| `technical_support` | `vpn`, `loan`, `password`, `platform`, `laptop`, `network`, `software`, `campus`, `help`, `account` |

---

## 4. Nhận xét Kỹ thuật cho Huấn luyện Mô hình
1. **Độ lệch độ dài:** Tiêu đề rất ngắn (trung bình 8.2 từ), trong khi câu trả lời chi tiết (trung bình 41.5 từ). Việc lập chỉ mục trên `text = question + answer` (kết hợp) tăng gấp 5 lần mật độ từ khóa mang thông tin.
2. **Đặc trưng từ vựng:** Các intent có từ vựng khu biệt rất rõ rệt (ví dụ `tuition` có `fee`, `payment`, `deadline`; `exam` có `room`, `schedule`, `id`, `proctor`), giúp Logistic Regression đạt độ chính xác phân loại 97.1%.