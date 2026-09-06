import os, re, streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl!important; text-align: right!important; }
* { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:14px!important; width:100%!important; font-weight:bold!important; font-size:17px!important; padding:12px!important; }
.answer-box { background:#eaf7f0; padding:22px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; line-height:2; }
.disclaimer-box { background:#fef9e7; padding:16px; border-radius:12px; border:1px solid #f5d78e; margin-top:18px; font-size:14px; }
/* يخفي تلميح Streamlit التلقائي بالإنجليزي ("Press Enter to apply") تحت خانة الكتابة */
div[data-testid="InputInstructions"] { display:none !important; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1.2, 1])
with c2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)

st.markdown("<h1 style='text-align:center!important; font-size:32px!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center!important; font-size:26px!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center!important; font-size:18px!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

q = st.text_input(" ", placeholder="اكتب سؤالك هنا...")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"
OUT = "هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH = (
    "تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، "
    "وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:"
    f"<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"
)

# --- Arabic-aware stopword list (kept small on purpose) ---
STOPWORDS = {
    "من", "الى", "إلى", "عن", "على", "في", "هل", "ما", "ماذا", "و", "او", "أو",
    "هو", "هي", "هم", "لا", "نعم", "كيف", "متى", "اين", "أين", "ال", "التي",
    "الذي", "كم", "لماذا", "مع", "هذا", "هذه", "ذلك", "تلك", "كان", "يكون",
}

