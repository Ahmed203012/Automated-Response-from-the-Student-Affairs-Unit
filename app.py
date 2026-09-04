import os
import streamlit as st
import pdfplumber
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered")

css_code = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], p, div, h1, h2, h3 {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Tajawal', sans-serif !important;
}
div[data-testid="stImage"] { display: flex; justify-content: center; }
div[data-testid="stButton"] > button {
    background-color: #c5a880 !important;
    color: white !important;
    border-radius: 12px !important;
    width: 100% !important;
    font-weight: bold !important;
}
.answer-box {
    background-color: #eaf7f0;
    padding: 20px;
    border-radius: 12px;
    line-height: 2;
    border: 1px solid #c3e6cb;
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

@st.cache_data
def load_data():
    chunks = []
    for fname in os.listdir("."):
        if fname.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(fname) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
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
        words = q2.split()
        for w in words:
            if len(w) > 2 and w in ch:
                found.append(ch)
                break
        if len(found) >= 2:
            break
    if not found:
        found = ALL_CHUNKS[:2]
    result = ""
    for f in found:
        result = result + "\n" + f
    return result[:6000]

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
    context_text = get_context(user_query)
    ans = ""
    try:
        prompt_text = "اجب باختصار ووضوح من اللوائح التالية فقط. اللوائح: " + context_text + " السؤال: " + user_query
        r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt_text)
        ans = r.text
    except:
        ans = context_text[:2000]
    if not ans:
        ans = "عذرا، هذه المعلومة غير متوفرة في اللوائح."
    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    disc = "<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>"
    st.markdown(disc, unsafe_allow_html=True)
