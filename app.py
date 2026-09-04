import os
import streamlit as st
import google.generativeai as genai
import pypdf

st.set_page_config(page_title="كليات الرؤية - Vision Colleges", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"], div, p, span, input, button, label {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTextInput > div > div > input {
        text-align: right !important;
        direction: rtl !important;
    }
    .stButton > button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    .disclaimer-box {
        background-color: #F3F4F6;
        border-right: 4px solid #1E3A8A;
        padding: 12px 15px;
        border-radius: 6px;
        margin-top: 20px;
        font-size: 14px;
        color: #374151;
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- قراءة المفتاح من Secrets ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("خطأ: لم يتم العثور على GEMINI_API_KEY في Secrets. أضف المفتاح في إعدادات Streamlit Cloud.")
    st.stop()

@st.cache_data
def load_all_documents():
    extracted_text = ""
    for file in os.listdir('.'):
        if file.startswith('.'):
            continue
        if file.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            except Exception:
                pass
        elif file.endswith('.txt') and file not in ['app.py', 'requirements.txt']:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    extracted_text += f.read() + "\n"
            except Exception:
                pass
    return extracted_text.strip()

context = load_all_documents()

if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", width=180)

st.title("كليات الرؤية - Vision Colleges")
st.subheader("الإستفسار الآلي - وحدة شؤون الطلبة")
st.write("أهلاً بك، يمكنك طرح أي سؤال متعلق باللوائح والتعليمات الأكاديمية.")

user_query = st.text_input("اسأل سؤالك هنا:")
submit_button = st.button("اضغط هنا للحصول على الإجابة")

if (submit_button or user_query) and user_query:
    if not context:
        st.error("عذراً، لم يتم العثور على أي لوائح أو مستندات مرفوعة للنظام.")
    else:
        with st.spinner("جاري البحث داخل اللائحة المرفقة..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                strict_prompt = f"""
أنت مساعد أكاديمي لشؤون الطلبة في كليات الرؤية.
تنبيه صارم جداً: أجب
