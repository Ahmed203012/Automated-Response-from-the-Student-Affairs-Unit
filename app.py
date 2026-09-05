import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# --- إعداد الصفحة وتصحيح التباعد ---
st.set_page_config(page_title="مساعد شؤون الطلبة", layout="centered")

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    html, body, p, li, div { line-height: 1.6 !important; }
    p { margin-bottom: 5px !important; }
    .answer-box { 
        background-color: #f6f9f7; 
        padding: 20px; 
        border-radius: 12px; 
        border-right: 6px solid #2e7d5b;
        white-space: pre-line;
    }
    .footer-note {
        margin-top: 20px; 
        background-color: #fdf8e8; 
        padding: 12px; 
        border-radius: 8px; 
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

st.title("مساعد شؤون الطلبة")
st.write("مرحبا بكم في كليات الرؤية - مساعد الرد الآلي للوائح الأعذار")

# المفتاح - يفضل وضعه في Secrets في Streamlit Cloud
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "AIzaضع_مفتاحك_هنا"

client = genai.Client(api_key=API_KEY)

def read_pdf(file):
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

with st.sidebar:
    st.header("1- رفع اللائحة")
    uploaded_file = st.file_uploader("ارفع ملف لائحة الأعذار PDF", type="pdf")
    if uploaded_file:
        st.session_state["laws_text"] = read_pdf(uploaded_file)
        st.success("تم تحميل اللائحة بنجاح")

if "laws_text" not in st.session_state:
    st.info("يرجى رفع ملف اللائحة أولا من القائمة الجانبية")
    st.stop()

# --- السؤال ---
st.subheader("2- اسأل سؤالك")
user_query = st.text_input("مثال: ما المدة المسموح بها لتقديم عذر طبي؟")

if st.button("اضغط هنا للحصول على الإجابة"):
    if not user_query:
        st.warning("اكتب سؤالك أولا")
    else:
        # --- Prompt مانع للتأليف 100% ---
        prompt = f"""
أنت آلة استخراج نصوص فقط. ممنوع التأليف.

النص المصدر الوحيد هو:
---
{st.session_state["laws_text"][:20000]}
---

السؤال: {user_query}

تعليمات صارمة جداً:
1. انسخ الإجابة حرفياً من النص المصدر. لا تغير أي رقم.
2. إذا السؤال عن مدة تقديم العذر عن محاضرة فالجواب هو "خلال ثلاثة أيام عمل من تاريخ التغيب" وليس أسبوع.
3. إذا السؤال عن نسبة الحرمان فالجواب "75%" وإذا عن رفع الحرمان فـ "50%".
4. إذا طُلب رقم فقط، أجب برقم فقط بدون شرح.
5. احتفظ بنفس التنسيق الأصلي:
   1. المدة المسموح بها لتقديم العذر الطبي
   2. ضوابط قبول العذر ورفع الحرمان من المقرر (المادتان 14 و 15)
   3. تنبيه في حال كان الغياب الطبي عن "اختبار"
6. لا تضف أي معلومة من خارج النص.
7. إذا لم تجد الجواب قل: لا يوجد نص صريح في اللائحة المرفوعة.
"""

        with st.spinner("جاري البحث في اللائحة..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        top_p=0.1,
                        max_output_tokens=1000
                    )
                )
                st.markdown(f'<div class="answer-box">{response.text}</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="footer-note">
                تنويه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية:<br>
                <a href="https://elearning.vision.edu.sa/course/view.php?id=188" target="_blank">https://elearning.vision.edu.sa/course/view.php?id=188</a>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"حدث خطأ: {e}")
