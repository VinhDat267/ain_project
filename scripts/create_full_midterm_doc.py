import os
import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from doc_helpers import set_cell_background, set_cell_margins, add_callout, format_row

def build_document(output_paths):
    doc = docx.Document()
    
    # Page setup: Margins 1 inch
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    def add_p(text="", space_before=2, space_after=6, line_spacing=1.15, bold=False, italic=False, font_size=11, color_rgb=(0x2D, 0x37, 0x48), align=WD_ALIGN_PARAGRAPH.LEFT):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = "Arial"
            run.font.size = Pt(font_size)
            run.font.color.rgb = RGBColor(*color_rgb)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D) # Navy
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x2C, 0x7A, 0x7B) # Teal
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(0x2D, 0x37, 0x48) # Dark slate
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
        
        r_txt = p.add_run(text)
        r_txt.font.name = "Arial"
        r_txt.font.size = Pt(10.5)
        r_txt.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
        return p

    # ================= COVER / HEADER =================
    add_p("HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG / ĐẠI HỌC HÀ NỘI — MÔN TRÍ TUỆ NHÂN TẠO (AIN)", font_size=10, bold=True, color_rgb=(0x71, 0x80, 0x96), align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("PROJECT 12: CAMPUS NOTICE & FAQ ASSISTANT", font_size=22, bold=True, color_rgb=(0x1A, 0x36, 0x5D), space_before=8, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("CẨM NANG TOÀN TẬP: LÝ THUYẾT, THUẬT TOÁN, GIAI THOẠI & KỊCH BẢN THUYẾT TRÌNH BẢO VỆ MIDTERM", font_size=13, bold=True, color_rgb=(0x2C, 0x7A, 0x7B), space_before=2, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_callout(doc, 
        "Tài liệu này được biên soạn đặc biệt theo phương pháp 'Từ số 0 đến Chuyên sâu'. Dù bạn chưa từng học qua Xử lý Ngôn ngữ Tự nhiên (NLP) hay Trí tuệ Nhân tạo, tài liệu này sẽ dẫn dắt bạn hiểu tường tận từng phép toán, từng dòng code và mọi kịch bản phản biện vấn đáp trước hội đồng.",
        title="DÀNH CHO NGƯỜI MỚI TIẾP XÚC & ÔN TẬP THUYẾT TRÌNH"
    )

    # ================= CHƯƠNG 1 =================
    add_h1("CHƯƠNG 1: BÀI TOÁN THỰC TẾ LÀ GÌ? (GIẢI THÍCH BÌNH DÂN)")
    add_p("Hãy tưởng tượng bạn là một sinh viên năm nhất vừa bước chân vào trường đại học. Bạn có hàng trăm thắc mắc: khi nào đóng học phí, làm sao đăng ký môn học, phòng thi ở đâu, mạng Wi-Fi trường bị lỗi thì liên hệ ai? Thay vì phải xếp hàng chờ ở phòng Đào tạo hoặc gửi email chờ vài ngày mới có phản hồi, nhà trường muốn xây dựng một Trợ lý ảo thông minh (Chatbot/Search Assistant) để trả lời ngay lập tức.")
    
    add_h2("1. Ba kịch bản đời thực mà trợ lý phải xử lý")
    add_bullet("Kịch bản 1 — Câu hỏi chuẩn xác (Normal): ", "Sinh viên hỏi rõ ràng, đúng câu chữ trong quy chế: 'When is tuition due for the semester?'. Hệ thống phải tìm đúng tài liệu hướng dẫn về hạn đóng học phí và gắn nhãn chủ đề 'tuition'.")
    add_bullet("Kịch bản 2 — Câu hỏi gõ sai chính tả (Typo): ", "Sinh viên gõ vội trên điện thoại: 'How do I reset my Sutdent Portal password?'. Từ 'Student' bị gõ nhầm thành 'Sutdent'. Máy tính không được đầu hàng mà vẫn phải nhận diện được để trả về đúng tài liệu hướng dẫn đặt lại mật khẩu.")
    add_bullet("Kịch bản 3 — Câu hỏi ngoài phạm vi (Out-of-Corpus - OOC): ", "Sinh viên hỏi: 'Quán ăn chay nào ngon nhất gần trường?' hoặc 'Có thể thuê thuyền kayak ở trung tâm thể thao không?'. Trường học không có dịch vụ này. Hệ thống TUYỆT ĐỐI KHÔNG ĐƯỢC BỊA ĐẶT CÂU TRẢ LỜI, mà phải biết nói lời từ chối lịch sự: 'Thông tin không tìm thấy — Vui lòng liên hệ văn phòng hành chính'.")

    add_h2("2. Một bài toán lớn được bóc tách thành 3 bài toán con")
    add_p("Nhìn bề ngoài thì giống một phần mềm duy nhất, nhưng bên trong là sự phối hợp nhịp nhàng của 3 bài toán AI cổ điển:")
    add_bullet("Bài toán 1 — Truy hồi tài liệu (Information Retrieval): ", "Trong kho 112 văn bản của trường, văn bản nào giống và liên quan nhất tới câu hỏi của sinh viên? (Không cần học máy, dùng hình học không gian vector).")
    add_bullet("Bài toán 2 — Phân loại ý định (Intent Classification): ", "Câu hỏi này thuộc về chủ đề nào trong 7 chủ đề: course_registration, exam, tuition, class_schedule, student_services, graduation, technical_support? (Dùng học máy có giám sát).")
    add_bullet("Bài toán 3 — Ra quyết định từ chối (Decision Making under Uncertainty): ", "Câu hỏi này có đủ độ tin cậy để trả lời không, hay phải từ chối? Cân bằng giữa hai cái sai: Trả lời bừa (ảo giác) vs Từ chối oan (câu hỏi đúng mà không chịu trả lời).")

    add_h2("3. Barem chấm điểm Midterm (Thang điểm 40)")
    # Table for Grading
    table1 = doc.add_table(rows=4, cols=3)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.autofit = False
    format_row(table1.rows[0], is_header=True)
    table1.rows[0].cells[0].paragraphs[0].text = "Hạng mục chấm điểm"
    table1.rows[0].cells[1].paragraphs[0].text = "Điểm số"
    table1.rows[0].cells[2].paragraphs[0].text = "Yêu cầu cần chứng minh với hội đồng"
    
    grading_data = [
        ("Mô hình không gian vector & Retrieval", "15 điểm", "Cài đặt đúng thuật toán TF-IDF và Cosine similarity tự viết (không dùng thư viện ngoài trong hàm chạy), hiểu cặn kẽ công thức toán học, giải thích được ví dụ tính tay."),
        ("Phân tích độ bền & Hiệu chỉnh ngưỡng", "10 điểm", "So sánh khách quan kết quả giữa các loại câu hỏi (Normal, Paraphrase, Typo), quét ngưỡng từ chối khoa học bằng Cross-Validation, không đoán mò."),
        ("Vấn đáp trực tiếp & Demo sản phẩm", "15 điểm", "Trả lời trôi chảy các câu hỏi lý thuyết, tự tin chạy demo trực tiếp trên máy tính tắt mạng (offline), chủ động chỉ ra điểm mạnh và giới hạn của hệ thống.")
    ]
    for idx, (c1, c2, c3) in enumerate(grading_data, start=1):
        format_row(table1.rows[idx], is_header=False)
        table1.rows[idx].cells[0].paragraphs[0].text = c1
        table1.rows[idx].cells[1].paragraphs[0].text = c2
        table1.rows[idx].cells[2].paragraphs[0].text = c3

    # ================= CHƯƠNG 2 =================
    add_h1("CHƯƠNG 2: TỪ CHỮ THÀNH SỐ — BẢN CHẤT XỬ LÝ NGÔN NGỮ TỰ NHIÊN")
    add_p("Con người hiểu văn bản bằng trí tưởng tượng và ngữ cảnh xã hội. Nhưng máy tính (và bộ xử lý CPU) bản chất chỉ là những chiếc máy tính cộng, trừ, nhân, chia các con số nhị phân. Để máy tính 'đọc' được tài liệu trường học, ta phải trải qua quy trình biến đổi từng bước:")

    add_h2("1. Bước tiền xử lý: Rửa sạch dữ liệu thô")
    add_bullet("Chuyển chữ thường (Lowercasing): ", "Chữ 'Tuition' đầu câu và 'tuition' giữa câu phải được xem là một từ duy nhất.")
    add_bullet("Tách từ (Tokenization): ", "Cắt câu văn thành các mẩu từ vựng độc lập bằng cách nhận diện các ký tự chữ và số [a-z0-9]+, vứt bỏ các dấu chấm câu (., ! ?).")
    add_bullet("Lọc từ dừng (Stopwords Removal) & Nghịch lý thú vị: ", "Thông thường người ta hay bỏ các từ quá phổ biến như 'the', 'is', 'at'. NHƯNG TRONG BÀI TOÁN NÀY, việc bỏ stopwords lại làm điểm MRR tụt từ 0.927 xuống 0.896! Lý do: Câu hỏi sinh viên rất ngắn, các từ như 'how', 'when', 'can' mang ý định cốt lõi của câu hỏi (Làm thế nào đóng tiền vs Khi nào đóng tiền). Giữ lại các từ này giúp máy phân biệt ý định tốt hơn.")

    add_h2("2. Mô hình Túi từ (Bag-of-Words) — Cách làm ngây thơ ban đầu")
    add_p("Hãy tưởng tượng bạn gom tất cả các từ xuất hiện trong 112 tài liệu của trường vào một 'từ điển' gồm hàng ngàn từ. Mỗi câu văn sẽ được biểu diễn bằng một dãy số: từ nào xuất hiện thì ghi số lần đếm, từ nào không có thì ghi số 0. Gọi là 'túi từ' vì ta vứt thứ tự ngữ pháp đi, chỉ đếm số lượng.")
    add_p("Điểm yếu chết người: BoW coi từ nối 'for' hay từ chung chung 'campus' nặng ngang hàng với từ định danh quan trọng như 'tuition' hay 'reschedule'. Nếu chỉ đếm số từ, câu nào có chữ 'campus' cũng bị chấm điểm cao ảo.")

    add_h2("3. TF-IDF — Bí quyết chấm điểm độ thông minh của từ")
    add_p("Để sửa sai cho Túi từ, ta dùng kỹ thuật TF-IDF. Nó dựa trên một triết lý vô cùng trực quan:")
    add_p("• TF (Term Frequency - Tần số từ trong câu): Từ đó xuất hiện bao nhiêu lần trong câu văn này? Xuất hiện càng nhiều lần thì câu đó càng nói nhiều về chủ đề đó.\n• IDF (Inverse Document Frequency - Độ hiếm của từ trên toàn trường): Từ đó có hiếm không? Từ nào xuất hiện ở khắp mọi tài liệu (như 'university', 'student') thì giá trị phân biệt bằng 0. Từ nào chỉ xuất hiện ở đúng 1 tài liệu (như 'graduation', 'transcript') thì giá trị phân biệt cực kỳ cao!")
    
    add_p("Công thức chuẩn scikit-learn mà nhóm lập trình:")
    add_p("TF-IDF = TF × IDF = TF × [ ln((1 + N) / (1 + DF)) + 1 ]", bold=True, color_rgb=(0x1A, 0x36, 0x5D))
    add_bullet("Vì sao có logarit (ln)? ", "Theo quy luật Zipf, tần suất từ tăng theo hàm mũ. Logarit giúp kìm độ dốc lại, không để từ hiếm có trọng số gấp hàng triệu lần từ khác.")
    add_bullet("Vì sao cộng 1 ở mẫu và tử số? ", "Để tránh lỗi chia cho 0 nếu gặp một từ hoàn toàn mới chưa từng có trong kho.")
    add_bullet("Vì sao cộng 1 ở ngoài cùng? ", "Để nếu một từ xuất hiện ở toàn bộ 112 tài liệu (DF = N) thì ln(1) = 0, cộng 1 giúp từ đó vẫn giữ trọng số tối thiểu là 1.0 thay vì bị nhân về 0 triệt tiêu.")
    add_bullet("Sublinear TF (1 + ln(TF)): ", "Tùy chọn giúp 'mềm hóa' tần số từ. Một người nhắc từ 'exam' 10 lần không có nghĩa là quan trọng gấp 10 lần người nhắc 1 lần.")

    add_h2("4. Cosine Similarity — Đo góc giữa 2 vector")
    add_p("Sau khi có trọng số TF-IDF, mỗi văn bản và mỗi câu hỏi trở thành một mũi tên (vector) chỉ vào không gian nhiều chiều:")
    add_bullet("Tại sao không dùng khoảng cách Euclid (thước kẻ đo đoạn thẳng)? ", "Vì khoảng cách Euclid bị đánh lừa bởi độ dài văn bản! Một bài viết dài 500 từ về học phí và một câu hỏi ngắn 4 từ về học phí sẽ có độ dài vector rất lệch nhau, khiến khoảng cách giữa chúng rất xa. Máy sẽ tưởng chúng không giống nhau.")
    add_bullet("Cosine Similarity đo góc: ", "Cosine chỉ nhìn vào hướng của mũi tên! Bất kể bài dài hay bài ngắn, nếu cả hai cùng hướng về chủ đề học phí thì góc giữa chúng bằng 0 độ, cos(0) = 1.0 (trùng khớp hoàn hảo). Giá trị luôn nằm từ 0.0 (không liên quan) đến 1.0 (trùng khớp tuyệt đối).")

    add_h2("5. N-gram ký tự (char_wb 3-5) — Tấm khiên chống gõ sai")
    add_p("Nếu người dùng gõ sai 'conncet' thay vì 'connect':")
    add_p("• Ở mức từ: 'conncet' là một từ hoàn toàn lạ, máy tra từ điển không thấy $\to$ Điểm bằng 0!\n• Ở mức n-gram ký tự (cắt cụm 3-5 chữ cái):")
    add_p("  - 'connect' $\to$ [' co', 'con', 'onn', 'nne', 'nec', 'ect', 'ct ']\n  - 'conncet' $\to$ [' co', 'con', 'onn', 'nnc', 'nce', 'cet', 'et ']")
    add_p("Cả hai từ này vẫn giữ nguyên 3 cụm đầu (' co', 'con', 'onn'). Máy tính vẫn tính toán được độ tương đồng cao! Ngoài ra, n-gram ký tự còn bắt được các biến thể từ ngữ pháp như 'register' và 'registration'.")

    # ================= CHƯƠNG 3 =================
    add_h1("CHƯƠNG 3: SO SÁNH THUẬT TOÁN — TẠI SAO CHỌN PHƯƠNG ÁN NÀY?")
    add_p("Nhóm không chọn thuật toán theo cảm tính mà đưa ra 8 phương án Retrieval và 5 phương án Intent so găng trực tiếp trên cùng dữ liệu thực tế:")

    add_h2("1. Bảng thi đấu 8 thuật toán Retrieval (Đo trên 105 câu hỏi hợp lệ)")
    table2 = doc.add_table(rows=9, cols=5)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.autofit = False
    format_row(table2.rows[0], is_header=True)
    table2.rows[0].cells[0].paragraphs[0].text = "Thuật toán Retrieval"
    table2.rows[0].cells[1].paragraphs[0].text = "MRR (Tổng)"
    table2.rows[0].cells[2].paragraphs[0].text = "P@1 Normal"
    table2.rows[0].cells[3].paragraphs[0].text = "P@1 Paraphrase"
    table2.rows[0].cells[4].paragraphs[0].text = "Hit@3"

    retrieval_data = [
        ("TF-IDF ký tự char_wb (3-5) [QUÁN QUÂN]", "0.943", "1.000", "0.714", "0.981"),
        ("Hybrid (0.5 từ + 0.5 ký tự)", "0.936", "1.000", "0.714", "0.952"),
        ("TF-IDF từ (mặc định)", "0.927", "1.000", "0.657", "0.952"),
        ("BM25 (k1=1.5, b=0.75 - Chuẩn công nghiệp)", "0.912", "1.000", "0.600", "0.943"),
        ("TF-IDF từ 1-2 gram", "0.905", "1.000", "0.600", "0.933"),
        ("TF-IDF từ + Bỏ stopword + sublinear", "0.896", "0.971", "0.629", "0.933"),
        ("Bag-of-Words thuần (đếm từ) + Cosine", "0.893", "0.971", "0.571", "0.952"),
        ("LSA (SVD nén 60 chiều ngữ nghĩa)", "0.873", "0.914", "0.600", "0.924")
    ]
    for idx, row in enumerate(retrieval_data, start=1):
        format_row(table2.rows[idx], is_header=False)
        for c_idx, val in enumerate(row):
            table2.rows[idx].cells[c_idx].paragraphs[0].text = val

    add_bullet("Vì sao TF-IDF ký tự (char_wb 3-5) chiến thắng? ", "Đạt MRR cao nhất (0.943). Toàn bộ khoảng cách thắng nằm ở câu diễn đạt lại (Paraphrase) nhờ bắt được các gốc từ chung.")
    add_bullet("Vì sao loại BM25 dù nó là chuẩn Google/Elasticsearch? ", "Điểm số của BM25 không bị chặn trong khoảng [0, 1] mà nhảy từ 7 đến 19 tùy độ dài văn bản. Điều này khiến việc đặt một ngưỡng từ chối cố định là bất khả thi. Hơn nữa, trên tập dữ liệu nhỏ 112 tài liệu, BM25 (0.912) thua xa char TF-IDF (0.943).")
    add_bullet("Vì sao loại LSA (Phân tích ngữ nghĩa ẩn)? ", "LSA cần hàng chục ngàn tài liệu để học ma trận đồng xuất hiện từ. Kho chỉ có 112 văn bản là quá nhỏ, LSA làm nhòe ranh giới khiến câu hỏi nào cũng giống nhau (câu ngoài kho bị chấm điểm cao tới 0.67).")

    add_h2("2. So găng Phân loại Intent: Naive Bayes vs Logistic Regression")
    add_bullet("Multinomial Naive Bayes (94.3%): ", "Là mô hình sinh (Generative). Nó học bằng cách đếm số lần từ xuất hiện theo từng chủ đề rồi dùng định lý xác suất Bayes. Điểm yếu: Giả định các từ độc lập khiến xác suất bị thổi phồng cực đoan sát 1.0 hoặc 0.0. Khi gặp câu hỏi ngoài kho, nó vẫn tự tin trung bình 0.45 (45%) $\to$ Không dùng làm tín hiệu từ chối được.")
    add_bullet("Logistic Regression (97.1% - QUÁN QUÂN): ", "Là mô hình phân biệt (Discriminative). Nó học trực tiếp ranh giới quyết định giữa các intent thông qua hàm Softmax. Độ tin cậy của nó cực kỳ trung thực: câu trong kho tự tin trung bình 0.74 (74%), còn câu ngoài kho tụt dốc về 0.26 (26%) gần sát mức đoán mò 1/7 $\to$ Đây chính là chiếc chìa khóa vàng để phát hiện câu hỏi ngoài kho!")

    # ================= CHƯƠNG 4 =================
    add_h1("CHƯƠNG 4: NGHỆ THUẬT TỪ CHỐI & KIẾN TRÚC CỔNG LỌC KÉP (DUAL-GATE)")
    add_p("Đây là đóng góp kiến trúc xuất sắc nhất của nhóm, giúp giải quyết bài toán hóc búa nhất: Làm sao để từ chối đúng 100% câu hỏi ngoài phạm vi mà không làm rơi rụng các câu hỏi hợp lệ của sinh viên?")

    add_h2("1. Bế tắc của việc chỉ dùng một ngưỡng Cosine đơn độc")
    add_p("Trong thực tế:")
    add_bullet("Câu hợp lệ (trong kho): ", "Có những câu paraphrase diễn đạt quá khác, điểm Cosine cao nhất chỉ đạt 0.17.")
    add_bullet("Câu ngoài kho: ", "Có những câu hỏi bâng quơ như 'Có thể thuê thuyền kayak ở trung tâm giải trí trường (campus recreation center) không?'. Dù trường không cho thuê kayak, nhưng câu này vô tình trùng các từ 'campus', 'center', 'can I' nên điểm Cosine vọt lên tận 0.39!")
    add_p("Kết luận toán học: Điểm số của câu trong kho [0.17 - 1.0] và câu ngoài kho [0.0 - 0.39] chồng lấn lên nhau! Nếu chọn ngưỡng 0.28 (điểm cân bằng), ta chỉ chặn được 11/15 câu ngoài kho. Nếu muốn chặn hết 15 câu ngoài kho thì phải nâng ngưỡng lên 0.40, nhưng khi đó sẽ 'giết oan' mất 25 câu hỏi hợp lệ của sinh viên!")

    add_h2("2. Giải pháp Cứu tinh: Kiến trúc Cổng lọc kép (Dual-Gate)")
    add_p("Thay vì chỉ nhìn vào điểm tương đồng tài liệu, nhóm kết hợp 2 tín hiệu độc lập:")
    add_p("CÂU HỎI CHỈ ĐƯỢC TRẢ LỜI KHI VƯỢT QUA CẢ 2 CỔNG:\n1. Điểm Cosine cao nhất s >= 0.15 (Cổng sàn loại bỏ rác)\n2. Độ tin cậy Intent p >= 0.34 (Cổng thẩm định nghiệp vụ)", bold=True, color_rgb=(0x1A, 0x36, 0x5D))
    
    add_p("Tại sao Cổng Intent lại chặn được câu ngoài kho tinh vi?")
    add_p("Câu hỏi về 'thuyền kayak' tuy có vài từ trùng với thông báo trường, nhưng nội dung của nó hoàn toàn không thuộc về 7 nghiệp vụ: nó không phải đăng ký môn, không phải thi, không phải học phí, không phải đổi lịch... Khi đưa vào Logistic Regression, mô hình thấy từ ngữ phân tán nên xác suất bị xé đều ra 7 lớp (mỗi lớp chỉ được 0.15 - 0.25). Vì 0.25 < 0.34, Cổng Intent lập tức hạ rào chắn và ra lệnh TỪ CHỐI!")
    add_p("Kết quả: Độ chính xác toàn diện End-to-End tăng vọt từ 85% lên 90%, chặn đứng hoàn hảo 15/15 câu hỏi ngoài kho!")

    # ================= CHƯƠNG 5 =================
    add_h1("CHƯƠNG 5: TỪ ĐIỂN THUẬT NGỮ & CÁC CHỈ SỐ ĐÁNH GIÁ")
    add_p("Bảng tra cứu nhanh các thuật ngữ giúp bạn nói chuẩn tiếng Anh chuyên ngành trước mặt giảng viên:")
    
    table3 = doc.add_table(rows=8, cols=3)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table3.autofit = False
    format_row(table3.rows[0], is_header=True)
    table3.rows[0].cells[0].paragraphs[0].text = "Chỉ số / Thuật ngữ"
    table3.rows[0].cells[1].paragraphs[0].text = "Đo lường điều gì?"
    table3.rows[0].cells[2].paragraphs[0].text = "Cách hiểu đơn giản nhất"

    metric_data = [
        ("MRR (Mean Reciprocal Rank)", "Chất lượng xếp hạng tài liệu đúng", "Lấy 1 chia cho vị trí của tài liệu đúng. Nếu tài liệu đúng nằm ở top 1: được 1/1 = 1 điểm. Nằm ở top 2: được 1/2 = 0.5 điểm. Nằm ở top 10: được 1/10 = 0.1 điểm. MRR càng gần 1.0 thì tài liệu đúng càng hay hiện lên đầu tiên."),
        ("P@1 (Precision at 1)", "Độ chính xác kết quả đầu tiên", "Tài liệu đứng đầu tiên có đúng là câu trả lời cần tìm không? Đúng là 1, sai là 0."),
        ("P@3 (Precision at 3)", "Độ chính xác trong top 3", "Số tài liệu đúng trong top 3 chia cho 3. LƯU Ý BẪY VẤN ĐÁP: Vì mỗi câu hỏi chỉ có DUY NHẤT 1 tài liệu đúng trong kho, nên P@3 tối đa chỉ có thể đạt 1/3 = 0.333! Không thể đạt 1.0."),
        ("Hit@3", "Tỉ lệ trúng trong top 3", "Tài liệu đúng có xuất hiện trong top 3 hay không? Có là 1, không là 0. Báo cáo Hit@3 trực quan hơn P@3."),
        ("Intent Accuracy", "Độ chính xác phân loại chủ đề", "Tỉ lệ đoán đúng chủ đề trong 7 intent trên các câu hỏi hợp lệ."),
        ("End-to-End Accuracy", "Độ chính xác toàn hệ thống", "Chỉ số khắt khe nhất: Câu hợp lệ chỉ tính đúng khi KHÔNG bị từ chối và Top-1 phải đúng tài liệu; Câu ngoài kho tính đúng khi BỊ TỪ CHỐI THÀNH CÔNG."),
        ("Cross-Validation 5-fold", "Kỹ thuật kiểm định chéo", "Chia 120 câu thành 5 phần, lấy 4 phần để dò tìm ngưỡng tối ưu và đo thử trên 1 phần còn lại, lặp lại 5 lần để đảm bảo ngưỡng tìm được có tính tổng quát, không bị học vẹt (overfitting).")
    ]
    for idx, row in enumerate(metric_data, start=1):
        format_row(table3.rows[idx], is_header=False)
        for c_idx, val in enumerate(row):
            table3.rows[idx].cells[c_idx].paragraphs[0].text = val

    # ================= CHƯƠNG 6 =================
    add_h1("CHƯƠNG 6: PHÂN TÍCH LỖI — BÀI HỌC VỀ GIỚI HẠN MÔ HÌNH")
    add_p("Trong nghiên cứu khoa học, một nhóm hiểu rõ mình SAI Ở ĐÂU luôn được đánh giá cao hơn nhóm chỉ biết khoe số liệu đẹp. Hãy nắm chắc các dạng lỗi sau:")
    add_bullet("1. Lỗi từ đồng nghĩa (Synonyms): ", "Người hỏi dùng từ 'no open seats' (hết chỗ), nhưng tài liệu quy chế lại viết 'section is full' (lớp học đã đầy). Do các mô hình cổ điển chỉ so khớp mặt chữ mà không hiểu ngữ nghĩa chiều sâu, máy không nhận ra hai cụm từ này cùng nghĩa.")
    add_bullet("2. Lỗi xung đột thời gian (Conflict vs Overlap): ", "Sinh viên hỏi: 'Two of my finals overlap on the same day' (Hai bài thi bị trùng giờ). Tài liệu đúng là faq_exam_02 (exam conflict). Nhưng vì có chữ 'day' và cấu trúc câu giống lịch học, máy lại trả về thông báo đổi lịch học.")
    add_bullet("3. Lỗi nhầm lẫn chủ đề vì từ dùng chung: ", "Sinh viên hỏi về 'registration hold' (bị khóa tài khoản không cho đăng ký môn). Máy bị phân vân giữa 2 intent: course_registration (đăng ký môn) hay tuition (học phí - vì lý do khóa tài khoản là do chưa đóng tiền).")
    add_p("💡 Hướng khắc phục ở giai đoạn Final: Tích hợp từ điển từ đồng nghĩa chuyên ngành (Domain Synonyms Dictionary) và thử nghiệm mô hình nhúng ngữ nghĩa (Sentence Transformers) chạy offline.")

    # ================= CHƯƠNG 7 =================
    add_h1("CHƯƠNG 7: KỊCH BẢN THUYẾT TRÌNH CHI TIẾT TỪNG SLIDE")
    add_p("Dưới đây là lời thoại mẫu (Presentation Script) viết bằng văn phong tự nhiên, đĩnh đạc, giúp bạn làm chủ 10-15 phút thuyết trình:")

    slides = [
        ("Slide 1: Mở đầu & Giới thiệu", "Kính chào thầy và các bạn. Hôm nay nhóm em xin trình bày Project 12: Xây dựng trợ lý thông minh tra cứu thông báo và giải đáp thắc mắc cho sinh viên (Campus Notice and FAQ Assistant). Nhóm em gồm 3 thành viên: bạn Vinh phụ trách đánh giá và thí nghiệm, bạn Dương phụ trách mô hình intent và giao diện, và em là Việt Anh phụ trách phân hệ truy hồi tài liệu Retrieval."),
        ("Slide 2: Bài toán & Ba tình huống thực tế", "Hằng ngày, phòng đào tạo phải tiếp nhận hàng ngàn thắc mắc giống nhau. Mục tiêu của nhóm là xây dựng một hệ thống tự động: nhận câu hỏi tự do của sinh viên, tìm đúng đoạn thông báo giải đáp, phân loại chủ đề và đặc biệt là BIẾT NÓI TỪ CHỐI khi câu hỏi nằm ngoài phạm vi. Đề bài đặt ra 3 thách thức lớn: câu hỏi diễn đạt lại (paraphrase), câu gõ sai chính tả (typo), và câu hỏi hoàn toàn ngoài lề (out-of-corpus)."),
        ("Slide 3: Dữ liệu & Ba nguyên tắc thép", "Dữ liệu gồm 112 tài liệu được chia đều cho 7 chủ đề nghiệp vụ. Nhóm tuân thủ nghiêm ngặt 3 nguyên tắc thép của môn học: Thứ nhất, tuyệt đối không dùng API của các mô hình ngôn ngữ lớn như ChatGPT hay Claude; Thứ hai, hệ thống phải chạy hoàn toàn offline trên máy cục bộ; Và thứ ba, thuật toán truy hồi phải được tự cài đặt bằng toán học thuần túy."),
        ("Slide 4: Demo nhanh một câu chuẩn", "Để thầy và các bạn dễ hình dung, em xin gõ một câu hỏi thực tế: 'When is tuition due for the semester?'. Như thầy thấy trên màn hình, chỉ mất chưa đầy 5 mili-giây, hệ thống lập tức gắn nhãn intent là Tuition với độ tin cậy 88%, đồng thời hiển thị đúng thông báo về hạn nộp học phí với điểm tương đồng Cosine là 0.54."),
        ("Slide 5: Kiến trúc giải pháp Cổng lọc kép", "Để đạt được kết quả trên, nhóm em không dùng một mô hình đơn lẻ mà thiết kế một Pipeline Cổng Kép song song: Một bên là mô hình Retrieval dùng TF-IDF n-gram ký tự kết hợp Cosine similarity để tìm tài liệu; một bên là mô hình Logistic Regression để thẩm định ý định. Kết quả chỉ được trả về khi vượt qua cả 2 cổng: điểm Cosine phải trên 0.15 và độ tin cậy Intent phải trên 0.34."),
        ("Slide 6: Phương pháp luận đánh giá khoa học", "Để đánh giá công tâm, nhóm sử dụng bộ 120 câu hỏi thử nghiệm và đo lường bằng các chỉ số chuẩn mực của ngành Information Retrieval: MRR (Mean Reciprocal Rank), Hit@3 và End-to-End Accuracy. Nhóm cam kết không nhìn trộm tập test trong quá trình phát triển để tránh rò rỉ dữ liệu."),
        ("Slide 7: Ánh xạ kiến thức môn học", "Toàn bộ giải pháp gắn liền mật thiết với chương trình học CS50 AI: Mô hình Túi từ và N-grams thuộc tuần 6 (Language); Cosine Similarity mở rộng từ Nearest-Neighbor tuần 4; Naive Bayes và Logistic Regression kế thừa từ tuần 2 và tuần 4; và việc hiệu chỉnh ngưỡng từ chối gắn với bài toán ra quyết định trong điều kiện bất định của tuần 2."),
        ("Slide 8: Thuật toán Retrieval cốt lõi", "Trọng tâm của phân hệ Retrieval là mô hình không gian vector. Nhóm áp dụng công thức Smooth IDF chuẩn hóa để tính toán độ quý hiếm của từ, sau đó đo góc Cosine giữa hai vector. Bằng cách chuẩn hóa độ dài vector L2, Cosine triệt tiêu hoàn toàn sự chênh lệch độ dài giữa câu hỏi ngắn và văn bản dài, khắc phục nhược điểm chí mạng của khoảng cách Euclid."),
        ("Slide 9: Vũ khí bí mật: N-gram ký tự", "Phát hiện lớn nhất của nhóm em nằm ở đây: Khi người dùng gõ sai 'conncet' hay dùng từ phái sinh 'registration' thay vì 'register', mô hình theo từ truyền thống sẽ thất bại. Nhóm em đã áp dụng n-gram ký tự 3-5 trong ranh giới từ (char_wb). Nhờ vậy, ngay cả khi gõ sai, các cụm ký tự con vẫn trùng khớp, giúp hệ thống duy trì độ chính xác 100% trên các câu hỏi typo."),
        ("Slide 10: Phân loại Intent & Bí mật xác suất", "Đối với phân loại Intent, nhóm thử nghiệm cả Naive Bayes và Logistic Regression. Logistic Regression đạt độ chính xác 97.1%, nhưng quan trọng hơn là phân phối xác suất của nó cực kỳ trung thực: câu trong kho đạt độ tin cậy 74%, câu ngoài kho tụt xuống 26%. Ngược lại, Naive Bayes do giả định các từ độc lập nên bị tự tin thái quá, câu ngoài kho vẫn báo 45% nên không dùng để chặn lọc được."),
        ("Slide 11: Đồ thị đánh đổi & Sức mạnh Cổng kép", "Nhìn vào đồ thị quét ngưỡng, nếu chỉ dùng ngưỡng Cosine đơn độc, để chặn hết câu ngoài kho ta phải nâng ngưỡng lên 0.40, khiến 25 câu đúng bị từ chối oan. Nhưng khi kết hợp Cổng Intent 0.34, hệ thống chặn trọn vẹn 15/15 câu ngoài kho mà vẫn giữ độ chính xác toàn hệ thống đạt đỉnh 90%!"),
        ("Slide 12: Demo chuyên sâu, Hạn chế & Kết luận", "Sau đây nhóm em xin demo các ca khó nhất: câu gõ sai, câu hỏi ngoài lề và một câu hệ thống đoán sai do từ đồng nghĩa để chứng minh giới hạn của mô hình. Hướng đi cho giai đoạn Final là bổ sung từ điển đồng nghĩa chuyên ngành và nhúng ngữ nghĩa offline. Em xin trân trọng cảm ơn thầy và sẵn sàng bước vào phần phản biện!")
    ]
    for s_title, s_text in slides:
        add_h2(s_title)
        add_p(s_text, line_spacing=1.2)

    # ================= CHƯƠNG 8 =================
    add_h1("CHƯƠNG 8: KỊCH BẢN DEMO THỰC TẾ TRÊN LỚP (6 CÂU THẦN THÁNH)")
    add_p("Khi bước lên bàn demo, hãy gõ lần lượt 6 câu sau đây. Mỗi câu mang một thông điệp kỹ thuật rõ ràng:")

    table4 = doc.add_table(rows=7, cols=3)
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    table4.autofit = False
    format_row(table4.rows[0], is_header=True)
    table4.rows[0].cells[0].paragraphs[0].text = "Câu gõ vào ô tìm kiếm"
    table4.rows[0].cells[1].paragraphs[0].text = "Kết quả hệ thống trả về"
    table4.rows[0].cells[2].paragraphs[0].text = "Lời giải thích trước thầy (Thông điệp)"

    demo_data = [
        ("How do I reset my Student Portal password?", "faq_technical_support_01 (Cosine 0.54, Intent 88%)", "Chứng minh trường hợp tiêu chuẩn hoạt động hoàn hảo, phản hồi siêu tốc dưới 5ms."),
        ("How do I reset my Sutdent Portal password?", "faq_technical_support_01 (Cosine 0.53, Intent 88%)", "Chỉ rõ từ 'Sutdent' bị gõ sai. Điểm số chỉ giảm nhẹ 0.01 nhờ n-gram ký tự vẫn bắt được các cụm ' co', 'con', 'onn'."),
        ("I forgot my Student Portal password - how do I reset it?", "faq_technical_support_01 (Cosine 0.51, Intent 85%)", "Chứng minh khả năng xử lý câu diễn đạt lại (Paraphrase) khi người dùng đổi cấu trúc câu."),
        ("What's the best restaurant near campus for vegan food?", "Hệ thống TỪ CHỐI: 'Information not found' (Intent 31%)", "Chứng minh câu hỏi ngoài phạm vi bị chặn đứng ngay lập tức do độ tin cậy Intent dưới 34%."),
        ("Can I rent a kayak from the campus recreation center?", "Hệ thống TỪ CHỐI: 'Information not found' (Intent 29%)", "ĐIỂM SÁNG: Dù câu có từ 'campus' và 'recreation center' nhưng hệ thống không bị lừa, cổng Intent vẫn chặn thành công!"),
        ("Two of my finals overlap on the same day - who do I tell?", "Hệ thống trả về SAI: faq_class_schedule_02 thay vì faq_exam_02", "TUYỆT CHIÊU ĐIỂM 10: Chủ động giải thích: 'Thưa thầy, đây là giới hạn của mô hình từ vựng cổ điển vì máy không biết overlap đồng nghĩa với conflict. Nhóm em sẽ xử lý triệt để ở vòng Final!'")
    ]
    for idx, row in enumerate(demo_data, start=1):
        format_row(table4.rows[idx], is_header=False)
        for c_idx, val in enumerate(row):
            table4.rows[idx].cells[c_idx].paragraphs[0].text = val

    # ================= CHƯƠNG 9 =================
    add_h1("CHƯƠNG 9: BỘ GIÁP VẤN ĐÁP 10 CÂU HỎI TỬ THẦN (15/40 ĐIỂM)")
    add_p("Hội đồng chấm thi rất thích hỏi sâu vào bản chất toán học và thực nghiệm. Hãy học thuộc lòng 10 câu trả lời đanh thép này:")

    qa_list = [
        ("Câu 1: Vì sao nhóm dùng Cosine Similarity mà không dùng Khoảng cách Euclid?",
         "Thưa thầy, khoảng cách Euclid bị phụ thuộc nặng nề vào độ dài văn bản. Một câu hỏi ngắn 4 từ và một thông báo dài 200 từ sẽ có độ dài vector rất lệch nhau, khiến khoảng cách Euclid rất lớn dù chúng cùng nói về một chủ đề. Ngược lại, Cosine Similarity chỉ đo góc giữa hai vector và chuẩn hóa độ dài về 1.0, giúp so khớp công bằng giữa câu hỏi ngắn và văn bản dài."),
        
        ("Câu 2: Công thức IDF có ý nghĩa gì? Nếu bỏ IDF thì điều gì sẽ xảy ra?",
         "Thưa thầy, IDF đo lường độ quý hiếm của từ trên toàn trường. Từ nào càng đại trà (như 'university', 'campus') thì IDF càng nhỏ; từ nào càng đặc thù thì IDF càng lớn. Nếu bỏ IDF, mô hình sẽ thoái lui về Bag-of-Words thuần: các từ đại trà sẽ thống trị điểm số, làm câu ngoài kho vọt lên 0.61 điểm và không thể nào đặt được ngưỡng từ chối."),
        
        ("Câu 3: Tại sao n-gram ký tự lại chịu được lỗi gõ phím?",
         "Thưa thầy, khi người dùng gõ sai 'conncet', ở mức từ vựng thì đó là từ lạ và bị điểm 0. Nhưng ở mức cụm 3-5 ký tự (char_wb), phép đảo chữ chỉ phá vỡ 1-2 cụm xung quanh vị trí lỗi, các cụm còn lại như ' co', 'con', 'onn' vẫn trùng khớp hoàn toàn với tài liệu gốc, giúp duy trì điểm số cao."),
        
        ("Câu 4: Ngưỡng từ chối được chọn như thế nào? Có bị học vẹt (overfit) vào tập test không?",
         "Thưa thầy, nhóm quét ngưỡng từ 0 đến 0.8 với bước nhảy 0.01 dựa trên chỉ số End-to-End Accuracy. Để chống overfit, nhóm áp dụng 5-fold Cross-Validation: dò tìm ngưỡng trên 4 phần và kiểm chứng trên 1 phần còn lại. Ngưỡng Cosine 0.28-0.29 xuất hiện ổn định ở cả 5 fold, chứng minh phương pháp chọn ngưỡng hoàn toàn vững chắc và khách quan."),
        
        ("Câu 5: Tại sao lỗi gõ phím 1 chữ cái gần như không làm giảm độ chính xác?",
         "Thưa thầy, vì câu hỏi của sinh viên thường dài từ 6 đến 10 từ. Việc gõ sai 1 từ chỉ làm giảm điểm số của riêng từ đó (khoảng 0.05 điểm Cosine), nhưng các từ khóa quan trọng còn lại vẫn đủ sức kéo tài liệu đúng lên vị trí top-1. Độ bền chỉ thực sự bị thử thách khi câu có từ 2 đến 3 lỗi gõ phím trở lên."),
        
        ("Câu 6: Vì sao nhóm chọn Logistic Regression thay vì Naive Bayes?",
         "Thưa thầy, Logistic Regression cho độ chính xác cao hơn (97.1% so với 94.3%). Nhưng lý do quyết định là Naive Bayes bị 'tự tin thái quá' do giả định các từ độc lập, câu ngoài kho nó vẫn tự tin tới 45%. Trong khi đó, Logistic Regression cho ra xác suất cực kỳ trung thực: câu ngoài kho tụt dốc về 26%, giúp nhóm tận dụng làm cổng từ chối thứ hai."),
        
        ("Câu 7: Đã có Retrieval rồi, tại sao vẫn phải phân loại Intent?",
         "Thưa thầy, mô hình Intent phục vụ 2 mục đích sống còn: Thứ nhất là hiển thị nhãn danh mục cho sinh viên trên giao diện; Thứ hai là đóng vai trò 'Cổng kiểm soát thứ hai' trong Pipeline Cổng kép. Riêng ngưỡng Cosine chỉ đạt 85%, nhưng khi có thêm cổng Intent, độ chính xác toàn hệ thống tăng vọt lên 90%."),
        
        ("Câu 8: Tại sao nhóm không dùng các mô hình hiện đại như ChatGPT, BERT hay Transformer?",
         "Thưa thầy, đề bài cấm tuyệt đối việc gọi API LLM và yêu cầu xây dựng hệ thống chạy offline, nhẹ và tức thì trên máy cục bộ. Hơn nữa, phương pháp không gian vector cổ điển có tính minh bạch toán học tuyệt đối (Explainable AI), cho phép giải thích được vì sao tài liệu này được chọn mà không lo ngại nguy cơ 'ảo giác' (hallucination) như LLM."),
        
        ("Câu 9: Độ phức tạp tính toán của hệ thống là bao nhiêu?",
         "Thưa thầy, độ phức tạp mỗi truy vấn là O(độ dài câu hỏi) cho khâu vector hóa và O(N × V_active) cho phép nhân ma trận thưa. Với kho 112 tài liệu, thời gian phản hồi thực tế đo được là dưới 5 mili-giây, hoàn toàn đáp ứng thời gian thực."),
        
        ("Câu 10: Hạn chế lớn nhất của hệ thống hiện tại là gì?",
         "Thưa thầy, hạn chế lớn nhất nằm ở câu Paraphrase (độ chính xác P@1 rơi từ 100% xuống 71.4%). Do mô hình chỉ so khớp mặt chữ nên khi sinh viên dùng từ đồng nghĩa như 'no open seats' thay vì 'full', máy sẽ bị phán đoán sai. Đây chính là mục tiêu mà nhóm em sẽ giải quyết ở giai đoạn Final bằng từ điển đồng nghĩa chuyên ngành.")
    ]

    for q, a in qa_list:
        add_h2(q)
        add_p(a, line_spacing=1.2)

    # Save to all target paths
    for p in output_paths:
        try:
            doc.save(p)
            print(f"Successfully saved document to: {p}")
        except Exception as e:
            print(f"Error saving to {p}: {e}")

if __name__ == "__main__":
    desktop_default = Path("C:/Users/luong/Desktop")
    onedrive_desktop = Path("C:/Users/luong/OneDrive/Máy tính")
    
    out_paths = []
    if desktop_default.exists():
        out_paths.append(str(desktop_default / "Project12_CamNang_LyThuyet_ThuyetTrinh_Midterm.docx"))
    if onedrive_desktop.exists():
        out_paths.append(str(onedrive_desktop / "Project12_CamNang_LyThuyet_ThuyetTrinh_Midterm.docx"))
    
    # Also save a copy inside the repo under notes/
    repo_notes = Path("c:/Users/luong/Documents/antigravity/brave-lavoisier/ain_project/notes")
    if repo_notes.exists():
        out_paths.append(str(repo_notes / "Project12_CamNang_LyThuyet_ThuyetTrinh_Midterm.docx"))
        
    build_document(out_paths)
