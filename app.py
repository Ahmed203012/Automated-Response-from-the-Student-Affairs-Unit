import streamlit as st
import fitz
from groq import Groq

st.set_page_config(page_title="Vision Colleges - وحدة شؤون الطلبة", layout="centered")

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

MODEL = "llama-3.1-8b-instant"

def ask_groq(question, context):
    prompt = f"أنت مساعد لكلية الرؤية. أجب من هذا النص فقط:\n{context}\n\nالسؤال: {question}"
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

# اقرأ ملف اللوائح PDF - نفس كودك القديم
# ضع باقي كودك هنا واستخدم ask_groq

st.title("Vision Colleges - كليات الرؤية")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
question = st.text_input("ما هو عميد الكلية")
if st.button("اضغط هنا للحصول على الإجابة"):
    try:
        # context = النص المستخرج من PDF
        context = "عميد الكلية هو أ.د. عبد الله بن محمد الدهيش ومدة عذر الوفاة 5 أيام يجب تقديمه خلال أسبوع" # مثال
        answer = ask_groq(question, context)
        st.success(answer)
    except Exception as e:
        st.error(f"خطأ في الاتصال بـ Groq: {e}")
