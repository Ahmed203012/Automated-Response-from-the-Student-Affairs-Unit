import os, re, streamlit as st

# 1. تهيئة إعدادات الصفحة
st.set_page_config(page_title="كليات الرؤية", layout="centered")

# 2. إخفاء كافة عناصر منصة Streamlit وتنسيق الواجهة عبر CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');

/* التنسيق العام والاتجاه من اليمين للشمال */
html, body, [data-testid="stAppViewContainer"] { direction: rtl!important; text-align: right!important; }
* { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }

/* تنسيق زر البحث والأجوبة */
div[data-testid="stButton"] > button { 
    background:#c5a880!important; 
    color:white!important; 
    border-radius:14px!important; 
    width:100%!important; 
    font-weight:bold!important; 
    font-size:17px!important; 
    padding:12px!important; 
}
.answer-box { background:#eaf7f0; padding:22px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; line-height:2; }
.disclaimer-box { background:#fef9e7; padding:16px; border-radius:12px; border:1px solid #f5d78e; margin-top:18px; font-size:14px; }

/* --- إخفاء كل أشرطة Streamlit الهيدر والفوتر والفلوانج بار عائم بالكامل --- */
#MainMenu, header, footer { visibility: hidden !important; display: none !important; }
div[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] { display: none !important; }
div[data-testid="InputInstructions"], .stAppDeployButton, [data-testid="manage-app-button"] { display: none !important; }

/* إخفاء الأزرار العائمة العلوية والسفلية */
div[data-testid="stAppToolbar"] { display: none !important; visibility: hidden !important; }
div[data-testid="stActionButton"] { display: none !important; visibility: hidden !important; }
div[data-testid="stSidebarCollapseButton"] { display: none !important; }
.stAppFooter, footer { display: none !important; }

/* إخفاء شارة Streamlit والشعارات العائمة للجوال */
div[class*="stViewerBadge"], .viewerBadge_container__1A52n, .viewerBadge_link__1S137, div[class*="viewerBadge"] { display: none !important; }
button[title="View app source"], a[href*="streamlit.io"], button[class*="viewerBadge"] { display: none !important; }

/* إلغاء الحواف والهوامش السفلية */
footer { position: fixed; bottom: -100px; }
.stApp { margin-bottom: 0px !important; padding-bottom: 0px !important; }
</style>
""", unsafe_allow_html=True)

# 3. شعار واجهة التطبيق
c1, c2, c3 = st.columns([1, 1.2, 1])
with c2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)

# العناوين والنصوص المطابقة تماماً لنسخة Render
st.markdown("<h1 style='text-align:center!important; font-size:32px!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center!important; font-size:22px!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center!important; font-size:18px!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

# حقل المدخلات والتفاعل
q = st.text_input(" ", placeholder="اكتب سؤالك هنا...")

# الزر بحسب تصميم نسخة Render
col1, col2 = st.columns([1, 2])
with col1:
    btn = st.button("للرد على استفسارك اضغط هنا")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"
OUT = "هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH = (
    "تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، "
    "وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:"
    f"<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"
)

# --- دالة توحيد وتطبيع النص العربي لتجاهل الهمزات والألفات والتاء المربوطة والحركات ---
def normalize_arabic(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)
    text = re.sub(r"ـ", "", text)
    return text.strip().lower()

RAW_STOPWORDS = {
    "من", "الى", "إلى", "عن", "على", "في", "هل", "ما", "ماذا", "و", "او", "أو",
    "هو", "هي", "هم", "لا", "نعم", "كيف", "متى", "اين", "أين", "ال", "التي",
    "الذي", "كم", "لماذا", "مع", "هذا", "هذه", "ذلك", "تلك", "كان", "يكون",
}
STOPWORDS = {normalize_arabic(w) for w in RAW_STOPWORDS}

VERIFIED_FACTS = """
عميد الكلية: الأستاذ الدكتور عبدالله محمد الدهمش

مفهوم الإرشاد الأكاديمي: خدمة أكاديمية تهدف إلى التعرف على المشكلات التي تعوق قدرة الطالب على التحصيل العلمي والتفاعل مع متطلبات الحياة الجامعية، وتعمل على تقديم المساعدة والدعم عن طريق زيادة وعي الطلبة بمسؤولياتهم.

=== خطة الأنشطة والفعاليات الطلابية المعتمدة (وحدة شؤون الطلبة) ===
--- أنشطة شهر سبتمبر (الشهر الأول) ---
- استقبال الطلاب والطلبة الجدد والتهيئة الأكاديمية
- اليوم الوطني السعودي (فعاليات ومعارض واحتفالات الكلية باليوم الوطني)
- ورش عمل تعريفية باللوائح والحقوق والواجبات الطلابية

--- أنشطة شهر أكتوبر (الشهر الثاني) ---
- حملات التوعية الصحية والطبية (اليوم العالمي لسرطان الثدي - الوردي)
- المعرض الطلابي للابتكار والبحوث الطلابية
- دوريات الألعاب الرياضية (كرة القدم، الشطرنج، كرة الطاولة)
- حملات التبرع بالدم بالتعاون مع الجهات الصحية

--- أنشطة شهر نوفمبر (الشهر الثالث) ---
- اليوم العالمي لطب الأسنان والتمريض (معارض وتوعية ميدانية)
- زيارات ميدانية علمية ومجتمعية
- المسابقات الثقافية واللقاءات الحوارية الطلابية
- ورش تطوير المهارات والمهن الصحية

--- أنشطة شهر ديسمبر (الشهر الرابع) ---
- المعرض الفني والمهارات الإبداعية والطبخ والصحة
- حملات التوعية المجتمعية والخدمات التطوعية
- التكريم والاحتفاء بالطلاب المتفوقين في الأنشطة الطلابية

--- أنشطة شهر يناير ---
- ورش الاستعداد للاختبارات وتحفيز الطلاب
- لقاءات الإرشاد الأكاديمي للطلبة المتعثرين والمتفوقين

--- أنشطة شهر فبراير ---
- فعاليات يوم التأسيس السعودي والمعارض التراثية والثقافية بالكلية
- الأنشطة الرياضية والبطولات التنافسية الداخلية

--- أنشطة شهر مارس ---
- فعاليات اليوم العالمي لطب الأسنان واليوم العالمي للصحة
- الحملات التوعوية والمبادرات التطوعية الخارجية والخدمات المجتمعية
- الدورات والورش التدريبية لتعزيز المهارات الطلابية

--- أنشطة شهر أبريل ---
- يوم البحث العلمي الطلابي ومعرض المبتكرات
- المسابقات الثقافية والدينية واللقاءات الطلابية المفتوحة
- التوعية بالصحة النفسية وبناء القدرات الشخصية

--- أنشطة شهر مايو ---
- المعارض الفنية والختامية للأنشطة الطلابية
- حفل تكريم الأندية الطلابية والمتطوعين والطلاب المتميزين

=== التقويم الأكاديمي المعتمد لكليات الرؤية ===
--- الفصل الدراسي الأول ---
- بداية التهيئة والتسجيل للفصل الدراسي الأول: الأحد 1448/03/03 هـ (الموافق 16/08/2026 م)
- بداية الدراسة للفصل الدراسي الأول: الأحد 1448/03/10 هـ (الموافق 23/08/2026 م)
- بداية فترة الحذف والإضافة للفصل الدراسي الأول: الأحد 1448/03/10 هـ (الموافق 23/08/2026 م)
- إجازة اليوم الوطني: الأربعاء والخميس 1448/04/12 - 1448/04/13 هـ (الموافق 23/09/2026 - 24/09/2026 م)
- بداية اختبارات منتصف الفصل الدراسي الأول: الخميس 1448/04/27 هـ (الموافق 08/10/2026 م)
- بداية الاختبارات النهائية للفصل الدراسي الأول: الأحد 1448/07/11 هـ (الموافق 20/12/2026 م)

--- الفصل الدراسي الثاني ---
- بداية التهيئة والتسجيل للفصل الدراسي الثاني: الأحد 1448/08/02 هـ (الموافق 10/01/2027 م)
- بداية الدراسة للفصل الدراسي الثاني: الأحد 1448/08/09 هـ (الموافق 17/01/2027 م)
- إجازة يوم التأسيس: الأحد والاثنين 1448/09/14 - 1448/09/15 هـ (الموافق 21/02/2027 - 22/02/2027 م)
- بداية إجازة عيد الفطر: الثلاثاء 1448/09/16 هـ (الموافق 23/02/2027 م)
- بداية الاختبارات النهائية للفصل الدراسي الثاني: الأحد 1449/01/01 هـ (الموافق 06/06/2027 م)
"""

HOLIDAY_WORDS = {normalize_arabic(w) for w in ["اجازه", "اجازات", "عطله", "عطلات", "عطل"]}
EXCUSE_WORDS = {normalize_arabic(w) for w in ["عذر", "اعذار", "وفاه", "ولاده", "مرضيه", "مرض", "مريض"]}
ACTIVITY_WORDS = {normalize_arabic(w) for w in [
    "نشاط", "نشاطات", "انشطه", "أنشطة", "فعاليه", "فعاليات", "خطة", "خطه", 
    "شهر", "أكتوبر", "اكتوبر", "سبتمبر", "نوفمبر", "ديسمبر", "يناير", "فبراير", 
    "مارس", "أبريل", "ابريل", "مايو", "أغسطس", "اغسطس"
]}

EXCUSE_SOURCE_HINTS = ("excuse", normalize_arabic("عذر"))
CALENDAR_SOURCE_HINTS = ("calendar", normalize_arabic("تقويم"))
ACTIVITY_SOURCE_HINTS = ("activity", normalize_arabic("أنشطة"), normalize_arabic("الأنشطة"), normalize_arabic("انشطة"), normalize_arabic("الأنشطه"))

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

@st.cache_data(ttl=3600)
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
                    warnings.append(f"{f}: فشل الاحتياطي أيضاً — {fallback_err}")
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

    src_norm = normalize_arabic(src)
    src_low = src.lower()
    
    if avoid_excuse and any(h in src_low or h in src_norm for h in EXCUSE_SOURCE_HINTS):
        score -= 5
    if prefer_calendar and any(h in src_low or h in src_norm for h in CALENDAR_SOURCE_HINTS):
        score += 3
    if prefer_activity and any(h in src_low or h in src_norm for h in ACTIVITY_SOURCE_HINTS):
        score += 8

    return score

def build_relevant_corpus(question, chunks, max_chars=6000, top_k=25):
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
    
    if prefer_activity:
        for idx, (sc, src, c) in enumerate(scored):
            src_norm = normalize_arabic(src)
            if any(h in src.lower() or h in src_norm for h in ACTIVITY_SOURCE_HINTS):
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
    with st.spinner("جاري جلب الإجابة..."):
        chunks, extraction_warnings = read_all_chunks()
        corpus = build_relevant_corpus(q, chunks, max_chars=6000, top_k=25)

        ans = ""
        try:
            from groq import Groq
            
            # جلب المفتاح سواء تم وضعه في os.environ (Render) أو st.secrets (Streamlit Cloud)
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                try:
                    api_key = st.secrets["GROQ_API_KEY"]
                except Exception:
                    api_key = None

            if not api_key:
                ans = "خطأ: لم يتم العثور على مفتاح GROQ_API_KEY. يُرجى إضافته في Environment Variables في Render."
            else:
                client = Groq(api_key=api_key)
                prompt = f"""أنت مساعد شؤون الطلبة في كليات الرؤية بالرياض.
مهمتك:
1. استخرج الإجابة بدقة من "النص المرجعي" المرفق فقط.
2. إذا سُئلت عن أنشطة أو فعاليات شهر معين، اذكر الأنشطة المذكورة في النص المرجعي على شكل نقاط بوضوح.
3. تجنب الحكم على الكلمات بناءً على وجود الهمزة أو عدمها (أبريل/ابريل، مارس، أكتوبر كلها مقبولة بنفس المعنى).
4. لا تذكر أي مبالغ مالية أو ميزانيات.
5. إذا لم توجد أي معلومة إطلاقاً تخص السؤال، رد بـ: "{OUT}".

النص المرجعي:
{corpus}

السؤال: {q}
الإجابة:"""

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
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
