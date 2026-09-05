import streamlit as st
from groq import Groq
import fitz
import os

st.set_page_config(page_title="Vision Colleges", layout="centered")
st.title("Vision Colleges - كليات الرؤية")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")

# المفتاح من Secrets - انت وضعته صحيح gsk_TmMI...
GROQ_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_KEY)

# الموديل الصحيح الحالي - في سطر واحد بدون تقطيع
MODEL_ID = "llama-3.1-8b-instant"

def get_context():
    # ضع هنا كود قراءة PDF الخاص بك
    return "عميد الكلية أ.د. عبد الله بن محمد الدهيش، مدة عذر الوفاة 5 أيام"

q = st.text_input("اكتب سؤالك", value="ما المدة المسموح بها لتقديم عذر حالة الوفاة")
if st.button("اضغط هنا للحصول على الإجابة"):
    ctx = get_context()
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "أجب بالعربية من النص المعطى فقط"},
                {"role": "user", "content": f"النص: {ctx}\nالسؤال: {q}"}
            ],
            temperature=0.1
        )
        st.success(completion.choices[0].message.content)
    except Exception as e:
        st.error(f"Groq Error: {e}")
