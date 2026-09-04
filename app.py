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

def find_best_pdfs(query, max_files=2):
    pdfs = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
    if not pdfs:
        return []
    q = query.lower()
    scored = []
    for pdf in pdfs:
        score = 0
        name = pdf.lower()
        if "عذر" in q or "غياب" in q:
            if "عذر" in name or "لائحة" in name or "دليل" in name:
                score += 10
        scored.append((score, pdf))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored[0][0] == 0:
        return pdfs[:max_files]
    return [p for s,p in scored[:max_files]]

if btn and user_query:
    best_pdfs = find_best_pdfs(user_query)
    ans = ""
    last_error = ""
    models_to_try = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash-8b"]
    try:
        from google import genai
        from google.genai import types
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)
        parts = []
        for pdf_file in best_pdfs:
            try:
                with open(pdf_file, "rb") as f:
                    pdf_bytes = f.read()
                parts.append(types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))
            except:
                pass
        prompt = f"انت مساعد اكاديمي في كليات الرؤية بالرياض. اقرأ ملفات اللوائح المرفقة واجب على هذا السؤال بالعربية الفصحى الواضحة في نقاط مرتبة: {user_query}. اذا كان السؤال عن عذر الوفاة اذكر المدة وطريقة التقديم والاوراق المطلوبة."
        parts.append(types.Part.from_text(text=prompt))
        for model_name in models_to_try:
            try:
                r = client.models.generate_content(
                    model=model_name,
                    contents=[types.Content(role="user", parts=parts)]
                )
                if r and r.text and len(r.text.strip()) > 10:
                    ans = r.text
                    break
            except Exception as e:
                last_error = str(e)
                continue
    except Exception as e:
        last_error = str(e)
        ans = ""
    if not ans:
        ans = f"عذرا، حدث خطأ مؤقت في قراءة اللوائح. (التفاصيل: {last_error[:400]}). يرجى المحاولة مرة اخرى."
    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    disc = "<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>"
    st.markdown(disc, unsafe_allow_html=True)
