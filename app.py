import streamlit as st
import os, re
import fitz
from groq import Groq

st.set_page_config(page_title="Vision Colleges", layout="wide", page_icon="🎓")
st.markdown("<h1 style='text-align:center'>Vision Colleges - كليات الرؤية</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وانظمة الكلية</p>", unsafe_allow_html=True)

# المفتاح
GROQ_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_KEY)
MODEL_ID = "openai/gpt-oss-20b" # شغال حاليا بعد إيقاف llama-3.x

@st.cache_data
def load_all_chunks():
    full_text = ""
    for root, _, files in os.walk("."):
        for f in files:
            if f.lower().endswith(".pdf"):
                try:
                    doc = fitz.open(os.path.join(root, f))
                    for p in doc:
                        full_text += p.get_text() + "\n"
                except: pass
    # قسم النص إلى مقاطع 600 حرف
    chunks = [full_text[i:i+600] for i in range(0, len(full_text), 500)]
    return full_text, chunks

corpus, chunks = load_all_chunks()

def search_chunks(question, chunks, top_k=6):
    q_words = set(re.findall(r'\w+', question.lower()))
    scored = []
    for ch in chunks:
        ch_words = set(re.findall(r'\w+', ch.lower()))
        score = len(q_words & ch_words)
        if score > 0:
            scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = [c for s,c in scored[:top_k]]
    # إذا لم يجد شيء، خذ أول 4000 حرف كاحتياط
    if not best:
        return corpus[:4000]
    return "\n---\n".join(best)[:4000]

question = st.text_input("اكتب سؤالك", placeholder="ما الفترة المسموح بها لتقديم عذر...")

if st.button("اضغط هنا للحصول على الإجابة"):
    if not question.strip():
        st.warning("اكتب سؤالك")
    else:
        context = search_chunks(question, chunks)
        prompt = f"""أنت مساعد وحدة شؤون الطلبة في كليات الرؤية.
مهمتك: أجب من النص المرجعي فقط. لا تخترع.
إذا كانت المعلومة غير موجودة قل: هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة.

النص المرجعي:
{context}

السؤال: {question}
الإجابة الواضحة والمختصرة بالعربية:"""

        try:
            resp = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role":"user","content":prompt}],
                temperature=0.1,
                max_tokens=800
            )
            st.success(resp.choices[0].message.content)
            st.caption("تنويه: هذا برنامج آلي قد يحتوي على أخطاء، في حال عدم وضوح الإجابة يرجى مراجعة وحدة شؤون الطلبة")
        except Exception as e:
            st.error(f"Groq Error: {e}")
