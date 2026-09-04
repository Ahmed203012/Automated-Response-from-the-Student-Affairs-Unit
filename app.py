import os
import streamlit as st
import pdfplumber
from google import genai
import re

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
    line-height: 2;
    border: 1px solid #c3e6cb;
    font-size: 17px;
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

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def normalize_ar(text):
    if not text:
        return ""
    text = text.replace("ـ", "").replace("ة", "ه").replace("ى", "ي")
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

@st.cache_data
def load_data():
    chunks = []
    for fname in os.listdir("."):
        if fname.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(fname) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            full_text += "\n" + t
                    words = full_text.split()
                    current = ""
                    for w in words:
                        current += w + " "
                        if len(current) > 700:
                            if len(current.strip()) > 50:
                                chunks.append(current.strip())
                            current = ""
                    if current.strip():
                        chunks.append(current.strip())
            except:
                pass
    return chunks

ALL_CHUNKS = load_data()

def get_context(q):
    q_norm = normalize_ar(q)
    q_words = [w for w in q_norm.split() if len(w) > 2]
    scored = []
    for ch in ALL_CHUNKS:
        ch_norm = normalize_ar(ch)
        score = 0
        for qw in q_words:
            if qw in ch_norm or qw.replace("ال", "") in ch_norm:
                score += 1
            if "عذر" in qw and "عذر" in ch_norm:
                score += 2
            if "وفاه" in qw and "وفاه" in ch_norm:
                score += 2
        if score > 0:
            scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return "\n".join(ALL_CHUNKS[:3])[:8000]
    top = [c for s,c in scored[:4]]
    result = "\n".join(top)
    return result[:8000]

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=130)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", width=130)

st.markdown("<h1 style='text-align:center;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"

if btn and user_query:
    context_text = get_context(user_query)
    ans = ""
    error_msg = ""
    try:
        prompt_text = "انت مساعد اكاديمي في كليات الرؤية. استخرج الاجابة بدقة من اللوائح التالية. اذا كان السؤال عن الاعذار الطلابية او عذر الوفاة فابحث عن المدة والضوابط. اجب بالعربية الواضحة في نقاط. اللوائح: " + context_text + " السؤال: " + user_query
        r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt_text)
        ans = r.text
    except Exception as e:
        error_msg = str(e)
        try:
            r2 = client.models.generate_content(model="gemini-1.5-flash", contents=prompt_text)
            ans = r2.text
        except Exception as e2:
            error_msg = str(e2)
            ans = ""
    if not ans or len(ans.strip()) < 10:
        if len(context_text.strip()) > 20:
            ans = "من واقع لوائح الكلية:\n\n" + context_text[:3000]
        else:
            ans = "عذرا، لم يتم العثور على اجابة واضحة. (خطأ: " + error_msg[:200] + ")"
    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    disc = "<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>"
    st.markdown(disc, unsafe_allow_html=True)
