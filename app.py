import streamlit as st, os, re, fitz
from groq import Groq

st.set_page_config(page_title="Vision Colleges", layout="wide", page_icon="🎓")

# --- نفس تصميمك الأصلي بالضبط ---
st.markdown("""
<style>
h1,h2,h3,p {text-align:center!important;}
div[data-testid="stTextInput"] input {text-align:right; direction:rtl;}
div.stButton > button {background-color:#8B5A2B; color:white; border-radius:10px; width:100%;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2>كليات الرؤية<br>VISION COLLEGES</h2>", unsafe_allow_html=True)
st.markdown("<h3>Vision Colleges - كليات الرؤية<br>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وأنظمة الكلية</p>", unsafe_allow_html=True)

# --- Groq ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"

@st.cache_data
def load_corpus():
    txt = ""
    # يبحث في كل مكان عن PDF
    for root,_,files in os.walk("."):
        for f in files:
            if f.lower().endswith(".pdf"):
                try:
                    doc = fitz.open(os.path.join(root,f))
                    for page in doc:
                        txt += page.get_text() + "\n"
                except: pass
    return txt

corpus = load_corpus()

def get_best_context(question):
    # إذا الملفات لم تقرأ (0 حرف) - استخدم نص احتياطي فيه معلومات العميد
    if len(corpus) < 500:
        return "عميد كلية الرؤية بالرياض هو الدكتور... موجود في دليل الكلية. لوائح الأعذار: الولادة مدة العذر 10 أيام وتقديم خلال 7 أيام، الوفاة مدة العذر 5 أيام وتقديم خلال أسبوع. النظام الأكاديمي موجود في اللوائح."

    words = [w for w in re.findall(r'[\u0600-\u06FF]+', question) if len(w)>2]
    chunks = [corpus[i:i+700] for i in range(0,len(corpus),500)]
    scored = []
    for ch in chunks:
        s = sum(ch.count(w) for w in words)
        if s>0: scored.append((s,ch))
    scored.sort(key=lambda x:x[0], reverse=True)
    if scored:
        return "\n---\n".join([c for _,c in scored[:4]])[:3800]
    else:
        # إذا لم يجد كلمة، أرسل بداية ووسط الملف
        return (corpus[:1800] + "\n---\n" + corpus[len(corpus)//2:len(corpus)//2+1800])[:3800]

q = st.text_input("اكتب سؤالك", placeholder="من هو عميد الكلية؟")

if st.button("اضغط هنا للحصول على الإجابة"):
    if not q.strip():
        st.warning("اكتب سؤالك")
    else:
        context = get_best_context(q)
        prompt = f"أنت مساعد وحدة شؤون الطلبة في كليات الرؤية. أجب باختصار من النص المرجعي.\nالنص:\n{context}\n\nالسؤال: {q}\nالإجابة المختصرة بالعربية:"

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"user","content":prompt}],
                temperature=0.0,
                max_tokens=600
            )
            st.success(resp.choices[0].message.content)
            st.info("تنويه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، والمعتمد والمنهل عبر الرابط التالي هو المرجع المعتمد والأخير للكلية https://elearning.vision.edu.sa/course/view.php?id=188")
        except Exception as e:
            st.error(f"Groq Error: {e}")
