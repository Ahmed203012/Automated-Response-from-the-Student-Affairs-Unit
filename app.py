import os
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
    line-height: 1.7;
    border: 1px solid #c3e6cb;
    font-size: 17px;
    white-space: pre-wrap;
}
.answer-box p, .answer-box li {
    margin-bottom: 4px !important;
}
.disclaimer-box {
    background-color: #fef9e7;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #f5d78e;
    margin-top: 20px;
    line-height: 1.7;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

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

def find_best_pdfs(query, max_files=5):
    pdfs = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
    if not pdfs:
        return []
    q = query.lower()
    scored = []
    for pdf in pdfs:
        name = pdf.lower()
        score = 0
        if "وفاة" in q or "وفاه" in q or "عذر" in
