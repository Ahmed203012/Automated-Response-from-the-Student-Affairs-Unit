import os
import streamlit as st
import pdfplumber
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], p, div, h1, h2, h3, input, textarea {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Tajawal', sans-serif !important;
}
div[data-testid="stImage"] { display: flex; justify-content: center; }
div[data-testid="stButton"] > button {
    background-color: #c5a880 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button:hover { background-color: #b8976a !important; }
.answer-box {
    background-color: #eaf7f0;
    padding: 20px;
    border-radius: 12px;
    line-height: 2.0;
    font-size: 17px;
    direction: rtl;
    text-align: right;
    border: 1px solid #c3e6cb;
    margin-top: 15px;
}
.disclaimer-box {
    background-color: #fef9e7;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #f5d78e;
    direction: rtl;
    text-align: right;
    line-height: 1.9;
    font-size: 15px;
    margin-top: 20px;
}
.disclaimer-box a { color: #0d47a1; font-weight: bold; word-break: break-all; }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

@st.cache_data
def load_data():
    chunks = []
    for fname in os.listdir("."):
        if fname.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(fname) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
                        if t and len(t.strip()) > 30:
                            chunks.append(t)
            except:
                pass
    return chunks

ALL_CHUNKS = load_data()

def get_context(q):
    q2 = q.replace("ة","ه")
    found = []
    for ch in ALL_CHUNKS:
        if any(w in ch for w in q2.split() if len(w) > 2):
            found.append(ch)
            if len(found) >= 2:
                break
    if not found:
        found = ALL_CHUNKS[:2]
    txt = ""
    for f in found:
        txt = txt + "\n" + f
    return txt[:6000]

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)

st.markdown("<h1 style='text-align:center;'>Vision Colleges - كليات الرؤية</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"

if btn and user_query:
    ctx =
