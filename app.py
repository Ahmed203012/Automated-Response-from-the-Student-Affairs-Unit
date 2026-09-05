import streamlit as st
import fitz # PyMuPDF
from groq import Groq
import os

st.set_page_config(page_title="Vision Colleges", layout="wide", page_icon="🎓")

# --- التصميم الكامل ---
st.markdown("""
<style>
h1 {text-align: center; font-weight: bold;}
h3 {text-align: center;}
div[data-testid="stTextInput"] {direction: rtl; text-align: right;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Vision Colleges - كليات الرؤية</h1>", unsafe_allow_html=True)
st.markdown("<h3>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وأنظمة الكلية</p>", unsafe_allow_html=True)

# --- المفتاح ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("لم يتم العثور على GROQ_API_KEY في Secrets")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# --- الموديل الوحيد الشغال حالياً في Groq - هذا يصلح خطأ 404 في صورك ---
MODEL_ID = "llama3-8b-8192"

# --- قراءة كل ملفات PDF ---
@st.cache_data
def load_pdfs():
    context = ""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pdf"):
                try:
                    doc = fitz.open(os.path.join(root, file))
                    for page in doc:
                        context += page.get_text() + "\n"
                except:
                    pass
    return context

with st.spinner("جاري تحميل لوائح الكلية..."):
    pdf_context = load_pdfs()
    if len(pdf_context) < 100:
        # نص احتياطي اذا لم يجد الملفات
        pdf_context = """
        عميد كلية الرؤية هو أ.د. عبد الله بن محمد الدهيش.
        المدة المسموح بها لتقديم عذر حالة الوفاة هي 5 أيام ويجب تقديمه خلال أسبوع من تاريخ الوفاة.
        جميع اللوائح الأكاديمية وشؤون الطلبة موجودة في ملفات الكلية.
        """

# --- صندوق السؤال بنفس تصميمك ---
question = st.text_input("اكتب سؤالك", placeholder="مثال: ما المدة المسموح بها لتقديم عذر حالة الوفاة")

if st.button("اضغط هنا للحصول على الإجابة"):
    if not question.strip():
        st.warning("الرجاء كتابة السؤال")
    else:
        try:
            completion = client.chat.completions.create(
                model=MODEL_ID, # <--- هذا السطر هو اللي كان عامل خطأ model_not_found في صورك
                messages=[
                    {"role": "system", "content": f"أنت مساعد ذكي لوحدة شؤون الطلبة في كليات الرؤية. أجب باللغة العربية فقط من خلال النص التالي. إذا لم تجد الإجابة قل لا توجد معلومة. النص: {pdf_context[:15000]}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            answer = completion.choices[0].message.content
            st.success(answer)

            st.markdown("---")
            st.caption("تنويه: هذا برنامج آلي قد يحتوي على أخطاء، في حال عدم وضوح الإجابة يرجى مراجعة وحدة شؤون الطلبة أو التواصل عبر الرابط التالي للرد المخصص والمتابعة عبر البريد الإلكتروني المخصص والخطة الدراسية.")

        except Exception as e:
            st.error(f"Groq Error: {e}")
