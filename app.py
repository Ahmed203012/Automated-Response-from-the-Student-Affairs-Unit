import os
import streamlit as st
import pypdf
from groq import Groq

st.set_page_config(page_title="Vision Colleges", layout="centered")

st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl!important; text-align: right!important; }
.stButton > button { width: 100%; background-color: #1E3A8A; color: white; font-weight: bold; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("اضف GROQ_API_KEY في Secrets")
    st.stop()

@st.cache_data
def load_all_documents():
    txt = ""
    for file in os.listdir('.'):
        if file.startswith('.'): continue
        if file.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    t = page.extract_text()
                    if t: txt += t + "\n"
            except: pass
    return txt.strip()

context = load_all_documents()
st.title("كليات الرؤية - Vision Colleges")
st.subheader("الإستفسار الآلي - وحدة شؤون الطلبة")

user_query = st.text_input("اسأل سؤالك هنا:")
submit_button = st.button("اضغط هنا للحصول على الإجابة")

if (submit_button or user_query) and user_query:
    with st.spinner("جاري البحث..."):
        try:
            base = "أنت مساعد أكاديمي لشؤون الطلبة في كليات الرؤية. أجب بناء على النص المرفق فقط."
            full_prompt = base + "\n\nالنص:\n" + context + "\n\nسؤال الطالب:\n" + user_query

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.2
            )
            st.markdown("### الإجابة من واقع اللائحة:")
            st.write(completion.choices[0].message.content)
        except Exception as e:
            st.error(str(e))