# --- Verified facts & Academic Calendar override -----------------------------
VERIFIED_FACTS = """
عميد الكلية: الأستاذ الدكتور عبدالله محمد الدهمش

مفهوم الإرشاد الأكاديمي: خدمة أكاديمية تهدف إلى التعرف على المشكلات التي تعوق قدرة الطالب على التحصيل العلمي والتفاعل مع متطلبات الحياة الجامعية، وتعمل على تقديم المساعدة والدعم عن طريق زيادة وعي الطلبة بمسؤولياتهم.

=== التقويم الأكاديمي المعتمد لكليات الرؤية (الفصول الدراسية الثلاثة) ===

--- الفصل الدراسي الأول ---
- بداية التهيئة والتسجيل للفصل الدراسي الأول: الأحد 1448/03/03 هـ (الموافق 16/08/2026 م)
- بداية الدراسة للفصل الدراسي الأول: الأحد 1448/03/10 هـ (الموافق 23/08/2026 م)
- بداية فترة الحذف والإضافة للفصل الدراسي الأول: الأحد 1448/03/10 هـ (الموافق 23/08/2026 م)
- آخر موعد لتأجيل الفصل الدراسي الأول: الخميس 1448/03/21 هـ (الموافق 03/09/2026 م)
- نهاية فترة الحذف والإضافة للفصل الدراسي الأول: الخميس 1448/03/21 هـ (الموافق 03/09/2026 م)
- إجازة اليوم الوطني: الأربعاء والخميس 1448/04/12 - 1448/04/13 هـ (الموافق 23/09/2026 - 24/09/2026 م)
- بداية اختبارات منتصف الفصل الدراسي الأول: الخميس 1448/04/27 هـ (الموافق 08/10/2026 م)
- نهاية اختبارات منتصف الفصل الدراسي الأول: الأحد 1448/05/07 هـ (الموافق 18/10/2026 م)
- إجازة نهاية أسبوع مطولة: الأربعاء والخميس 1448/06/15 - 1448/06/16 هـ (الموافق 25/11/2026 - 26/11/2026 م)
- آخر موعد للاعتذار عن الفصل الدراسي الأول أو الانسحاب عن دراسة مقرر: الخميس 1448/06/23 هـ (الموافق 03/12/2026 م)
- بداية الاختبارات النهائية للفصل الدراسي الأول: الأحد 1448/07/11 هـ (الموافق 20/12/2026 م)
- نهاية الاختبارات النهائية للفصل الدراسي الأول: السبت 1448/07/24 هـ (الموافق 02/01/2027 م)
- بداية إجازة منتصف العام الدراسي: الأحد 1448/07/25 هـ (الموافق 03/01/2027 م)

--- الفصل الدراسي الثاني ---
- بداية التهيئة والتسجيل للفصل الدراسي الثاني: الأحد 1448/08/02 هـ (الموافق 10/01/2027 م)
- بداية الدراسة للفصل الدراسي الثاني: الأحد 1448/08/09 هـ (الموافق 17/01/2027 م)
- بداية فترة الحذف والإضافة للفصل الدراسي الثاني: الأحد 1448/08/09 هـ (الموافق 17/01/2027 م)
- آخر موعد لتأجيل الفصل الدراسي الثاني: الخميس 1448/08/20 هـ (الموافق 28/01/2027 م)
- نهاية فترة الحذف والإضافة للفصل الدراسي الثاني: الخميس 1448/08/20 هـ (الموافق 28/01/2027 م)
- إجازة يوم التأسيس: الأحد والاثنين 1448/09/14 - 1448/09/15 هـ (الموافق 21/02/2027 - 22/02/2027 م)
- بداية إجازة عيد الفطر: الثلاثاء 1448/09/16 هـ (الموافق 23/02/2027 م)
- بداية الدراسة بعد إجازة عيد الفطر: الأحد 1448/10/06 هـ (الموافق 14/03/2027 م)
- بداية اختبارات منتصف الفصل الدراسي الثاني: الخميس 1448/10/17 هـ (الموافق 25/03/2027 م)
- نهاية اختبارات منتصف الفصل الدراسي الثاني: الأحد 1448/10/27 هـ (الموافق 04/04/2027 م)
- آخر موعد للاعتذار عن الفصل الدراسي الثاني أو الانسحاب عن مقرر: الخميس 1448/12/07 هـ (الموافق 13/05/2027 م)
- بداية إجازة عيد الأضحى: نهاية دوام يوم الخميس 1448/12/07 هـ (الموافق 13/05/2027 م)
- بداية الدراسة بعد إجازة عيد الأضحى: الأحد 1448/12/17 هـ (الموافق 23/05/2027 م)
- بداية الاختبارات النهائية للفصل الدراسي الثاني: الأحد 1449/01/01 هـ (الموافق 06/06/2027 م)
- نهاية الاختبارات النهائية للفصل الدراسي الثاني: السبت 1449/01/14 هـ (الموافق 19/06/2027 م)
- بداية إجازة نهاية العام الدراسي: الأحد 1449/01/15 هـ (الموافق 20/06/2027 م)

--- الفصل الدراسي الصيفي ---
- بداية التهيئة والتسجيل للفصل الصيفي: الأحد 1449/01/15 هـ (الموافق 20/06/2027 م)
- بداية الدراسة للفصل الصيفي: الأحد 1449/01/22 هـ (الموافق 27/06/2027 م)
- بداية فترة الحذف والإضافة للفصل الصيفي: الأحد 1449/01/22 هـ (الموافق 27/06/2027 م)
- نهاية فترة الحذف والإضافة للفصل الصيفي: الخميس 1449/01/26 هـ (الموافق 01/07/2027 م)
- بداية اختبارات منتصف الفصل الصيفي: الأحد 1449/02/14 هـ (الموافق 18/07/2027 م)
- نهاية اختبارات منتصف الفصل الصيفي: السبت 1449/02/20 هـ (الموافق 24/07/2027 م)
- آخر موعد للاعتذار عن الفصل الصيفي أو الانسحاب عن مقرر: الأحد 1449/02/21 هـ (الموافق 25/07/2027 م)
- بداية الاختبارات النهائية للفصل الصيفي: الأحد 1449/03/06 هـ (الموافق 08/08/2027 م)
- نهاية الاختبارات النهائية للفصل الصيفي: السبت 1449/03/12 هـ (الموافق 14/08/2027 م)
- بداية إجازة نهاية العام الدراسي: الأحد 1449/03/13 هـ (الموافق 15/08/2027 م)
- بداية الدراسة للعام الدراسي الجديد 1448-1449 هـ: الأحد 1449/03/20 هـ (الموافق 22/08/2027 م)
"""

HOLIDAY_WORDS = {"اجازه", "اجازات", "عطله", "عطلات", "عطل"}
EXCUSE_WORDS = {"عذر", "اعذار", "وفاه", "ولاده", "مرضيه", "مرض", "مريض"}
ACTIVITY_WORDS = {"نشاط", "نشاطات", "انشطه", "أنشطة", "فعاليه", "فعاليات", "خطة", "خطه", "شهر", "أكتوبر", "اكتوبر", "سبتمبر", "نوفمبر", "ديسمبر", "يناير", "فبراير", "مارس", "أبريل", "ابريل", "مايو", "أغسطس", "اغسطس"}
EXCUSE_SOURCE_HINTS = ("excuse", "عذر")
CALENDAR_SOURCE_HINTS = ("تقويم", "calendar")
ACTIVITY_SOURCE_HINTS = ("أنشطة", "الأنشطة", "انشطة", "الأنشطه", "activity")

