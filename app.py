import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# --- 1- تصحيح التنسيق والتباعد الكبير ---
st.set_page_config(page_title="مساعد شؤون الطلبة", layout="centered", page_title_="مساعد شؤون الطلبة")

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    p, li, div { line-height: 1.7 !important; margin-bottom: 6px !important; }
    h1, h2, h3 { margin-top: 15px !important; margin-bottom: 10px !important; }
    .answer-box { background-color: #f0f7f4; padding: 20px; border-radius: 10px; border-right: 5px solid #2e7d5b; }
</style>
""", unsafe_allow_html=True)

st.title("مساعد شؤون الطلبة")
st.caption("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

API_KEY = "AIzaضع_مفتاحك_هنا"
client = genai.Client(api_key=API_KEY)

# --- 2- قراءة اللوائح ---
def read_pdf(file):
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

with st.sidebar:
    st.header("رفع اللوائح")
    f1 = st.file_uploader("ملف الأعذار الطلابية", type="pdf")
    if f1:
        st.session_state["laws"] = read_pdf(f1)
        st.success("تم تحميل اللائحة")

if "laws" not in st.session_state:
    st.info("يرجى رفع لائحة الأعذار من الشريط الجانبي أولاً")
    st.stop()

# --- 3- السؤال ---
query = st.text_input("مثال: ما المدة المسموح بها لتقديم عذر طبي عن المحاضرات؟")

if st.button("اضغط هنا للحصول على الإجابة") and query:

    # --- 4- Prompt مانع التأليف 100% ---
    system_prompt = f"""
أنت نظام استخراج معلومات حرفي. ممنوع منعاً باتاً التأليف أو التلخيص أو إضافة كلمات من عندك.

المصدر الوحيد هو هذا النص:
---
{st.session_state["laws"][:18000]}
---

قواعد إجبارية:
1.  إذا سُئلت عن مدة تقديم العذر عن محاضرة: الجواب هو حرفياً من النص: "خلال ثلاثة أيام عمل من تاريخ التغيب عن الفعالية الأكاديمية" - لا تقل أسبوع.
2.  إذا سُئلت عن نسبة الحرمان: الجواب هو "75%" و "50%" فقط كما في النص.
3.  لا تجب بأكثر من المطلوب. إذا طُلب رقم، أجب برقم فقط.
4.  حافظ على نفس ترقيم وتنسيق اللائحة الأصلية: 1. المدة المسموح بها... 2. ضوابط قبول العذر... 3. تنبيه في حال كان الغياب عن اختبار.
5.  اذكر الفقرة الأصلية نسخ لصق. لا تغير كلمة واحدة.
6.  إذا لم تجد المعلومة، قل: لا يوجد نص صريح في اللائحة المرفوعة.

المطلوب الآن: أجب عن هذا السؤال: {query}
بالتنسيق المحدد وبدون تباعد كبير وبدون إضافة مقدمات.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=system_prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,  # هذا يمنعه يألف
                top_p=0.1,
                max_output_tokens=800
            )
        )
        
        # --- 5- عرض بنفس التنسيق اللي في صورك ---
        st.markdown(f'<div class="answer-box">{response.text}</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top:20px; background-color:#fdf8e8; padding:15px; border-radius:8px; font-size:13px;'>
        تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br>
        <a href='https://elearning.vision.edu.sa/course/view.php?id=188' target='_blank'>https://elearning.vision.edu.sa/course/view.php?id=188</a>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"خطأ: {e}")
