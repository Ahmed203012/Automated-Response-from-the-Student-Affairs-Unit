import os
import streamlit as st
import pdfplumber
import pypdf
from google import genai

st.set_page_config(page_title="كليات الرؤية", layout="centered")

# --- تصميم RTL + هوية الكلية الذهبية ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [class*="css"] { 
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl !important; 
    text-align: right !important; 
}
h1, h2, h3, h4, p, div, input, label, span {
    text-align: right !important;
    direction: rtl !important;
}
.stTextInput > div > div > input {
    direction: rtl !important;
    text-align: right !important;
}
.stButton > button { 
    width: 100%; 
    background-color: #C9A86A !important;
    color: #1A1A1A !important;
    font-weight: bold !important; 
    border-radius: 10px !important;
    border: none !important;
    padding: 12px !important;
    font-size: 16px !important;
}
.stButton > button:hover {
    background-color: #B8965A !important;
    color: white !important;
}
.answer-box {
    background-color: #FFFBF0;
    border-right: 5px solid #C9A86A;
    padding: 15px;
    border-radius: 8px;
    margin-top: 15px;
    direction: rtl !important;
    text-align: right !important;
}
.disclaimer-box {
    background-color: #FFF3CD;
    border: 1px solid #C9A86A;
    padding: 12px;
    border-radius: 8px;
    margin-top: 20px;
    font-size: 13px;
    color: #856404;
    direction: rtl !important;
    text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except:
    st.error("اضف GEMINI_API_KEY في Secrets")
    st.stop()

@st.cache_data
def load_all_documents():
    txt = ""
    for file in os.listdir('.'):
        if not file.endswith('.pdf'):
            continue
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        txt += f"\n--- من ملف {file} ---\n" + t + "\n"
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table:
                                if row:
                                    clean_row = [str(c).strip() for c in row if c and str(c).strip()]
                                    if clean_row:
                                        txt += " | ".join(clean_row) + "\n"
        except:
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        txt += t + "\n"
            except:
                pass
    return txt.strip()

context = load_all_documents()

# --- العناوين بالترتيب الجديد ---
st.markdown("<h1 style='text-align: right; color: #1E3A8A; margin-bottom:0;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: right; color: #555; margin-top:5px;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)

user_query = st.text_input("اسأل سؤالك هنا:", placeholder="مثال: من هو عميد الكلية؟")
submit_button = st.button("اضغط هنا للحصول على الإجابة")

# --- التنويه: غير هذا النص بالنص اللي في الصورة اللي هترسلها ---
DISCLAIMER_TEXT = """
تنويه: هذه الإجابة إرشادية من واقع لوائح الكلية المعتمدة، وللتأكيد النهائي أو الحالات الخاصة يرجى مراجعة وحدة شؤون الطلبة.
"""

if (submit_button or user_query) and user_query:
    with st.spinner("جاري البحث في لوائح الكلية..."):
        try:
            base = "انت مساعد اكاديمي لشؤون الطلبة في كليات الرؤية. اجب بناء على النص المرفق فقط. اذا كان السؤال عن اسماء من مجلس الكلية استخرج الاسم كاملا من الجدول."
            full_prompt = base + "\n\nالنص:\n" + context + "\n\nسؤال الطالب:\n" + user_query
            
            candidates = ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3.6-flash", "gemini-flash-latest", "gemini-2.0-flash"]
            last_err = ""
            for model_name in candidates:
                try:
                    response = client.models.generate_content(model=model_name, contents=full_prompt)
                    st.markdown(f"<div class='answer-box'><h4 style='color:#1E3A8A; text-align:right;'>الإجابة من واقع اللائحة:</h4><div style='text-align:right; direction:rtl;'>{response.text}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='disclaimer-box'>⚠️ {DISCLAIMER_TEXT}</div>", unsafe_allow_html=True)
                    break
                except Exception as e:
                    last_err = str(e)
                    continue
            else:
                st.error(last_err)
        except Exception as e:
            st.error(str(e))
