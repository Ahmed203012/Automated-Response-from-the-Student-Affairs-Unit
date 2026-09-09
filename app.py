import os, re, streamlit as st

# 1. تهيئة إعدادات الصفحة
st.set_page_config(page_title="كليات الرؤية", layout="centered")

# 2. إخفاء كافة عناصر منصة Streamlit والأزرار والشريط السفلي عبر CSS - نسخة محسنة
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

/* --- إخفاء كل أشرطة وأزرار Streamlit العلويّة والسفليّة وقوائم المطورين - نسخة نهائية 2024-2026 --- */
#MainMenu { visibility: hidden !important; display: none !important; }
header { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
div[data-testid="stHeader"] { display: none !important; visibility: hidden !important; height:0 !important;}
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
div[data-testid="InputInstructions"] { display: none !important; }
.stAppDeployButton { display: none !important; visibility: hidden !important;}

/* --- إخفاء زر Manage app وشريط Profile و Hosted with Streamlit و App Viewers --- */
[data-testid="manage-app-button"] { display: none !important; }
div[class*="stViewerBadge"] { display: none !important; visibility: hidden !important;}
iframe[title="streamlit_app"] { margin-bottom: 0px !important; }
.viewerBadge_container__1A52n { display: none !important; }
.viewerBadge_link__1S137 { display: none !important; }
div[class*="viewerBadge"] { display: none !important; }

/* إخفاءات إضافية جديدة لـ Streamlit Cloud */
div[data-testid="stBottomBlockContainer"] > div > div > a { display: none !important; }
button[kind="header"] { display: none !important; }
div._profileContainer { display: none !important; }
div[data-testid="stAppViewBlockContainer"] { padding-top: 1rem !important; }

/* إخفاء الأزرار العائمة وأزرار المشاريع والبروفايل */
button[title="View app source"] { display: none !important; }
.stAppFooter { display: none !important; }
div[data-testid="stActionButton"] { display: none !important; }
div[class*="stAppViewer"] { display: none !important; }
a[href*="streamlit.io"] { display: none !important; }
button[class*="viewerBadge"] { display: none !important; }

/* إخفاء قوي للشارات السفلية اليمنى */
section[data-testid="stSidebar"] + div div[class*="viewer"] { display:none !important; }
</style>
""", unsafe_allow_html=True)

# 3. شعار واجهة التطبيق
c1, c2, c3 = st.columns([1, 1.2, 1])
with c2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)

st.markdown("<h1 style='text-align:center!important; font-size:32px!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center!important; font-size:26px!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
# تم التغيير الوحيد المطلوب: استفساركم -> استفساراتكم
st.markdown("<p style='text-align:center!important; font-size:18px!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية والأنشطة الطلابية.</p>", unsafe_allow_html=True)

q = st.text_input(" ", placeholder="اكتب سؤالك هنا...")
btn = st.button("اضغط هنا للحصول على الإجابة")

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
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)  # إزالة التشكيل والحركات
    text = re.sub(r"ـ", "", text)          # إزالة التطويل
    return text.strip().lower()

# --- قائمة الكلمات المتوقفة ---
RAW_STOPWORDS = {
    "من", "الى", "إلى", "عن", "على", "في", "هل", "ما", "ماذا", "و", "او", "أو",
    "هو", "هي", "هم", "لا", "نعم", "كيف", "متى", "اين", "أين", "ال", "التي",
    "الذي", "كم", "لماذا", "مع", "هذا", "هذه", "ذلك", "تلك", "كان", "يكون",
}
STOPWORDS = {normalize_arabic(w) for w in RAW_STOPWORDS}

# --- الحقائق المعتمدة، التقويم الأكاديمي والأنشطة الطلابية ---
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

--- أنشطة الفصول الأخرى والمستمرة ---
- رحلات ترفيهية وثقافية
- مسابقات القرآن الكريم والسنة النبوية
- الأنشطة واللقاءات الدورية لأندية الكلية الطلابية

=== التقويم الأكاديمي المعتمد لكليات الرؤية (الفصول الدراسية الثلاثة) ===

--- الفصل الدراسي الأول ---
- بداية التهيئة والتسجيل للفصل الدراسي الأول: الأحد 1448/03/03 هـ (الموافق 16/08/2026 م)
"""

EXCUSE_SOURCE_HINTS = ["عذر", "اعذار", "غياب"]
CALENDAR_SOURCE_HINTS = ["تقويم", "اجازه", "عطله", "جدول"]
ACTIVITY_SOURCE_HINTS = ["نشاط", "فعاليه", "انشطه", "فعاليات", "شهر", "سبتمبر", "اكتوبر", "نوفمبر", "ديسمبر"]
HOLIDAY_WORDS = {"اجازه", "اجازات", "عطله", "عطل", "عطلة"}
EXCUSE_WORDS = {"عذر", "اعذار", "غياب", "تبرير"}
ACTIVITY_WORDS = {"نشاط", "انشطه", "فعاليه", "فعاليات", "سبتمبر", "اكتوبر", "نوفمبر", "ديسمبر", "يناير", "فبراير", "مارس", "ابريل", "مايو", "يونيو", "يوليو", "اغسطس"}


# --- تحسين السرعة: تخزين قراءة الملفات في الذاكرة مرة واحدة فقط ---
@st.cache_data(show_spinner=False)
def read_all_chunks_cached():
    chunks, warnings = [], []
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    for f in files:
        low = f.lower()
        if low.endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(f) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        try:
                            text = page.extract_text() or ""
                            heading = None
                            words = getattr(page, "objects", {}).get("text", [])
                            if words:
                                sizes = [w.get("size", 0) for w in words]
                                if sizes:
                                    max_size = max(sizes)
                                    big = [w for w in words if w.get("size", 0) >= max_size - 0.5]
                                    if big:
                                        heading = " ".join(w.get("text","") for w in big).strip()
                            for para in re.split(r"\n\s*\n", text):
                                para = para.strip()
                                if len(para) <= 5:
                                    continue
                                row_text = para
                                if heading and len(heading) > 3 and heading not in para and len(heading.split()) <= 10:
                                    if len(para) < 200:
                                        row_text = f"{heading} — {para}"
                                chunks.append((f, row_text))
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
        chunks, extraction_warnings = read_all_chunks_cached()
        corpus = build_relevant_corpus(q, chunks, max_chars=6000, top_k=25)

        ans = ""
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"""أنت مساعد شؤون الطلبة في كليات الرؤية بالرياض.
مهمتك:
1. استخرج الإجابة بدقة من "النص المرجعي" المرفق فقط.
2. إذا سُئلت عن أنشطة أو فعاليات شهر معين (مثل أكتوبر، نوفمبر، إلخ)، اذكر جميع الأنشطة والفعاليات الخاصة بهذا الشهر المذكورة في النص المرجعي على شكل نقاط أو أسطر مستقلة.
3. تجنب الحكم على الكلمات بناءً على وجود الهمزة أو عدمها (مثلاً: أكتبر/اكتوبر، أنشطة/انشطة كلها تعني نفس الشيء).
4. لا تذكر أي مبالغ مالية أو ميزانيات إطلاقاً.
5. فقط إذا كان السؤال خروجاً تاماً عن شؤون الطلبة والأنشطة واللوائح (مثل أسئلة عامة أو دول)، رد بـ: "{OUT}".

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

    if extraction_warnings:
        with st.expander("تفاصيل تقنية (لو احتجت تبلغني بمشكلة)"):
            for w in extraction_warnings:
                st.write(w)
