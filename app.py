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
.answer-box p,.answer-box li { margin-bottom: 4px!important; }
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
OUT_MSG = "هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."

def find_best_pdfs(query, max_files=4):
    pdfs = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
    if not pdfs: return []
    q = query.lower()
    scored = []
    for pdf in pdfs:
        name = pdf.lower()
        score = 0
        if any(k in q for k in ["عذر","غياب","حرمان","وفاة","ولادة"]):
            if "عذر" in name or "اعذار" in name: score+=100
        if "تظلم" in q and "تظلم" in name: score+=100
        if "اختبار" in q and ("اختبار" in name or "قواعد" in name): score+=80
        if "مجلس" in q and "مجلس" in name: score+=80
        scored.append((score,pdf))
    scored.sort(key=lambda x:x[0], reverse=True)
    if scored and scored[0][0]==0:
        return pdfs[:max_files]
    return [p for s,p in scored[:max_files]]

if btn and user_query:
    best_pdfs = find_best_pdfs(user_query)
    try:
        from google import genai
        from google.genai import types
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)
        parts=[]
        for pdf_file in best_pdfs:
            try:
                with open(pdf_file,"rb") as f:
                    parts.append(types.Part.from_bytes(data=f.read(), mime_type="application/pdf"))
            except: pass

        prompt = f"""
أنت مساعد شؤون الطلبة. أمامك ملفات لوائح كلية الرؤية فقط.

السؤال: "{user_query}"

نفذ هذه الأوامر الثلاثة بح
