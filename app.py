import os, re, streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl!important; text-align: right!important; }
* { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:14px!important; width:100%!important; font-weight:bold!important; font-size:17px!important; }
.answer-box { background:#eaf7f0; padding:22px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; line-height:2; }
.disclaimer-box { background:#fef9e7; padding:16px; border-radius:12px; border:1px solid #f5d78e; margin-top:18px; font-size:14px; }
</style>
""", unsafe_allow_html=True)

# الشعار كبير في الوسط
c1,c2,c3=st.columns([1,1.2,1])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    elif os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)

st.markdown("<h1 style='text-align:center!important; font-size:32px!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center!important; font-size:26px!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center!important; font-size:18px!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

q=st.text_input(" ", placeholder="اكتب سؤالك هنا...")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_all_files():
    full=""
    for fname in os.listdir("."):
        low=fname.lower()
        # يقرأ كل TXT وكل PDF
        if low.endswith(".txt"):
            for enc in ["utf-8","utf-8-sig","windows-1256"]:
                try:
                    with open(fname,"r",encoding=enc,errors="ignore") as f:
                        t=f.read()
                        if len(t.strip())>20:
                            full+=t+"\n"
                            break
                except: pass
        elif low.endswith(".pdf"):
            try:
                import fitz
                t="\n".join([p.get_text() for p in fitz.open(fname)])
                full+=t+"\n"
            except: pass
    return full

def get_answer(query, text):
    q_words=[w for w in query.split() if len(w)>2]
    sentences=re.split(r'[\n\.]+', text)
    sentences=[s.strip() for s in sentences if 15 < len(s) < 350]

    scored=[]
    for s in sentences:
        score=sum(1 for w in q_words if w in s)
        if score>0:
            scored.append((score, s))
    scored.sort(reverse=True, key=lambda x: x[0])

    if not scored:
        return ""
    return scored[0][1]

if btn and q:
    full_text=read_all_files()
    ans=get_answer(q, full_text)
    if not ans:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
