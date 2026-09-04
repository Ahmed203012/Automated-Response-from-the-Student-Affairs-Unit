import os
import streamlit as st
import pdfplumber
import pypdf
from google import genai

st.set_page_config(page_title="كليات الرؤية", layout="centered", page_icon="🎓")

# --- تصميم الهوية النهائي RTL + الذهبي + الشعار ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
h1, h2, h3, h4, p, div, input, label, span { text-align: right !important; direction: rtl !important; }
.stTextInput > div > div > input { direction: rtl !important; text-align: right !important; }
.stButton > button { width: 100%; background-color: #C9A86A !important; color: #1A1A1A !important; font-weight: bold !important; border-radius: 10px !important; border: none !important; padding: 12px !important; font-size: 17px !important; }
.stButton > button:hover { background-color: #B8965A !important; color: white !important; }
.answer-box { background-color: #FFF9E6 !important; border-right: 6px solid #C9A86A; padding: 18px; border-radius: 10px; margin-top: 18px; direction: rtl !important; text-align: right !important; line-height: 1.8; }
.disclaimer-box { background-color: #FFF8D6; border: 1px solid #C9A86A; padding: 12px; border-radius: 8px; margin-top: 18px; font-size: 13.5px; color: #665500; direction: rtl !important; text-align: right !important; }
.logo-container { text-align: center !important; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except:
    st.error("أضف GEMINI_API_KEY في Secrets")
    st.stop()

@st.cache_data(show_spinner=False)
def load_all_documents():
    txt = ""
    for file in os.listdir('.'):
        if not file.endswith('.pdf'): continue
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: txt += f"\n--- {file} ---\n" + t + "\n"
                    for table in page.extract_tables() or []:
                        for row in table:
                            if row:
                                clean = [str(c).strip() for c in row if c and str(c).strip()]
                                if clean: txt += " | ".join(clean) + "\n"
        except:
            try:
                reader = pypdf.PdfReader(file)
                for p in reader.pages:
                    t = p.extract_text()
                    if t: txt += t + "\n"
            except: pass
    # --- حل مشكلة السرعة: نأخذ أهم 12000 حرف فقط ---
    return txt.strip()[:12000]

context = load_all_documents()

# --- الشعار (لو رفعت ملف اسمه logo.png سيظهر تلقائيا) ---
if os.path.exists("logo.png"):
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("logo.png", width=120)
    st.markdown("</div>", unsafe_allow_html=True)

# --- العناوين باللون الذهبي والأسود ---
st.markdown("<h1 style='text-align: right; color: #C9A86A; margin-bottom:0; font-weight:800;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: right; color: #222; margin-top:6px; font-weight:700;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:right; color:#555; margin-top:10px;'>كلية الرؤية بالرياض ترحب بكم، ويمكنكم طرح سؤالكم هنا وسيتم الرد من واقع اللوائح المعتمدة</p>", unsafe_allow_html=True)

user_query = st.text_input(" ", placeholder="مثال: ما الفترة المسموح بها لتقديم العذر في حالة الوفاة؟")
submit_button = st.button("اضغط هنا للحصول على الإجابة")

DISCLAIMER_TEXT = "تنويه: هذه الإجابة مستنبطة من واقع لوائح الكلية المعتمدة، وللتأكيد النهائي أو الحالات الخاصة يرجى مراجعة وحدة شؤون الطلبة عبر البوابة الإلكترونية."

if (submit_button or user_query) and user_query:
    with st.spinner("جاري البحث..."):
        try:
            base = "انت مساعد اكاديمي في كليات الرؤية. اجب باختصار ودقة من النص فقط، واذكر اسم العميد من جدول مجلس الكلية اذا سئلت. اللغة عربية فصحى RTL."
            full_prompt = base + "\n\nالنص:\n" + context + "\n\nسؤال:\n" + user_query
            # ترتيب جديد للسرعة: نبدأ بالأسرع
            candidates = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest", "gemini-3-flash-preview"]
            for model_name in candidates:
                try:
                    response = client.models.generate_content(model=model_name, contents=full_prompt)
                    st.markdown(f"<div class='answer-box'><h4 style='color:#8C6D2F; text-align:right; margin-top:0;'>الإجابة من واقع اللائحة:</h4><div style='text-align:right; direction:rtl;'>{response.text}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='disclaimer-box'>⚠️ {DISCLAIMER_TEXT} <a href='https://vision.edu.sa' target='_blank'>رابط البوابة</a></div>", unsafe_allow_html=True)
                    break
                except: continue
            else:
                st.error("النظام مشغول حاليا، حاول بعد دقيقة")
        except Exception as e:
            st.error(str(e))
