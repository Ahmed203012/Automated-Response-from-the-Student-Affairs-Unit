import os
import streamlit as st
import pdfplumber
import pypdf
from google import genai

st.set_page_config(page_title="كليات الرؤية", layout="centered", page_icon="🎓")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
h1, h2, h3, h4, p, div, input, label, span { text-align: right!important; direction: rtl!important; }
.stTextInput > div > div > input { direction: rtl!important; text-align: right!important; }
.stButton > button { width: 100%; background-color: #C9A86A!important; color: #1A1A1A!important; font-weight: bold!important; border-radius: 10px!important; border: none!important; padding: 12px!important; font-size: 17px!important; }
.answer-box { background-color: #FFF9E6!important; border-right: 6px solid #C9A86A; padding: 18px; border-radius: 10px; margin-top: 18px; direction: rtl!important; text-align: right!important; line-height: 1.9; }
.disclaimer-box { background-color: #FFF8D6; border: 1px solid #C9A86A; padding: 12px; border-radius: 8px; margin-top: 18px; font-size: 13.5px; color: #665500; direction: rtl!important; text-align: right!important; }
</style>
""", unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except:
    st.error("أضف GEMINI_API_KEY في Secrets")
    st.stop()

@st.cache_data(show_spinner=False)
def load_all_chunks():
    chunks = []
    for file in os.listdir('.'):
        if not file.endswith('.pdf'): continue
        try:
            with pdfplumber.open(file) as pdf:
                for i, page in enumerate(pdf.pages):
                    t = page.extract_text()
                    if t and len(t.strip()) > 40:
                        chunks.append({"file": file, "page": i, "text": t})
                    for table in page.extract_tables() or []:
                        txt = ""
                        for row in table:
                            if row:
                                clean = [str(c).strip() for c in row if c and str(c).strip()]
                                if clean: txt += " | ".join(clean) + "\n"
                        if txt: chunks.append({"file": file, "page": i, "text": txt})
        except: pass
    return chunks

all_chunks = load_all_chunks()

def get_relevant_context(query, top_k=3):
    query_words = query.split()
    scored = []
    for ch in all_chunks:
        score = 0
        for w in query_words:
            if w in ch["text"]: score += 1
        if "ولادة" in query and "ولادة" in ch["text"]: score += 15
        if "وفاة" in query and "وفاة" in ch["text"]: score += 15
        if "عذر" in query and "عذر" in ch["text"]: score += 5
        if "عميد" in query and "عميد" in ch["text"]: score += 15
        scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    relevant = [c for s,c in scored[:top_k] if s>0]
    if not relevant: relevant = [c for _,c in scored[:2]]
    return "\n\n---\n\n".join([f"{c['text']}" for c in relevant])

# --- إصلاح الشعار: يدعم كل الأسماء ---
logo_file = None
for name in ["logo.png", "Logo.png", "LOGO.PNG", "logo.PNG", "logo.jpg", "Logo.jpg"]:
    if os.path.exists(name):
        logo_file = name
        break
if logo_file:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(logo_file, width=150)

st.markdown("<h1 style='text-align: right; color: #000000; margin-bottom:0; font-weight:800;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: right; color: #000000; margin-top:6px; font-weight:700;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:right; color:#555;'>كلية الرؤية بالرياض ترحب بكم، ويمكنكم طرح سؤالكم هنا وسيتم الرد من واقع اللوائح المعتمدة</p>", unsafe_allow_html=True)

user_query = st.text_input(" ", placeholder="كلية الرؤية بالرياض ترحب بكم، يمكنكم طرح سؤالكم هنا")
submit_button = st.button("اضغط هنا للحصول على الإجابة")

DISCLAIMER_TEXT = "تنويه: هذه الإجابة مستنبطة من واقع لوائح الكلية المعتمدة، وللتأكيد النهائي أو الحالات الخاصة يرجى مراجعة وحدة شؤون الطلبة عبر البوابة الإلكترونية."
PORTAL_URL = "https://portal.vision.edu.sa"

if (submit_button or user_query) and user_query:
    with st.spinner("جاري البحث في اللوائح..."):
        try:
            relevant_context = get_relevant_context(user_query)
            base = "انت مساعد دقيق جدا في كليات الرؤية. اجب فقط من النصوص المرتبطة المرفقة."
            full_prompt = base + "\n\nالنصوص:\n" + relevant_context + "\n\nسؤال الطالب:\n" + user_query
            for model_name in ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
                try:
                    response = client.models.generate_content(model=model_name, contents=full_prompt)
                    st.markdown(f"<div class='answer-box'><h4 style='color:#000000; text-align:right;'>الإجابة من واقع اللائحة:</h4><div style='text-align:right; direction:rtl;'>{response.text}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='disclaimer-box'>⚠️ {DISCLAIMER_TEXT} <a href='{PORTAL_URL}' target='_blank' style='color:#000000; font-weight:bold;'>رابط البوابة الإلكترونية</a></div>", unsafe_allow_html=True)
                    break
                except: continue
        except Exception as e:
            st.error(str(e))