def unscramble_reversed_arabic_line(line: str) -> str:
    rev = line[::-1]
    rev = re.sub(r"[A-Za-z0-9]+", lambda m: m.group()[::-1], rev)
    return rev

_COMMON_ARABIC_WORDS = ("الكلية", "الطلاب", "برنامج", "الرياض", "الأنشطة")

def pdf_text_is_reversed(sample_text: str) -> bool:
    if any(w in sample_text for w in _COMMON_ARABIC_WORDS):
        return False
    fixed = "\n".join(unscramble_reversed_arabic_line(l) for l in sample_text.split("\n"))
    return any(w in fixed for w in _COMMON_ARABIC_WORDS)

def normalize_arabic(text: str) -> str:
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)  # strip tashkeel
    return text

def read_all_chunks():
    chunks = []
    warnings = []
    for f in sorted(os.listdir(".")):
        low = f.lower()
        if low.endswith(".txt"):
            for enc in ["utf-8", "utf-8-sig", "windows-1256"]:
                try:
                    with open(f, "r", encoding=enc, errors="ignore") as file:
                        t = file.read()
                        if len(t.strip()) > 20:
                            for para in re.split(r"\n\s*\n", t):
                                para = para.strip()
                                if len(para) > 5:
                                    chunks.append((f, para))
                            break
                except Exception:
                    pass
        elif low.endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(f) as pdf:
                    sample = ""
                    for p in pdf.pages[:2]:
                        sample += (p.extract_text() or "")
                    is_reversed = pdf_text_is_reversed(sample)

                    for page_num, page in enumerate(pdf.pages, start=1):
                        try:
                            text = page.extract_text() or ""
                            if is_reversed:
                                text = "\n".join(
                                    unscramble_reversed_arabic_line(l) for l in text.split("\n")
                                )
                            flat_text = re.sub(r"\s+", " ", text)
                            heading_match = re.search(r"أنشطة\s+شهر\s+\S+(?:\s+\S+)?", flat_text)
                            heading = heading_match.group().strip() if heading_match else ""

                            for table in (page.extract_tables() or []):
                                for row in table:
                                    cells = []
                                    for c in row:
                                        if not c:
                                            continue
                                        c = str(c).strip()
                                        if is_reversed:
                                            c = "\n".join(
                                                unscramble_reversed_arabic_line(l)
                                                for l in c.split("\n")
                                            )
                                        if c:
                                            cells.append(c)
                                    if cells:
                                        row_text = " | ".join(cells)
                                        if heading:
                                            row_text = f"{heading} — {row_text}"
                                        chunks.append((f, row_text))

                            for para in re.split(r"\n\s*\n", text):
                                para = para.strip()
                                if len(para) > 5:
                                    chunks.append((f, para))
                        except Exception as page_err:
                            warnings.append(f"{f} (صفحة {page_num}): {page_err}")
            except Exception as file_err:
                warnings.append(f"{f}: فشل pdfplumber — {file_err}")
                try:
                    import fitz
                    doc = fitz.open(f)
                    for page in doc:
                        text = page.get_text()
                        for para in re.split(r"\n\s*\n", text):
                            para = para.strip()
                            if len(para) > 5:
                                chunks.append((f, para))
                except Exception as fallback_err:
                    warnings.append(f"{f}: فشل الاحتياطي أيضًا — {fallback_err}")
        elif low.endswith((".xlsx", ".xls", ".csv")):
            try:
                import pandas as pd
                df = (
                    pd.read_excel(f, dtype=str).fillna("")
                    if not low.endswith(".csv")
                    else pd.read_csv(f, dtype=str).fillna("")
                )
                for _, row in df.iterrows():
                    line = " | ".join([str(v).strip() for v in row.values if str(v).strip() != ""])
                    if len(line) > 5:
                        chunks.append((f, line))
            except Exception:
                pass
        elif low.endswith(".docx"):
            try:
                import docx
                d = docx.Document(f)
                for para in d.paragraphs:
                    t = para.text.strip()
                    if len(t) > 5:
                        chunks.append((f, t))
            except Exception:
                pass
    return chunks, warnings

