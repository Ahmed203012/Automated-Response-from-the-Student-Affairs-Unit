import os, re, streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl!important; text-align: right!important; }
* { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:14px!important; width:100%!important; font-weight:bold!important; font-size:17px!important; padding:12px!important; }
.answer-box { background:#eaf7f0; padding:22px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; line-height:2; }
.disclaimer-box { background:#fef9e7; padding:16px; border-radius:12px; border:1px solid #f5d78e; margin-top:18px; font-size:14px; }
</style>
""", unsafe_allow_html=True)

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

def read_all():
    full=""
    for f in os.listdir("."):
        low=f.lower()
        if low.endswith(".txt"):
            for enc in ["utf-8","utf-8-sig","windows-1256"]:
                try:
                    with open(f,"r",encoding=enc,errors="ignore") as file:
                        t=file.read()
                        if len(t.strip())>20:
                            full+=t+"\n"
                            break
                except: pass
        elif low.endswith(".pdf"):
            try:
                import fitz
                full+="\n".join([p.get_text() for p in fitz.open(f)])+"\n"
            except: pass
        elif low.endswith((".xlsx",".xls",".csv")):
            try:
                import pandas as pd
                df=pd.read_excel(f, dtype=str).fillna("") if not low.endswith(".csv") else pd.read_csv(f, dtype=str).fillna("")
                for _, row in df.iterrows():
                    line=" | ".join([str(v).strip() for v in row.values if str(v).strip()!=""])
                    if len(line)>5:
                        full+=line+"\n"
            except: pass
    return full

def get_answer(query, corpus):
    ql=query.lower()
    is_email = "ايميل" in ql or "@" in ql or "email" in ql
    is_name = any(x in ql for x in ["من هو","من هي","من عميد","عميد الكلية","وكيل"])
    is_duration = "مدة" in ql or "كم" in ql or "خلال" in ql

    lines=list(set([l.strip() for l in corpus.splitlines() if 15 < len(l.strip()) < 300]))

    # مرادفات
    if "طبي" in ql: ql+=" مرضية صحية تقرير طبي"
    if "حادث" in ql or "حوادث" in ql: ql+=" حادث مروري اصابة تقرير"
    if "ولادة" in ql: ql+=" ولادة وضع مولود"

    q_words=[w for w in ql.split() if len(w)>2]

    scored=[]
    for l in lines:
        score=sum(1 for w in q_words if w in l)
        # إذا سؤال عن مدة، أعط نقاط إضافية للسطر اللي فيه رقم ويوم/أسبوع
        if is_duration and re.search(r'\d+|خمسة|ثلاثة|ثلاث|اسبوع|أسبوع|يوم|أيام', l):
            if re.search(r'(يوم|أيام|اسبوع|أسبوع)', l):
                score+=3
        if score>0:
            scored.append((score,l))
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return ""

    if is_email:
        for _,l in scored:
            if "@" in l:
                return l[:300]
        return ""

    if is_name:
        for _,l in scored:
            if ("الدكتور" in l or "د." in l or "أ.د" in l) and "يجوز" not in l:
                return l[:300]
        # إذا اسم العميد موجود في ملف واحد بصيغة محددة
        for _,l in scored:
            if "عميد" in l and len(l)<150 and "يجوز" not in l:
                return l[:300]
        return ""

    # للمدة: خذ أول سطرين فيهما مدة مختلفة
    if is_duration:
        res=[]
        for _,l in scored:
            if re.search(r'(يوم|أيام|اسبوع|أسبوع)', l):
                if l not in res:
                    res.append(l)
            if len(res)>=2:
                break
        if res:
            return " - ".join(res)[:500]

    return scored[0][1][:400]

if btn and q:
    corpus=read_all()
    ans=get_answer(q, corpus)

    if not ans:
        try:
            import google.generativeai as genai
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model=genai.GenerativeModel("gemini-1.5-flash")
            # أرسل فقط السطور التي لها علاقة
            rel="\n".join([l for l in corpus.splitlines() if any(w in l for w in q.split() if len(w)>2)][:20])
            prompt=f"أجب باختصار من النص فقط. إذا سؤال عن مدة اذكر الرقم واليوم. النص:{rel[:10000]}\nالسؤال:{q}\nالإجابة:"
            r=model.generate_content(prompt)
            if r.text and "يجوز تحويل" not in r.text:
                ans=r.text.strip()[:500]
        except: pass

    if not ans:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
