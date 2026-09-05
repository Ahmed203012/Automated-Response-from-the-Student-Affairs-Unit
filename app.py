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


def normalize_arabic(text: str) -> str:
    """Light normalization so 'العميد' and 'عميد' etc. match better."""
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)  # strip tashkeel
    return text


def read_all_chunks():
    """Read every supported file and return a list of (source_file, chunk_text)."""
    chunks = []
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
                import fitz
                doc = fitz.open(f)
                for page in doc:
                    text = page.get_text()
                    for para in re.split(r"\n\s*\n", text):
                        para = para.strip()
                        if len(para) > 5:
                            chunks.append((f, para))
            except Exception:
                pass
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
    return chunks


def score_chunk(question_words, chunk_text):
    norm_chunk = normalize_arabic(chunk_text)
    score = 0
    for w in question_words:
        if w in norm_chunk:
            score += 1
    return score


def build_relevant_corpus(question, chunks, max_chars=6000, top_k=25):
    """Pick the chunks most relevant to the question instead of blindly
    taking the first N characters of the whole corpus."""
    norm_q = normalize_arabic(question)
    q_words = [w for w in re.split(r"\s+", norm_q) if w and w not in STOPWORDS and len(w) > 1]

    if not q_words or not chunks:
        # fallback: just take from the start if we truly can't score anything
        joined = "\n".join(c for _, c in chunks)
        return joined[:max_chars]

    scored = [(score_chunk(q_words, c), src, c) for src, c in chunks]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # no keyword overlap found anywhere — fall back to a broader slice
        joined = "\n".join(c for _, c in chunks)
        return joined[:max_chars]

    selected = []
    total_len = 0
    for score, src, c in scored[:top_k]:
        if total_len + len(c) > max_chars:
            continue
        selected.append(f"[{src}] {c}")
        total_len += len(c)

    return "\n".join(selected)


if btn and q:
    chunks = read_all_chunks()
    corpus = build_relevant_corpus(q, chunks, max_chars=6000, top_k=25)

    ans = ""
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = f"""أنت مساعد شؤون الطلبة في كليات الرؤية بالرياض.
أجب باختصار شديد سطر أو سطرين فقط ومن النص المرجعي فقط.
- لا تخلط: عذر الوفاة = 5 أيام + تقديم خلال أسبوع، عذر الولادة = أسبوع واحد + تقديم خلال 10 أيام، العذر الطبي/الحوادث = 3 أيام عمل.
- إذا سُئلت عن عميد أو وكيل أو ايميل ابحث عن الاسم بالضبط.
- إذا لم تجد قل: {OUT}

النص المرجعي:
{corpus}

السؤال: {q}
الإجابة المختصرة:"""

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        ans = completion.choices[0].message.content.strip()
    except Exception as e:
        ans = f"خطأ في الاتصال بـ Groq: {e}"

    if not ans:
        ans = OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
