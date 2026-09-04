import os
import streamlit as st
import pdfplumber
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered")

st.markdown("<style> @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap'); html, body { font-family: Tajawal, sans-serif; direction: rtl; text-align: right; } .stButton>button { width: 100%; background-color: #C9A86A; color: #000; font-weight: bold; border-radius: 10px; border: none; padding: 12px; } </style>", unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

@st.cache_data
def load_data():
    chunks = []
    for fname in os.listdir("."):
        if fname.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(fname) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
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
        if any(w in ch for w in q2.split() if len(w) > 2):
            found.append(ch)
            if len(found) >= 2:
                break
    if not found:
        found = ALL_CHUNKS[:2]
    txt = ""
    for f in found:
        txt = txt + "\n" + f
    return txt[:6000]

if os.path.exists("logo.png"):
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.image("logo.png", width=150)
elif os.path.exists("Logo.png"):
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.image("Logo.png", width=150)

st.markdown("<h1 style='text-align:right;color:#000;margin-bottom
