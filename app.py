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

q=st.text_input(" ", placeholder="اكتب سؤالك هنا... مثال: ايميل د. أحمد أو مدة عذر الوفاة")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_all_formats():
    full_text=""
    # 1- قراءة TXT
    for f in os.listdir("."):
        low=f.lower()
        if low.endswith(".txt"):
            for enc in ["utf-8","utf-8-sig","windows-1256"]:
                try:
                    with open(f,"r",encoding=enc,errors="ignore") as file:
                        t=file.read()
                        if len(t.strip())>20:
                            full_text+=f"\n[ملف {f}]\n"+t+"\n"
                            break
                except: pass
        # 2- قراءة PDF
        elif low.endswith(".pdf"):
            try:
                import fitz
                t="\n".join([p.get_text() for p in fitz.open(f)])
                if len(t.strip())>20:
                    full_text+=f"\n[ملف {f}]\n"+t+"\n"
            except: pass
        # 3- قراءة Excel للإيميلات
        elif low.endswith((".xlsx",".xls")):
            try:
                import pandas as pd
                xls=pd.ExcelFile(f)
                for sheet in xls.sheet_names:
                    df=pd.read_excel(f, sheet_name=sheet, dtype=str).fillna("")
                    # حول كل صف إلى نص: اسم - ايميل - قسم
                    for _, row in df.iterrows():
                        row_text=" | ".join([f"{col}: {str(row[col]).strip()}" for col in df.columns if str(row[col]).strip()!=""])
                        if len(row_text)>10:
                            full_text+=row_text+"\n"
            except: pass
        elif low.endswith(".csv"):
            try:
                import pandas as pd
                df=pd.read_csv(f, dtype=str).fillna("")
                for _, row in df.iterrows():
                    row_text=" | ".join([f"{col}: {str(row[col]).strip()}" for col in df.columns if str(row[col]).strip()!=""])
                    if len(row_text)>10:
                        full_text+=row_text+"\n"
            except: pass
    return full_text

def retrieve_relevant_chunks(query, corpus, top_k=5):
    # قسم النص إلى فقرات 400 حرف
    chunks=re.split(r'\n+', corpus)
    chunks=[c.strip() for c in chunks if len(c.strip())>20]
    q_words=[w for w in query.split() if len(w)>2]

    scored=[]
    for ch in chunks:
        score=sum(1 for w in q_words if w in ch)
        # إذا السؤال عن ايميل، أعط وزن للإيميل
        if "@" in ch or "ايميل" in q.lower() or "email" in q.lower():
            if any(w in ch for w in q_words):
                score+=2
        if score>0:
            scored.append((score,ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    best=[c for _,c in scored[:top_k]]
    return "\n".join(best)

if btn and q:
    corpus=read_all_formats()

    # استخرج أهم الفقرات فقط - لا ترسل كل الملفات لـ Gemini
    relevant=retrieve_relevant_chunks(q, corpus, top_k=8)

    ans=""
    if not relevant:
        ans=OUT
    else:
        try:
            import google.generativeai as genai
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model=genai.GenerativeModel("gemini-1.5-flash")
            prompt=f"""أنت مساعد شؤون الطلبة في كليات الرؤية.
أجب باختصار شديد (سطر أو سطرين فقط) ومن النص المرجعي فقط.
- إذا سُئلت عن مدة عذر: اذكر المدة + خلال كم يجب التقديم.
- إذا سُئلت عن ايميل دكتور: اذكر الاسم والايميل كما هو في النص.
- إذا سُئلت عن عميد الكلية أو وكيل أو اسم شخص: ابحث عن الاسم في النص، لا تشرح كلمة عميد.
- إذا لم تجد الإجابة في النص، قل بالضبط: {OUT}

النص المرجعي:
{relevant[:12000]}

السؤال: {q}
الإجابة المختصرة:"""
            r=model.generate_content(prompt)
            if r.text:
                ans=r.text.strip()
        except Exception as e:
            # fallback محلي إذا فشل Gemini
            ans=relevant[:500]

    if not ans or len(ans.strip())<3:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
