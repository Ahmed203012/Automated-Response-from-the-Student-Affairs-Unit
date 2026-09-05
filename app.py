import streamlit as st, os, re, fitz
from groq import Groq

st.set_page_config(page_title="Vision Colleges", layout="wide")
st.markdown("<h1 style='text-align:center'>Vision Colleges - كليات الرؤية</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)

GROQ_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_KEY)
MODEL_ID = "openai/gpt-oss-20b"

# كلمات عامة يجب تجاهلها في البحث
STOP_WORDS = {"ما","من","هو","هي","هل","في","عن","على","الى","إلى","كيف","لماذا","متى","أين","بها","لها","هذا","هذه","الذي","التي"}

def load_chunks():
    full = ""
    for r,_,fs in os.walk("."):
        for f in fs:
            if f.lower().endswith(".pdf"):
                try:
                    doc = fitz.open(os.path.join(r,f))
                    for p in doc: full += p.get_text() + "\n"
                except: pass
    # تقسيم ذكي كل 500 حرف
    chunks = [full[i:i+500] for i in range(0,len(full),400)]
    return full, chunks

corpus, chunks = load_chunks()

def get_context(question):
    # تنظيف السؤال من الكلمات العامة
    q_words = [w for w in re.findall(r'\w+', question) if w not in STOP_WORDS and len(w)>2]
    if not q_words: q_words = re.findall(r'\w+', question)

    scored = []
    for ch in chunks:
        score = sum(1 for w in q_words if w in ch)
        if score>0: scored.append((score,ch))

    scored.sort(key=lambda x:x[0], reverse=True)
    if not scored:
        # إذا لم يجد، ارجع 3500 حرف من المنتصف حيث اسم العميد والوكيل
        mid = len(corpus)//2
        return corpus[mid:mid+3500]

    top = "\n---\n".join([c for s,c in scored[:5]])
    return top[:4000]

q = st.text_input("اكتب سؤالك")
if st.button("اضغط هنا للحصول على الإجابة"):
    ctx = get_context(q)
    prompt = f"أجب من النص المرجعي فقط. إذا غير موجود قل: المعلومة غير متوفرة في اللوائح. النص: {ctx}\nالسؤال: {q}\nالإجابة المختصرة:"
    try:
        r = client.chat.completions.create(model=MODEL_ID, messages=[{"role":"user","content":prompt}], temperature=0.0, max_tokens=500)
        st.success(r.choices[0].message.content)
        # للتشخيص - احذفه بعد ما تتأكد
        with st.expander("النص المرجعي المستخدم (للتأكد)"):
            st.text(ctx[:2000])
    except Exception as e:
        st.error(e)
