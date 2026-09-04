import os
import re
import streamlit as st

st.set_page_config(page_title="Vision Colleges", layout="centered")

css_code = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], p, div, h1, h2, h3 {
    direction: rtl!important;
    text-align: right!important;
    font-family: 'Tajawal', sans-serif!important;
}
div[data-testid="stImage"] { display: flex; justify-content: center; }
div[data-testid="stButton"] > button {
    background-color: #c5a880!important;
    color: white!important;
    border-radius: 12px!important;
    width: 100%!important;
    font-weight: bold!important;
}
.answer-box {
    background-color: #eaf7f0;
    padding: 20px;
    border-radius: 12px;
    line-height: 2.1;
    border: 1px solid #c3e6cb;
    font-size: 17px;
    white-space: pre-wrap;
}
.disclaimer-box {
    background-color: #fef9e7;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #f5d78e;
    margin-top: 20px;
    line-height: 1.9;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

def fix_arabic_text(text):
    if not text:
        return text
    text = text.replace("ـ", "")
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except:
        return text

def normalize_for_search(text):
    if not text:
        return ""
    text = text.replace("ـ", "").replace("ة", "ه").replace("ى", "ي")
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

@st.cache_data
def load_data():
    chunks = []
    try:
        import fitz
        for fname in os.listdir("."):
            if fname.lower().endswith(".pdf"):
                try:
                    doc = fitz.open(fname)
                    full = ""
                    for page in doc:
                        t = page.get_text("text")
                        if t:
                            full += "\n" + t
                    words = full.split()
                    cur = ""
                    for w in words:
                        cur += w + " "
                        if len(cur) > 800:
                            if len(cur.strip()) > 40:
                                chunks.append(cur.strip())
                            cur = ""
                    if cur.strip():
                        chunks.append(cur.strip())
                except:
                    pass
        if chunks:
            return chunks
    except:
        pass
    try:
        import pdfplumber
        for fname in os.listdir("."):
            if fname.lower().endswith(".pdf"):
                try:
                    with pdfplumber.open(fname) as pdf:
                        full = ""
                        for p in pdf.pages:
                            t = p.extract_text()
                            if t:
                                full += "\n" + t
                        words = full.split()
                        cur = ""
                        for w in words:
                            cur += w + " "
                            if len(cur) > 800:
                                if len(cur.strip()) > 40:
                                    chunks.append(cur.strip())
                                cur = ""
                        if cur.strip():
                            chunks.append(cur.strip())
                except:
                    pass
    except:
        pass
    return chunks

ALL_CHUNKS = load_data()

def get_context(q):
    q_norm = normalize_for_search(q)
    q_words = [w for w in q_norm.split() if len(w) > 2]
    scored = []
    for ch in ALL_CHUNKS:
        ch_norm = normalize_for_search(ch)
        score = 0
        for qw in q_words:
            base = qw.replace("ال", "")
            if qw in ch_norm or base in ch_norm:
                score += 1
        if "عذر" in q_norm and "عذر" in ch_norm:
            score += 5
        if "وفاه" in q_norm and "وفاه" in ch_norm:
            score += 5
        if "غياب" in q_norm and "غياب" in ch_norm:
            score += 3
        if score > 0:
            scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return "\n".join(ALL_CHUNKS[:4])[:8000]
    top = [c for s,c in scored[:4]]
    return "\n".join(top)[:8000]

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", width=120)

st.markdown("<h1 style='text-align:center;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"

if btn and user_query:
    raw_context = get_context(user_query)
    fixed_context = fix_arabic_text(raw_context)
    ans = ""
    try:
        from google import genai
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)
        prompt_text = "انت مساعد في كليات الرؤية. اجب من اللوائح التالية باختصار واضح بالعربية الفصحى في نقاط مرتبة. اذا سئل عن المدة لعذر الوفاة اذكر المدة المسموحة. اللوائح: " + fixed_context + " السؤال: " + user_query
        r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt_text)
        ans = r.text
        ans = fix_arabic_text(ans)
    except Exception as e:
        ans = fixed_context[:3500]
    if not ans or len(ans.strip()) < 10:
        ans = fixed_context[:3500]
    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    disc = "<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>"
    st.markdown(disc, unsafe_allow_html=True)
