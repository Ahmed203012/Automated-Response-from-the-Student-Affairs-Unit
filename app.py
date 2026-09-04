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
    .stButton > button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# قراءة المفتاح من Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("أضف المفتاح في Secrets باسم GEMINI_API_KEY")
    st.stop()

@st.cache_data
def load_all_documents():
    text = ""
    for file in os.listdir('.'):
        if file.startswith('.'): continue
        if file.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    t = page.extract_text()
                    if t: text += t + "\n"
            except: pass
    return text.strip()

context = load_all_documents()

st.title("كليات الرؤية - Vision Colleges")
st.subheader("الإستفسار الآلي - وحدة شؤون الطلبة")

user_query = st.text_input("اسأل سؤالك هنا:")
submit_button = st.button("اضغط هنا للحصول على الإجابة")

if (submit_button or user_query) and user_query:
    if not context:
        st.error("لا يوجد مستندات.")
    else:
        with st.spinner("جاري البحث..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
أنت مساعد أكاديمي لشؤون الطلبة في كليات الرؤية.
أجب بناءً على النص المرفق فقط. إذا المعلومة غير موجودة قل: "عذراً، هذه المعلومة غير مذكورة في اللائحة الأكاديمية المرفقة".
يمنع استخدام معلومات خارجية.

النص:
{context}

سؤال الطالب:
{user_query}
"""
                response = model.generate_content(prompt)
                st.markdown("### الإجابة من واقع اللائحة:")
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
