import os
import streamlit as st
import pdfplumber
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered", page_icon=":mortar_board:")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
h1, h2, h3, h4, p, div, input, label, span { text-align: right!important; direction: rtl!important; }
.stTextInput > div > div > input { direction: rtl!important; text-align: right!important; }
.stButton > button { width: 100%; background-color: #C9A86A!important; color: #000!important; font-weight: bold!important; border-radius: 10px!important; border: none!important; padding: 12px!important; font-size: 17px!important; }
.answer-box { background-color: #FFF9E6!important; border-right: 6px solid #C9A86A; padding: 18px; border-radius: 10px; margin-top: 18px; direction: rtl!important; text-align: right!important; line-height: 1.9; }
.disclaimer-box { background-color: #FFF8D6; border: 1px solid #C9A86A; padding: 14px; border-radius: 8px; margin-top: 18px; font-size: 13.5px; color: #000; direction: rtl!important; text-align: right!important; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except:
    st.error("Add GEMINI_API_KEY in Secrets")
    st.stop()

@st.cache_data(show_spinner=False)
def load_text():
    full = ""
    chunks = []
    for file in os.listdir('.'):
        if not file.lower().endswith('.pdf'):
            continue
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    if len(t.strip()) > 20:
                        full += "\n" + t + "\n"
                        chunks.append(t)
        except:
            pass
    return full, chunks

full_text, all_chunks = load_text()

def get_context
