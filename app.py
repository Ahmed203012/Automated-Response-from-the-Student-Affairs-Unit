import os
import streamlit as st
import pdfplumber
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered")

# ستايل
st.markdown("<style> @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap'); html, body { font-family: Tajawal, sans-serif; direction: rtl; text-align: right; } .stButton>button { width: 100%; background-color: #C9A86A; color: #000; font-weight: bold; border-radius: 10px; border: none; padding: 12px; } </style>", unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def load_all_text():
    all_text = []
    for fname in os.listdir("."):
        if fname.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(fname) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
                        if t and len(t.strip()) > 20:
                            all_text.append(t)
            except:
                pass
    return all_text

ALL_CHUNKS = load_all_text()

def get_context(q):
    q2 = q.replace("ة","ه").replace("أ","ا").replace("إ","ا")
    found = []
    for ch in ALL_CHUNKS:
        ch2 = ch.replace("ة","ه").replace("أ","ا")
        for w in q2.split():
            if len(w) > 2 and w in ch2:
                found.append(ch)
                break
    if not found:
        found = ALL_CHUNKS[:5]
    txt = "\n".join(found[:5])
    return txt[:12000]

# شعار
if os.path.exists("logo.png"):
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.image("logo.png", width=150)
elif os.path.exists("Logo.png"):
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.image("Logo.png", width=150)

st.markdown("<h1 style='text-align:right;color:#000;'>Vision Colleges - كليات الرؤية</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;color:#000;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الاجابة")

DISCLAIMER = "تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:"
LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"

if btn and user_query:
    with st.spinner("جاري البحث..."):
        ctx = get_context(user_query)
        hidden = "انت مساعد رسمي لكليات الرؤية. اجب فقط من النصوص المرفقة. ممنوع الخروج عنها. اذا السؤال غير موجود قل: عذرا، هذه المعلومة غير متوفرة في اللوائح المرفقة حاليا."
        prompt = hidden + "\n\nاللوائح:\n" + ctx + "\n\nالسؤال: " + user_query
        resp = None
        for m in ["gemini-2.0-flash", "gemini-2.5-flash"]:
            try:
                r = client.models.generate_content(model=m, contents=prompt)
                if r.text:
                    resp = r
                    break
            except:
                pass
        if resp and resp.text:
            st.success(resp.text)
        else:
            st.info("عذرا، هذه المعلومة غير متوفرة في اللوائح المرفقة حاليا.")
        st.warning(DISCLAIMER)
        st.markdown(f"[{LINK}]({LINK})")
