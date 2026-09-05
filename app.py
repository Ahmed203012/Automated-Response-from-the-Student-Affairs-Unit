import streamlit as st
import os
import glob
from google import genai
from google.genai import types
from pypdf import PdfReader

st.set_page_config(page_title="مساعد شؤون الطلبة", layout="centered")

# --- نفس التنسيق اللي كان عندك بدون تباعد كبير ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    p { line-height: 1.6 !important; margin-bottom: 4px !important; }
    .box { background-color: #f0f7f0; padding: 22px; border-radius: 12px; margin-bottom: 15px; }
    .footer { background-color: #fdf8e8; padding: 14px; border-radius: 10px; font-size: 13px; margin-top: 25px; }
</style>
""", unsafe_allow_html=True)

st.title("مساعد شؤون الطلبة")
st.caption("مرحبا بكم في كليات الرؤية - مساعد الرد الآلي")

# --- قراءة كل ملفات PDF الموجودة في المستودع تلقائياً ---
@st.cache_data
def load_all_pdfs():
    all_text = ""
    pdf_files = glob.glob("*.pdf")
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            all_text += f"\n--- بداية ملف: {pdf_file} ---\n{text}\n--- نهاية ملف: {pdf_file} ---\n"
        except:
            pass
    return all_text

# --- المفتاح ---
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)
LAWS_TEXT = load_all_pdfs()

if not LAWS_TEXT.strip():
    st.error("لم يتم العثور على ملفات PDF في المستودع")
    st.stop()

# --- واجهة السؤال ---
user_query = st.text_input("اسأل سؤالك هنا:", placeholder="مثال: ما المدة المسموح بها لتقديم عذر طبي؟")

if st.button("اضغط هنا للحصول على الإجابة"):
    if not user_query:
        st.warning("اكتب سؤالك")
    else:
        prompt = f"""
أنت مساعد شؤون الطلبة في كليات الرؤية. مهمتك الإجابة فقط من الملفات المرفوعة.

النصوص المرجعية الكاملة من جميع اللوائح:
{LAWS_TEXT[:25000]}

السؤال: {user_query}

قواعد صارمة لا تخرج عنها أبداً:
1.  ممنوع التأليف. أجب حرفياً من النصوص أعلاه. المدة للعذر عن محاضرة هي "ثلاثة أيام عمل" وليست أسبوع.
2.  كن مختصراً ومباشراً. إذا طلب رقم قل الرقم فقط.
3.  لا تطلع برا ملفات البلوكات. إذا السؤال عن عذر طبي أجب من ملف الأعذار فقط.
4.  حافظ على هذا التنسيق بالضبط في الإجابة بدون تغيير:
    1. المدة المسموح بها لتقديم العذر الطبي:
    2. ضوابط قبول العذر ورفع الحرمان من المقرر (المادتان 14 و 15):
    3. تنبيه في حال كان الغياب الطبي عن "اختبار":
5.  لا تضع مسافات كبيرة بين الأسطر.

أجب الآن.
"""
        with st.spinner("جاري البحث في اللوائح..."):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    top_p=0.1
                )
            )
            st.markdown(f'<div class="box">{response.text}</div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="footer">
            تنويه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية:<br>
            <a href="https://elearning.vision.edu.sa/course/view.php?id=188" target="_blank">https://elearning.vision.edu.sa/course/view.php?id=188</a>
            </div>
            """, unsafe_allow_html=True)
