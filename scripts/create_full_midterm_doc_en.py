import os
import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

# Import helpers from existing doc_helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_helpers import set_cell_background, set_cell_margins, add_callout, format_row

def build_document_en(output_paths):
    doc = docx.Document()
    
    # 1-inch margins
    for section in doc.sections:
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
    add_p("POSTS AND TELECOMMUNICATIONS INSTITUTE OF TECHNOLOGY / HANOI UNIVERSITY — ARTIFICIAL INTELLIGENCE (AIN)", font_size=10, bold=True, color_rgb=(0x71, 0x80, 0x96), align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("PROJECT 12: CAMPUS NOTICE & FAQ ASSISTANT", font_size=22, bold=True, color_rgb=(0x1A, 0x36, 0x5D), space_before=8, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("ALL-IN-ONE COMPREHENSIVE HANDBOOK: THEORY, ALGORITHMS, CASE STUDIES & MIDTERM PRESENTATION SCRIPT", font_size=13, bold=True, color_rgb=(0x2C, 0x7A, 0x7B), space_before=2, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_callout(doc, 
        "This master handbook has been specially structured following the 'From First Principles to Advanced Mastery' approach. Even if you have never encountered Natural Language Processing (NLP) or Classical Information Retrieval before, this guide will walk you through every mathematical derivation, code line, benchmark experiment, and defense question before the examination board.",
        title="SPECIAL NOTE FOR BEGINNERS & ORAL EXAM PREPARATION"
    )

    # ================= CHAPTER 1 =================
    add_h1("CHAPTER 1: WHAT IS THE REAL-WORLD PROBLEM? (INTUITIVE EXPLANATION)")
    add_p("Imagine you are a freshman who just arrived on university campus. You face hundreds of confusing procedures: When is tuition due? How do I register for classes? Where do I check exam rooms? Who do I contact if the campus Wi-Fi breaks down? Instead of waiting in long lines at the registrar office or waiting days for an email reply, the university wants an intelligent AI assistant (Chatbot / Search Assistant) that answers student questions instantaneously.")

    add_h2("1. Three Real-World Scenarios Handled by the System")
    add_bullet("Scenario 1 — Canonical Question (Normal): ", "A student asks directly using exact wording found in official policies: 'When is tuition due for the semester?'. The system must locate the exact FAQ document regarding payment deadlines and assign the 'tuition' intent label.")
    add_bullet("Scenario 2 — Question with Typo (Typo): ", "A student types quickly on a mobile phone: 'How do I reset my Sutdent Portal password?'. The word 'Student' is mistyped as 'Sutdent'. The system must not crash or fail, but seamlessly recognize character-level similarities to return the correct password reset FAQ.")
    add_bullet("Scenario 3 — Out-of-Corpus Query (Out-of-Corpus - OOC): ", "A student asks: 'What's the best vegan restaurant near campus?' or 'Can I rent a kayak from the campus recreation center?'. The university offers no such service. THE SYSTEM MUST NEVER FABRICATE AN ANSWER. Instead, it must politely abstain: 'Information not found — please contact the administrative office'.")

    add_h2("2. Decomposing One Large System into 3 Sub-Problems")
    add_p("While presenting a single coherent interface, the assistant internally solves 3 distinct classical AI problems:")
    add_bullet("Sub-Problem 1 — Document Retrieval (Information Retrieval): ", "Among 112 campus documents, which document is most relevant to the student query? (Requires no model training; uses geometric vector space similarity).")
    add_bullet("Sub-Problem 2 — Intent Classification: ", "Which of the 7 official business domains does this query belong to: course_registration, exam, tuition, class_schedule, student_services, graduation, technical_support? (Uses supervised machine learning).")
    add_bullet("Sub-Problem 3 — Decision-Making under Uncertainty (Abstention): ", "Does the system possess sufficient confidence to answer, or must it abstain? Balances two opposing risks: Hallucination (answering falsely) vs False Abstention (refusing to answer valid questions).")

    add_h2("3. Midterm Grading Rubric (40 Points Total)")
    table1 = doc.add_table(rows=4, cols=3)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.autofit = False
    format_row(table1.rows[0], is_header=True)
    table1.rows[0].cells[0].paragraphs[0].text = "Grading Item"
    table1.rows[0].cells[1].paragraphs[0].text = "Points"
    table1.rows[0].cells[2].paragraphs[0].text = "Demonstrated Competency Required"
    
    grading_data = [
        ("Vector Space Model & Correct Retrieval", "15 pts", "Correctly implement custom TF-IDF and Cosine similarity (without external black-box library calls in runtime functions), deep understanding of formulas, and ability to calculate manual examples on whiteboard."),
        ("Robustness Analysis & Threshold Calibration", "10 pts", "Objective benchmark comparisons across query types (Normal, Paraphrase, Typo), rigorous threshold selection via Cross-Validation, eliminating guesswork."),
        ("Oral Defense & Live Interactive Demo", "15 pts", "Fluent explanation of theoretical foundations, flawless live demo on a fully offline laptop (zero internet access), and proactive analysis of model strengths and limitations.")
    ]
    for idx, (c1, c2, c3) in enumerate(grading_data, start=1):
        format_row(table1.rows[idx], is_header=False)
        table1.rows[idx].cells[0].paragraphs[0].text = c1
        table1.rows[idx].cells[1].paragraphs[0].text = c2
        table1.rows[idx].cells[2].paragraphs[0].text = c3

    # ================= CHAPTER 2 =================
    add_h1("CHAPTER 2: FROM TEXT TO NUMBERS — FOUNDATIONS OF NLP")
    add_p("Humans understand text through cognitive context and semantic associations. Computers, however, operate purely on binary arithmetic. To enable machine comprehension of university documents, text undergoes a multi-stage numerical transformation:")

    add_h2("1. Preprocessing: Cleaning the Raw Text")
    add_bullet("Lowercasing: ", "Treats 'Tuition' at the sentence start and 'tuition' in the middle as identical tokens.")
    add_bullet("Tokenization: ", "Splits sentences into isolated alphanumeric word tokens using the regular expression [a-z0-9]+, stripping away punctuation marks (., ! ?).")
    add_bullet("Stopwords Removal & The Stopwords Paradox: ", "Standard NLP practice often strips high-frequency words like 'the', 'is', 'at'. HOWEVER, IN THIS SPECIFIC TASK, stripping stopwords causes MRR to drop from 0.927 to 0.896! Why? Student queries are extremely short. Words like 'how', 'when', 'can' carry critical interrogative intent (e.g., 'How to pay tuition' vs 'When is tuition due'). Retaining them preserves essential intent signals.")

    add_h2("2. Bag-of-Words (BoW) — The Naive Starting Point")
    add_p("Imagine gathering all distinct words across all 112 campus documents into a global 'Vocabulary' of thousands of terms. Each sentence is represented as a vector of counts: if a word appears, record its frequency; otherwise, record 0. It is called a 'bag' because word order and syntax are discarded.")
    add_p("Fatal flaw of BoW: It treats common glue words like 'for' or generic terms like 'campus' with the exact same weight as highly discriminative keywords like 'tuition' or 'reschedule'. Under raw counting, any document containing 'campus' receives artificially inflated relevance.")

    add_h2("3. TF-IDF — Scoring the Discriminative Value of Words")
    add_p("TF-IDF fixes the flaw of Bag-of-Words based on an elegant intuitive principle:")
    add_p("• TF (Term Frequency): How often does word t appear in this specific document d? Higher frequency indicates that document d focuses heavily on that topic.\n• IDF (Inverse Document Frequency): How rare is word t across the entire corpus of 112 documents? Words occurring in nearly every notice ('university', 'student') carry zero discriminative power. Words occurring in only 1 or 2 documents ('graduation', 'transcript') carry immense diagnostic value!")

    add_p("Standard scikit-learn smooth_idf formula implemented by our team:")
    add_p("TF-IDF = TF × IDF = TF × [ ln((1 + N) / (1 + DF)) + 1.0 ]", bold=True, color_rgb=(0x1A, 0x36, 0x5D))
    add_bullet("Why the natural logarithm (ln)? ", "By Zipf's Law, term frequency follows a power-law distribution. The logarithm dampens exponential frequency spikes, preventing rare terms from overwhelming other features by millions of times.")
    add_bullet("Why add 1 to the numerator and denominator? ", "Prevents division by zero when an unseen out-of-vocabulary word is encountered.")
    add_bullet("Why add 1.0 outside the logarithm? ", "If a word appears in all N documents (DF = N), ln(1) = 0. Adding 1.0 guarantees that universally occurring words retain a baseline weight of 1.0 rather than being zeroed out entirely.")
    add_bullet("Sublinear TF Scaling (1 + ln(TF)): ", "Softens term repetition. A user repeating 'exam' 10 times is not 10 times more important than one typing it once.")

    add_h2("4. Cosine Similarity — Measuring Direction Instead of Length")
    add_p("Once TF-IDF weights are computed, each document and query becomes an arrow (vector) in high-dimensional space:")
    add_bullet("Why not Euclidean Distance? ", "Euclidean distance measures straight-line physical distance, which is severely distorted by document length! A 500-word detailed policy on tuition and a 4-word query on tuition point in the same direction, but their vector magnitudes differ vastly, making Euclidean distance huge. The computer would mistakenly classify them as unrelated.")
    add_bullet("Cosine Similarity measures the angle: ", "Cosine strictly evaluates vector direction regardless of magnitude. If both vectors point toward the tuition concept, the angle between them is 0 degrees, giving cos(0) = 1.0 (perfect match). The score strictly ranges from 0.0 (orthogonal / unrelated) to 1.0 (identical direction).")

    add_h2("5. Character N-Grams (char_wb 3-5) — The Shield Against Typos")
    add_p("When a user mistypes 'conncet' instead of 'connect':")
    add_p("• At word level: 'conncet' is an unknown token, absent from vocabulary $\to$ Score is 0.0!\n• At character n-gram level (splitting words into 3-5 character slices with word boundaries):")
    add_p("  - 'connect' $\to$ [' co', 'con', 'onn', 'nne', 'nec', 'ect', 'ct ']\n  - 'conncet' $\to$ [' co', 'con', 'onn', 'nnc', 'nce', 'cet', 'et ']")
    add_p("Both words share 3 identical leading n-grams (' co', 'con', 'onn'). The mathematical similarity remains remarkably high! Furthermore, character n-grams naturally capture morphological variations such as 'register' and 'registration'.")

    # ================= CHAPTER 3 =================
    add_h1("CHAPTER 3: ALGORITHM BENCHMARK — WHY THIS SELECTION?")
    add_p("Our team avoided subjective choices. We benchmarked 8 Retrieval algorithms and 5 Intent classifiers head-to-head on the identical evaluation dataset:")

    add_h2("1. Retrieval Tournament: 8 Candidate Algorithms (Tested on 105 In-Scope Queries)")
    table2 = doc.add_table(rows=9, cols=5)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.autofit = False
    format_row(table2.rows[0], is_header=True)
    table2.rows[0].cells[0].paragraphs[0].text = "Retrieval Algorithm"
    table2.rows[0].cells[1].paragraphs[0].text = "MRR (Overall)"
    table2.rows[0].cells[2].paragraphs[0].text = "P@1 Normal"
    table2.rows[0].cells[3].paragraphs[0].text = "P@1 Paraphrase"
    table2.rows[0].cells[4].paragraphs[0].text = "Hit@3"

    retrieval_data = [
        ("TF-IDF char_wb (3-5) [CHAMPION]", "0.943", "1.000", "0.714", "0.981"),
        ("Hybrid (0.5 word + 0.5 char)", "0.936", "1.000", "0.714", "0.952"),
        ("TF-IDF word-level (Default)", "0.927", "1.000", "0.657", "0.952"),
        ("BM25 (k1=1.5, b=0.75 - Industry Standard)", "0.912", "1.000", "0.600", "0.943"),
        ("TF-IDF word 1-2 gram", "0.905", "1.000", "0.600", "0.933"),
        ("TF-IDF word + Stopwords stripped + sublinear", "0.896", "0.971", "0.629", "0.933"),
        ("Bag-of-Words (Count) + Cosine", "0.893", "0.971", "0.571", "0.952"),
        ("LSA (SVD 60-dimensional Latent Semantic)", "0.873", "0.914", "0.600", "0.924")
    ]
    for idx, row in enumerate(retrieval_data, start=1):
        format_row(table2.rows[idx], is_header=False)
        for c_idx, val in enumerate(row):
            table2.rows[idx].cells[c_idx].paragraphs[0].text = val

    add_bullet("Why did Character TF-IDF (char_wb 3-5) win? ", "Achieved highest MRR (0.943). Its margin of victory stems entirely from Paraphrased queries (P@1 = 0.714 vs 0.657) due to morphological sub-word matching.")
    add_bullet("Why eliminate BM25 despite being the search engine standard? ", "BM25 scores are unbounded (ranging from 7 to 19 depending on length), making a fixed rejection threshold impossible across dynamic corpora. Furthermore, on this compact 112-document corpus, BM25 (0.912) significantly lagged behind char TF-IDF (0.943).")
    add_bullet("Why eliminate LSA (Latent Semantic Analysis)? ", "LSA requires tens of thousands of documents to learn robust co-occurrence singular value decompositions. On only 112 documents, LSA blurred class boundaries, causing out-of-corpus queries to receive high similarity scores (averaging 0.67).")

    add_h2("2. Intent Classification Face-Off: Naive Bayes vs Logistic Regression")
    add_bullet("Multinomial Naive Bayes (94.3% Accuracy): ", "A generative model computing prior class frequencies and likelihoods via Bayes rule. Fatal drawback: The conditional independence assumption causes probability values to polarize sharply near 1.0 or 0.0. On Out-of-Corpus queries, it remains stubbornly overconfident (averaging 0.45 / 45% confidence), making it useless as an abstention gate.")
    add_bullet("Logistic Regression (97.1% Accuracy - CHAMPION): ", "A discriminative model directly optimizing decision boundaries via multi-class Softmax loss. Crucially, its predicted probabilities are exceptionally well-calibrated: in-scope queries average 0.74 (74% confidence), while out-of-corpus queries plummet to 0.26 (26%), barely above random chance (1/7 = 14.3%). This calibration makes it the ultimate gatekeeper!")

    # ================= CHAPTER 4 =================
    add_h1("CHAPTER 4: THE ART OF ABSTENTION & DUAL-GATE ARCHITECTURE")
    add_p("This represents our team's most impactful architectural innovation, solving the most difficult challenge in the project: How do we reject 100% of out-of-corpus queries without discarding valid student questions?")

    add_h2("1. The Deadlock of Single-Threshold Cosine")
    add_p("In practice:")
    add_bullet("Valid in-scope queries: ", "Difficult paraphrased queries can have a top Cosine similarity as low as 0.17.")
    add_bullet("Out-of-corpus queries: ", "Off-topic questions like 'Can I rent a kayak from the campus recreation center?' accidentally share words like 'campus', 'center', 'can I', pushing their Cosine score up to 0.39!")
    add_p("Mathematical deadlock: In-scope scores [0.17 - 1.0] and out-of-corpus scores [0.0 - 0.39] overlap heavily! A single Cosine threshold of 0.28 (optimal trade-off) only blocks 11/15 out-of-corpus queries. Pushing the threshold to 0.40 to block all 15 queries results in rejecting 25 valid student queries falsely!")

    add_h2("2. The Dual-Gate Architecture Solution")
    add_p("Instead of relying on a single geometric score, our system combines two orthogonal signals:")
    add_p("A QUERY IS ANSWERED ONLY IF IT PASSES BOTH GATES:\n1. Top Cosine similarity score s >= 0.15 (Floor gate rejecting complete noise)\n2. Intent classification confidence p >= 0.34 (Semantic business domain validation)", bold=True, color_rgb=(0x1A, 0x36, 0x5D))

    add_p("Why does the Intent Gate successfully intercept tricky out-of-corpus queries?")
    add_p("A question about 'kayaks' may share casual words with campus notices, but its core topic belongs to none of the 7 business domains (it is neither exam, nor tuition, nor registration). Logistic Regression divides its probability mass across all 7 classes, leaving each with only 0.15 - 0.25 confidence. Because 0.25 < 0.34, the Intent Gate slams shut and triggers ABSTENTION!")
    add_p("Result: End-to-End accuracy rises from 85% to 90%, blocking 15/15 out-of-corpus queries completely!")

    # ================= CHAPTER 5 =================
    add_h1("CHAPTER 5: EVALUATION METRICS & TERMINOLOGY GLOSSARY")
    add_p("Quick reference guide to speak fluent, rigorous evaluation terminology before the examination board:")

    table3 = doc.add_table(rows=8, cols=3)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table3.autofit = False
    format_row(table3.rows[0], is_header=True)
    table3.rows[0].cells[0].paragraphs[0].text = "Metric / Term"
    table3.rows[0].cells[1].paragraphs[0].text = "What Does It Measure?"
    table3.rows[0].cells[2].paragraphs[0].text = "Intuitive Understanding"

    metric_data = [
        ("MRR (Mean Reciprocal Rank)", "Ranking quality of the target document", "Averages 1 divided by the rank of the true document. Rank 1 = 1/1 = 1.0 pt. Rank 2 = 1/2 = 0.5 pt. Rank 10 = 1/10 = 0.1 pt. Higher MRR indicates the true answer consistently appears at the top."),
        ("P@1 (Precision at 1)", "Top-1 result correctness", "Was the very first document returned correct? Binary: 1 if yes, 0 if no."),
        ("P@3 (Precision at 3)", "Precision within top 3 results", "Number of correct documents in top 3 divided by 3. ORAL DEFENSE TRAP: Because each query has EXACTLY 1 true target document in the corpus, P@3 can NEVER exceed 1/3 = 0.333! It cannot reach 1.0."),
        ("Hit@3", "Top-3 recall presence", "Did the true document appear anywhere in the top 3? 1 if yes, 0 if no. Much more intuitive to report than P@3."),
        ("Intent Accuracy", "Classification correctness", "Percentage of in-scope queries assigned the correct business intent."),
        ("End-to-End Accuracy", "Holistic system accuracy", "Most stringent metric: In-scope queries must NOT abstain AND must achieve Hit@1 = 1; Out-of-corpus queries must successfully abstain with an empty list []."),
        ("5-fold Cross-Validation", "Out-of-sample parameter tuning", "Splits the 120 queries into 5 folds, tuning thresholds on 4 folds and testing on the remaining 1 fold to guarantee thresholds are generalizable and not overfitted.")
    ]
    for idx, row in enumerate(metric_data, start=1):
        format_row(table3.rows[idx], is_header=False)
        for c_idx, val in enumerate(row):
            table3.rows[idx].cells[c_idx].paragraphs[0].text = val

    # ================= CHAPTER 6 =================
    add_h1("CHAPTER 6: ERROR ANALYSIS & MODEL BOUNDARIES")
    add_p("In academic defense, an engineering team that understands EXACTLY WHERE AND WHY their system fails earns far higher credibility than one claiming artificial perfection. Master these error archetypes:")
    add_bullet("1. Synonyms Failure: ", "Student asks: '...the class section I need has no open seats?'. Official FAQ states: 'section ... is full'. Because classical lexical models match character strings rather than semantic embeddings, the system fails to bridge 'no open seats' and 'full'.")
    add_bullet("2. Temporal & Schedule Overlap (Conflict vs Overlap): ", "Student asks: 'Two of my finals overlap on the same day - who do I tell?'. The true target is faq_exam_02 (exam conflict). Due to the presence of 'day' and scheduling syntax, the model misroutes to class schedule conflicts.")
    add_bullet("3. Cross-Domain Holds: ", "Student asks about a 'registration hold'. The system struggles between course_registration (the affected action) and tuition (the root financial cause of the hold).")
    add_p("💡 Roadmap for Final Round: Integrate a domain-specific synonym dictionary and evaluate offline semantic sentence transformer embeddings.")

    # ================= CHAPTER 7 =================
    add_h1("CHAPTER 7: SLIDE-BY-SLIDE PRESENTATION SCRIPT")
    add_p("The following complete presentation script is written in confident, natural, professional English for your 10-15 minute oral delivery:")

    slides_en = [
        ("Slide 1: Title & Introduction", "Good morning, respected professors and fellow students. Today, our team proudly presents Project 12: An intelligent Campus Notice and FAQ Assistant. Our team consists of three members: Vinh, leading evaluation and benchmarking; Duong, heading intent classification and UI; and myself, Viet Anh, leading the retrieval engine and vector space architecture."),
        ("Slide 2: Problem Definition & Three Real-World Scenarios", "Every semester, university administrative offices face thousands of repetitive inquiries. Our goal is to deploy an autonomous assistant that accepts free-form student queries, retrieves the exact official notice, predicts business intent, and crucially, ABSTAINS when queries fall outside the university scope. We specifically tackle three core challenges: paraphrased expressions, typographical errors, and off-topic queries."),
        ("Slide 3: Data & Three Engineering Iron Rules", "Our corpus comprises 112 official documents balanced across 7 administrative intents. We strictly adhered to three engineering rules: First, zero calls to hosted LLM APIs like ChatGPT or Claude; Second, 100% offline execution on local hardware; And third, implementing our retrieval core from mathematical first principles."),
        ("Slide 4: Quick Baseline Demo", "To demonstrate immediate functionality, observe this standard query: 'When is tuition due for the semester?'. Within 5 milliseconds, our offline engine predicts the 'tuition' intent with 88% confidence and surfaces the exact payment policy notice with a Cosine similarity score of 0.54."),
        ("Slide 5: Dual-Gate Architecture Pipeline", "To achieve high reliability, we reject monolithic designs in favor of an orthogonal Dual-Gate Pipeline: One pipeline executes character n-gram TF-IDF retrieval for document ranking; a parallel pipeline runs multi-class Logistic Regression for intent confidence. A query is answered if and only if it clears both gates: Cosine score at least 0.15, and intent confidence at least 0.34."),
        ("Slide 6: Rigorous Scientific Evaluation Methodology", "We benchmarked our engine against 120 rigorous evaluation queries across standard IR metrics: Mean Reciprocal Rank (MRR), Hit@3, and End-to-End Accuracy. We maintained a strict split discipline to prevent any data leakage into test sets."),
        ("Slide 7: Direct Curriculum Mapping (CS50 AI)", "Our architecture directly maps to our course curriculum: Bag-of-Words and N-grams derive from Week 6 (Language); Cosine Similarity expands Week 4's Nearest-Neighbor to high-dimensional space; Naive Bayes and Logistic Regression build upon Week 2 (Uncertainty) and Week 4 (Learning); and threshold calibration models decision-making under uncertainty."),
        ("Slide 8: Core Mathematical Retrieval Engine", "At the core of retrieval is our custom Vector Space Model. We compute scikit-learn smooth_idf weights and measure angular alignment via Cosine similarity. By applying L2 vector normalization, Cosine similarity eliminates document length bias, resolving the fundamental flaw of Euclidean distance."),
        ("Slide 9: Secret Weapon: Character N-Grams (char_wb 3-5)", "Our key empirical breakthrough lies in character-level modeling: While word-level tokenization completely fails on typos like 'conncet' or morphological variants like 'registration', our 3-to-5 character n-grams preserve sub-word n-gram overlaps, securing 100% accuracy on typo queries."),
        ("Slide 10: Intent Classification: Generative vs Discriminative", "Comparing Naive Bayes and Logistic Regression, Logistic Regression not only achieved 97.1% accuracy, but proved decisively superior in probability calibration. While Naive Bayes produced overconfident probabilities on off-topic queries (averaging 45%), Logistic Regression plummeted to 26%, providing the exact signal needed to filter out-of-corpus queries."),
        ("Slide 11: Threshold Trade-Off & Dual-Gate Mastery", "Analyzing our threshold sweep curve, a single Cosine gate requires raising the threshold to 0.40 to stop all off-topic queries, which falsely rejects 25 valid questions. By coupling a 0.15 Cosine floor with our 0.34 Intent confidence gate, we achieve 90% End-to-End accuracy and eliminate 100% of out-of-corpus queries!"),
        ("Slide 12: Error Analysis, Limitations & Conclusion", "We conclude by actively highlighting our system boundaries: Paraphrased queries without lexical overlap remain the primary challenge. Our Final-round roadmap focuses on domain-specific synonym expansion and offline sentence transformers. Thank you for your attention, and we welcome your questions!")
    ]
    for s_title, s_text in slides_en:
        add_h2(s_title)
        add_p(s_text, line_spacing=1.2)

    # ================= CHAPTER 8 =================
    add_h1("CHAPTER 8: LIVE DEMO PROTOCOL (6 GOLDEN QUERIES)")
    add_p("During the live interactive demo, execute the following 6 queries in exact sequence. Each query demonstrates a distinct technical triumph:")

    table4 = doc.add_table(rows=7, cols=3)
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    table4.autofit = False
    format_row(table4.rows[0], is_header=True)
    table4.rows[0].cells[0].paragraphs[0].text = "Input Query"
    table4.rows[0].cells[1].paragraphs[0].text = "System Output"
    table4.rows[0].cells[2].paragraphs[0].text = "Oral Takeaway for Examiners"

    demo_data_en = [
        ("How do I reset my Student Portal password?", "faq_technical_support_01 (Cosine 0.54, Intent 88%)", "Proves standard canonical workflow performs with sub-5ms latency."),
        ("How do I reset my Sutdent Portal password?", "faq_technical_support_01 (Cosine 0.53, Intent 88%)", "Highlight the typo 'Sutdent'. Score dips by only 0.01 thanks to char n-grams retaining ' co', 'con', 'onn' sub-tokens."),
        ("I forgot my Student Portal password - how do I reset it?", "faq_technical_support_01 (Cosine 0.51, Intent 85%)", "Proves system robustness against sentence restructuring and paraphrasing."),
        ("What's the best restaurant near campus for vegan food?", "SYSTEM ABSTAINS: 'Information not found' (Intent 31%)", "Proves completely off-topic queries are immediately blocked by the 0.34 Intent confidence gate."),
        ("Can I rent a kayak from the campus recreation center?", "SYSTEM ABSTAINS: 'Information not found' (Intent 29%)", "CRITICAL HIGHLIGHT: Despite containing keywords 'campus' and 'recreation center', the system is not fooled and abstains correctly!"),
        ("Two of my finals overlap on the same day - who do I tell?", "System returns INCORRECT: faq_class_schedule_02 instead of faq_exam_02", "PERFECT-SCORE TECHNIQUE: Proactively state: 'Professors, this highlights the inherent boundary of lexical matching—the system lacks semantic awareness that overlap equals conflict. We address this in Final!'")
    ]
    for idx, row in enumerate(demo_data_en, start=1):
        format_row(table4.rows[idx], is_header=False)
        for c_idx, val in enumerate(row):
            table4.rows[idx].cells[c_idx].paragraphs[0].text = val

    # ================= CHAPTER 9 =================
    add_h1("CHAPTER 9: THE 10 FATAL DEFENSE QUESTIONS & BULLETPROOF ANSWERS")
    add_p("Examination boards consistently probe the mathematical boundaries of student projects. Memorize these 10 authoritative, theoretically rigorous responses:")

    qa_list_en = [
        ("Question 1: Why did your team choose Cosine Similarity over Euclidean Distance?",
         "Professors, Euclidean distance is severely distorted by document length. A short 4-word query and a 200-word official notice produce vectors with vastly different magnitudes, resulting in a large Euclidean distance even when discussing the exact same topic. In contrast, Cosine Similarity strictly measures the angular deviation between vectors and normalizes lengths to 1.0, ensuring completely equitable comparison regardless of document verbosity."),
        
        ("Question 2: What is the theoretical role of IDF? What happens if IDF is eliminated?",
         "Professors, IDF quantifies the global rarity and discriminative power of terms across the entire corpus. Universal terms like 'university' receive low IDF weights, while specialized terms receive high IDF weights. Eliminating IDF reduces our model to raw Bag-of-Words: ubiquitous noise words dominate relevance calculations, causing off-topic queries to score as high as 0.61 Cosine similarity, rendering threshold-based abstention impossible."),
        
        ("Question 3: Why are Character N-Grams inherently robust against typographical errors?",
         "Professors, when a user mistypes 'conncet', word-level models treat it as an unknown out-of-vocabulary token with zero weight. However, under character n-grams (char_wb 3-5), a two-character transposition disrupts only 1 or 2 localized sub-word slices; remaining slices like ' co', 'con', and 'onn' match the legitimate index perfectly, preserving strong similarity scores."),
        
        ("Question 4: How was the abstention threshold selected? Is it overfitted to the test queries?",
         "Professors, we swept thresholds from 0.0 to 0.8 in 0.01 increments using End-to-End Accuracy as the objective function. To guarantee out-of-sample validity and prevent overfitting, we conducted 5-fold Cross-Validation. The Cosine threshold converged solidly at 0.28-0.29 across all 5 folds, confirming our methodology is mathematically sound and generalizable."),
        
        ("Question 5: Why did single-character typos produce virtually no drop in retrieval metrics?",
         "Professors, authentic student queries span 6 to 10 words. A single transposed typo reduces the similarity contribution of that specific word by only ~0.05 Cosine points, leaving remaining keywords fully intact to pull the target document to rank 1. Robustness boundaries are only genuinely tested under multiple compound typos (2 to 3 errors per query)."),
        
        ("Question 6: Why did you select Logistic Regression over Naive Bayes for intent classification?",
         "Professors, Logistic Regression not only delivered higher accuracy (97.1% vs 94.3%), but provided vastly superior probability calibration. Due to its flawed conditional independence assumption, Naive Bayes exhibits extreme overconfidence, assigning ~45% probability even to off-topic queries. Logistic Regression probabilities drop to 26% on off-topic inputs, providing an ideal abstention trigger."),
        
        ("Question 7: If Retrieval already returns relevant documents, why classify Intent at all?",
         "Professors, Intent classification fulfills two indispensable roles: First, it renders categorical visual badges on the student UI; Second, and most importantly, it functions as Gate 2 in our Dual-Gate Pipeline. While Cosine thresholding alone achieves 85% accuracy, adding the Intent Gate raises total system End-to-End accuracy to 90%."),
        
        ("Question 8: Why didn't you utilize modern Transformer architectures like ChatGPT or BERT?",
         "Professors, project constraints strictly forbid hosted LLM APIs and mandate lightweight, offline local execution. Furthermore, classical Vector Space Models offer complete mathematical explainability (XAI), allowing us to inspect the exact feature contribution of every token without suffering from LLM hallucination."),
        
        ("Question 9: What is the computational complexity of your inference pipeline?",
         "Professors, query inference complexity is O(|query|) for tokenization and O(N * V_active) for sparse matrix vector multiplication. Across our 112-document corpus, actual measured query latency is below 5 milliseconds, providing instantaneous real-time response."),
        
        ("Question 10: What is the primary performance bottleneck of the current system?",
         "Professors, the fundamental limitation lies in Lexical Paraphrasing (where P@1 drops from 100% to 71.4%). Because string-matching models possess no semantic embedding space, synonyms like 'no open seats' and 'full' fail to align. Resolving this via domain synonym dictionaries and offline semantic embeddings represents our primary roadmap for the Final phase.")
    ]

    for q, a in qa_list_en:
        add_h2(q)
        add_p(a, line_spacing=1.2)

    # Save to all target paths
    for p in output_paths:
        try:
            doc.save(p)
            print(f"Successfully saved English document to: {p}")
        except Exception as e:
            print(f"Error saving to {p}: {e}")

if __name__ == "__main__":
    desktop_default = Path("C:/Users/luong/Desktop")
    onedrive_desktop = Path("C:/Users/luong/OneDrive/Máy tính")
    repo_notes = Path("c:/Users/luong/Documents/antigravity/brave-lavoisier/ain_project/notes")
    
    out_paths = []
    if desktop_default.exists():
        out_paths.append(str(desktop_default / "Project12_Comprehensive_Handbook_Midterm_EN.docx"))
        out_paths.append(str(desktop_default / "Project12_CamNang_LyThuyet_ThuyetTrinh_Midterm_EN.docx"))
    if onedrive_desktop.exists():
        out_paths.append(str(onedrive_desktop / "Project12_Comprehensive_Handbook_Midterm_EN.docx"))
    if repo_notes.exists():
        out_paths.append(str(repo_notes / "Project12_Comprehensive_Handbook_Midterm_EN.docx"))
        
    build_document_en(out_paths)
