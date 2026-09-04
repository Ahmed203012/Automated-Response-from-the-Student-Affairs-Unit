import os
import streamlit as st
import pypdf
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered")

st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl!important; text-align: right!important; }
.stButton > button { width: 100%; background-color: #1E3A8A; color: white; font-weight: bold; border-radius: 8px; }
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
        if file.startswith('.'):
            continue
        if file.endswith('.pdf'):
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
st.title("Vision Colleges - كليات الرؤية")
st.subheader("الاستفسار الالي - وحدة شؤون الطلبة")

user_query = st.text_input("اسأل سؤالك هنا:")
submit_button = st.button("اضغط هنا للحصول على الاجابة")

if (submit_button or user_query) and user_query:
    with st.spinner("جاري البحث..."):
        try:
            base = "انت مساعد اكاديمي لشؤون الطلبة في كليات الرؤية. اجب بناء على النص المرفق فقط."
            full_prompt = base + "\n\nالنص:\n" + context + "\n\nسؤال الطالب:\n" + user_query
            
            # نجرب كل الموديلات المتاحة تلقائيا حتى ينجح واحد
            candidates = ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3.6-flash", "gemini-flash-latest", "gemini-2.0-flash"]
            last_err = ""
            for model_name in candidates:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    st.markdown("### الاجابة من واقع اللائحة:")
                    st.write(response.text)
                    break
                except Exception as e:
                    last_err = str(e)
                    continue
            else:
                st.error(last_err)
                
        except Exception as e:
            st.error(str(e))
