import streamlit as st, os, re, fitz
from groq import Groq

st.set_page_config(page_title="Vision Colleges", layout="wide")
st.markdown("<h1 style='text-align:center'>كليات الرؤية<br>VISION COLLEGES</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center'>Vision Colleges - كليات الرؤية<br>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وأنظمة الكلية</p>", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"

@st.cache_data
def load_text():
    txt = ""
    for root,_,files in os.walk("."):
        for f in files:
            if f.lower().endswith(".pdf"):
                try:
                    doc = fitz.open(os.path.join(root,f))
                    for p in doc:
                        t = p.get_text("text")
                        if t.strip(): txt += t + "\n"
                except: pass
    return txt

corpus = load_text()

def find_context(q):
    # نظف السؤال
    q = q.strip()
    words = [w for w in re.findall(r'[\u0600-\u06FF\w]+', q) if len(w)>2]
    # خذ أفضل مقاطع تحتوي أي كلمة من السؤال
    parts = corpus.split("\n")
    ranked = []
    for i, line in enumerate(parts):
        score = sum(1 for w in words if w in line)
        if score>0: ranked.append((score, line))
    ranked.sort(reverse=True)
    if ranked:
        # خذ 12 سطر الأعلى + سطر قبله وبعده للسياق
        best_lines = [l for s,l in ranked[:12]]
        return "\n".join(best_lines)[:4000]
    else:
        # إذا لم يجد - خذ بداية ووسط وآخر النص (حيث يوجد العميد والوكيل والنظام)
        L = len(corpus)
        return (corpus[:1500] + "\n...\n" + corpus[L//2:L//2+1500] + "\n...\n" + corpus[-1500:])[:4000]

q = st.text_input(" ", placeholder="من هو عميد الكلية")
if st.button("اضغط هنا للحصول على الإجابة"):
    ctx = find_context(q)
    prompt = f"أنت مساعد وحدة شؤون الطلبة في كليات الرؤية. أجب من النص المرجعي فقط باختصار ووضوح بالعربية. إذا لم تجد المعلومة قل: المعلومة غير مذكورة بالنص المرجعي.\n\nالنص المرجعي:\n{ctx}\n\nالسؤال: {q}\nالإجابة:"
    try:
        r = client.chat.completions.create(model=MODEL, messages=[{"role":"user","content":prompt}], temperature=0.0, max_tokens=500)
        st.info(r.choices[0].message.content)
        st.warning("تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة. المرجع المعتمد هو الرابط التالي https://elearning.vision.edu.sa/course/view.php?id=188")
    except Exception as e:
        st.error(f"Groq Error: {e}")