def score_chunk(question_words, question_bigrams, src, chunk_text, prefer_calendar, avoid_excuse, prefer_activity):
    norm_chunk = normalize_arabic(chunk_text)
    score = 0
    for w in question_words:
        if w in norm_chunk:
            score += 2
    for bg in question_bigrams:
        if bg in norm_chunk:
            score += 4

    src_low = src.lower()
    if avoid_excuse and any(h in src_low or h in src for h in EXCUSE_SOURCE_HINTS):
        score -= 5
    if prefer_calendar and any(h in src_low or h in src for h in CALENDAR_SOURCE_HINTS):
        score += 3
    if prefer_activity and any(h in src_low or h in src for h in ACTIVITY_SOURCE_HINTS):
        score += 8  # إعطاء أولوية مرتفعة لملف الأنشطة عند السؤال عنها

    return score

def build_relevant_corpus(question, chunks, max_chars=8000, top_k=35):
    norm_q = normalize_arabic(question)
    q_words = [w for w in re.split(r"\s+", norm_q) if w and w not in STOPWORDS and len(w) > 1]
    q_bigrams = [f"{a} {b}" for a, b in zip(q_words, q_words[1:])]

    asks_about_holiday = any(w in HOLIDAY_WORDS for w in q_words)
    asks_about_excuse = any(w in EXCUSE_WORDS for w in q_words)
    asks_about_activity = any(w in ACTIVITY_WORDS for w in q_words)

    prefer_calendar = asks_about_holiday and not asks_about_excuse
    avoid_excuse = asks_about_holiday and not asks_about_excuse
    prefer_activity = asks_about_activity

    if not q_words or not chunks:
        joined = "\n".join(c for _, c in chunks)
        return VERIFIED_FACTS + "\n" + joined[:max_chars]

    scored = [
        (score_chunk(q_words, q_bigrams, src, c, prefer_calendar, avoid_excuse, prefer_activity), src, c)
        for src, c in chunks
    ]
    
    # إذا كان السؤال عن الأنشطة، نلتقط أجزاء ملف الأنشطة حتى لو لم ينطبق السكور التلقائي عليها بشكل كامل
    if prefer_activity:
        for idx, (sc, src, c) in enumerate(scored):
            if any(h in src for h in ACTIVITY_SOURCE_HINTS):
                scored[idx] = (sc + 5, src, c)

    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        joined = "\n".join(c for _, c in chunks)
        return VERIFIED_FACTS + "\n" + joined[:max_chars]

    selected = []
    total_len = 0
    for score, src, c in scored[:top_k]:
        if total_len + len(c) > max_chars:
            continue
        selected.append(f"[{src}] {c}")
        total_len += len(c)

    return VERIFIED_FACTS + "\n" + "\n".join(selected)

if btn and q:
    chunks, extraction_warnings = read_all_chunks()
    corpus = build_relevant_corpus(q, chunks, max_chars=10000, top_k=50)

    ans = ""
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"""أنت مساعد شؤون الطلبة في كليات الرؤية بالرياض.
مهمتك:
1. استخرج الإجابة بدقة من "النص المرجعي" المرفق فقط.
2. إذا سُئلت عن أنشطة أو فعاليات شهر معين (مثل أكتوبر، نوفمبر، إلخ)، اذكر جميع الأنشطة والفعاليات الخاصة بهذا الشهر المذكورة في النص المرجعي على شكل نقاط أو أسطر مستقلة.
3. لا تذكر أي مبالغ مالية أو ميزانيات إطلاقاً.
4. فقط إذا كان السؤال خروجاً تاماً عن شؤون الطلبة والأنشطة واللوائح (مثل أسئلة عامة أو دول)، رد بـ: "{OUT}".

النص المرجعي:
{corpus}

السؤال: {q}
الإجابة:"""

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        ans = completion.choices[0].message.content.strip()
    except Exception as e:
        ans = f"خطأ في الاتصال بـ Groq: {e}"

    if not ans or OUT in ans:
        ans = OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)

    if extraction_warnings:
        with st.expander("تفاصيل تقنية (لو احتجت تبلغني بمشكلة)"):
            for w in extraction_warnings:
                st.write(w)
