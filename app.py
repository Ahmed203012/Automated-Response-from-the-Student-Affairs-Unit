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
    return "\n".join(found)[:6000]

if os.path.exists("logo.png"):
    c1,c2,c3 = st.columns([1,2,1])
    with c2: st.image("logo.png", width=150)
elif os.path.exists("Logo.png"):
    c1,c2,c3 = st.columns([1,2,1])
    with c2: st.image("Logo.png", width=150)

st.markdown("<h1 style='text-align:right;color:#000;margin-bottom:0;'>Vision Colleges - كليات الرؤية</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;color:#000;margin-top:5px;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)

# العبارة الترحيبية الحلوة التي طلبتها
st.markdown("<p style='text-align:right;color:#444;font-size:16px;line-height:1.8;margin-top:10px;'>مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية، يمكنكم طرح أي سؤال وسيتم الرد عليكم مباشرة من واقع اللوائح المعتمدة.</p>", unsafe_allow_html=True)

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا - مثلا: ما هو وكيل الكلية؟")
btn = st.button("اضغط هنا للحصول على الاجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"
DISCLAIMER_HTML = f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية: <br><a href='{LINK}' target='_blank' style='color:#000;font-weight:bold;word-break:break-all;'>{LINK}</a>"

if btn and user_query:
    ctx = get_context(user_query)
    ans = ""
    try:
        prompt = "اجب فقط من هذه اللوائح. اذا غير موجود قل غير موجود.\n\n" + ctx + "\n\nالسؤال: " + user_query
        r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        ans = r.text
    except:
        ans = "من واقع اللوائح المرفقة:\n\n" + ctx[:1500]

    if not ans:
        ans = "عذرا، هذه المعلومة غير متوفرة في اللوائح المرفقة حاليا."

    st.markdown(f"<div style='background:#FFF9E6;border-right:6px solid #C9A
