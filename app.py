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
                t="\n".join([p.get_text() for p in fitz.open(f)])
                full+=t+"\n"
            except: pass
        elif low.endswith((".xlsx",".xls",".csv")):
            try:
                import pandas as pd
                if low.endswith(".csv"):
                    df=pd.read_csv(f, dtype=str).fillna("")
                else:
                    df=pd.read_excel(f, dtype=str).fillna("")
                # حول كل صف لصيغة قابلة للبحث
                for _, row in df.iterrows():
                    line=" | ".join([str(v).strip() for v in row.values if str(v).strip()!=""])
                    if "@" in line or len(line)>10:
                        full+=line+"\n"
            except: pass
    return full

def get_answer(query, corpus):
    # إذا السؤال عن اسم شخص (من هو عميد / من هو وكيل / اسم دكتور)
    is_name_query = any(x in query for x in ["من هو","من هي","من عميد","من وكيل","اسم"])
    is_email_query = "ايميل" in query or "إيميل" in query or "email" in query.lower() or "@" in query

    # قسم لجمل
    lines=[l.strip() for l in corpus.splitlines() if 10 < len(l.strip()) < 250]
    # احذف التكرار (هذا اللي كان يسبب تكرار جملة يجوز تحويل الطالب 4 مرات)
    uniq=[]
    seen=set()
    for l in lines:
        if l not in seen:
            uniq.append(l)
            seen.add(l)
    lines=uniq

    q_words=[w for w in query.split() if len(w)>2 and w not in ["من","هو","هي","ما","كم","ما هو"]]

    scored=[]
    for l in lines:
        score=sum(1 for w in q_words if w in l)
        if score>0:
            scored.append((score,l))
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return ""

    # للايميل: لازم الجواب يحتوي @
    if is_email_query:
        for _,l in scored:
            if "@" in l:
                return l[:300]
        return "" # لا يوجد ايميل -> غير متوفرة

    # لاسم العميد: لازم الجواب يحتوي "الدكتور" أو "د." أو اسم صريح وليس "يجوز تحويل"
    if is_name_query:
        for _,l in scored:
            if ("الدكتور" in l or "د." in l or "أ." in l) and "يجوز" not in l and "تحويل" not in l:
                return l[:300]
        # إذا لم نجد اسم، لا نرجع جملة تحويل، نرجع فارغ -> غير متوفرة
        return ""

    # سؤال عن مدة: ارجع جملتين مختلفتين فقط (المدة + التقديم)
    result=[]
    for _,l in scored[:6]:
        if l not in result:
            result.append(l)
        if len(result)>=2:
            break
    return " - ".join(result)[:500]

if btn and q:
    corpus=read_all()
    ans=get_answer(q, corpus)

    # إذا لم يجد بالبحث المحلي، جرب Gemini لكن مع منع التكرار
    if not ans:
        try:
            import google.generativeai as genai
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model=genai.GenerativeModel("gemini-1.5-flash")
            # أرسل فقط الفقرات التي تحتوي كلمة من السؤال
            relevant="\n".join([l for l in corpus.splitlines() if any(w in l for w in q.split() if len(w)>2)][:15])
            if relevant:
                prompt=f"أجب في جملة واحدة فقط من النص. إذا كان السؤال عن اسم ولم تجد اسم شخص في النص قل: {OUT}\nالنص:{relevant[:8000]}\nالسؤال:{q}"
                r=model.generate_content(prompt)
                if r.text and "يجوز تحويل" not in r.text: # امنع تكرار جملة التحويل
                    ans=r.text.strip()[:400]
        except: pass

    if not ans:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
