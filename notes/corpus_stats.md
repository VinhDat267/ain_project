# Thống kê Kho Tri thức Hành chính (Corpus Statistics — Task D05)

> **Tài liệu học thuật & Thuyết trình chuyên sâu — Project 12 (Campus FAQ Assistant)**  
> **Nguồn dữ liệu:** `data/faq.json` (84 mục) và `data/notices.json` (28 mục), tổng cộng **112 tài liệu**.  
> **Công cụ kiểm chứng:** Xuất tự động từ `scripts/build_report_tables.py` vào `experiments/results/report_verification_manifest.json`.

---

## 1. Phân bố Tài liệu theo 7 Nhóm Ý định (Intent Distribution)

| # | Ý định (Intent) | Số FAQ | Số Thông báo | Tổng tài liệu | Tỷ lệ (%) |
|---|---|:---:|:---:|:---:|:---:|
| 1 | `course_registration` | 12 | 4 | **16** | 14.29% |
| 2 | `exam` | 12 | 4 | **16** | 14.29% |
| 3 | `tuition` | 12 | 4 | **16** | 14.29% |
| 4 | `class_schedule` | 12 | 4 | **16** | 14.29% |
| 5 | `student_services` | 12 | 4 | **16** | 14.29% |
| 6 | `graduation` | 12 | 4 | **16** | 14.29% |
| 7 | `technical_support` | 12 | 4 | **16** | 14.29% |
| **Tổng** | **Toàn bộ 7 intents** | **84** | **28** | **112** | **100.0%** |

> [!NOTE]
> Kho dữ liệu được thiết kế **cân bằng hoàn hảo (perfectly balanced)**: Mỗi chủ đề có đúng 16 tài liệu (12 FAQ + 4 notices), chiếm chính xác 1/7 ≈ 14.29% toàn kho.

---

## 2. Thống kê Độ dài Văn bản Thực tế (Ground-Truth Corpus Statistics)

Dữ liệu được đo lường chính xác trên 112 tài liệu thực tế:

| Phân loại | Trường văn bản | Số mục | Min từ | Max từ | Mean từ ± Std | Min ký tự | Max ký tự | Mean ký tự ± Std |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **FAQ** | Câu hỏi (`question`) | 84 | 5 | 17 | 10.26 ± 2.49 | 27 | 86 | 53.51 ± 10.78 |
| **FAQ** | Câu trả lời (`answer`) | 84 | 15 | 33 | 23.04 ± 3.62 | 103 | 216 | 145.70 ± 20.16 |
| **FAQ** | Toàn văn (`question + answer`) | 84 | 25 | 44 | 33.30 ± 4.58 | 150 | 267 | 200.21 ± 22.17 |
| **Notices** | Tiêu đề (`title`) | 28 | 3 | 8 | 4.89 ± 1.08 | 26 | 47 | 35.68 ± 5.18 |
| **Notices** | Nội dung (`body`) | 28 | 14 | 32 | 22.11 ± 3.76 | 109 | 222 | 139.25 ± 24.59 |
| **Notices** | Toàn văn (`title + body`) | 28 | 19 | 36 | 27.00 ± 3.41 | 143 | 254 | 175.93 ± 24.05 |
| **Toàn kho** | **Toàn văn hợp nhất (112 docs)** | **112** | **19** | **44** | **31.72 ± 5.11** | **143** | **267** | **194.14 ± 24.98** |

---

## 3. Thống kê Không gian Đặc trưng & Kích thước Từ vựng (Feature Space Statistics)

Đo lường trực tiếp qua `sklearn.feature_extraction.text.TfidfVectorizer` fit trên 112 tài liệu toàn văn:

- **Từ đơn (Word unigrams `1,1`):** `845` features.
- **Từ ghép (Word unigrams + bigrams `1,2`):** `3,210` features.
- **Ký tự ranh giới từ (Character n-grams `char_wb 3..5`):** **`8,398` features**.

---

## 4. Top 10 Từ khóa Đặc trưng nhất của Từng Intent (Top Distinctive Terms by TF-IDF)

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

## 5. Nhận xét Kỹ thuật cho Huấn luyện Mô hình
1. **Độ lệch độ dài:** Tiêu đề rất ngắn (trung bình 4.89 từ cho notice, 10.26 từ cho FAQ), trong khi câu trả lời chi tiết (trung bình 23 từ). Việc lập chỉ mục trên `text = question/title + answer/body` (kết hợp) tăng gấp 3-5 lần mật độ từ khóa mang thông tin.
2. **Đặc trưng từ vựng:** Các intent có từ vựng khu biệt rất rõ rệt (ví dụ `tuition` có `fee`, `payment`, `bursar`; `exam` có `room`, `schedule`, `final`, `proctor`), giúp Logistic Regression đạt độ chính xác phân loại 97.14% (102/105) trên benchmark in-corpus.
