import os, re, streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; font-weight:bold!important; }
.answer-box { background:#eaf7f0; padding:20px; border-radius:12px; line-height:1.9; border:1px solid #c3e6cb; font-size:18px; white-space:pre-wrap; }
.disclaimer-box { background:#fef9e7; padding:18px; border-radius:12px; border:1px solid #f5d78e; margin-top:20px; line-height:1.8; }
</style>
""", unsafe_allow_html=True)

c1,c2,c3=st.columns([1,1,1])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", width=140)
    elif os.path.exists("Logo.png"): st.image("Logo.png", width=140)

st.markdown("<h1 style='text-align:center!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:right!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

user_query=st.text_input(" ", placeholder="اكتب سؤالك هنا...")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT_MSG="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_file_text(path):
    low=path.lower()
    try:
        if low.endswith(".pdf"):
            try:
                import fitz
                return "\n".join([p.get_text() for p in fitz.open(path)])
            except:
                import PyPDF2
                return "\n".join([(p.extract_text() or "") for p in PyPDF2.PdfReader(path).pages])
        elif low.endswith((".xlsx",".xls")):
            import pandas as pd
            xls=pd.ExcelFile(path)
            t=""
            for sh in xls.sheet_names:
                df=xls.parse(sh,dtype=str).fillna("")
                for _,row in df.iterrows():
                    line=" | ".join([str(v) for v in row.values if str(v).strip()!=""])
                    if line: t+=line+"\n"
            return t
        elif low.endswith(".docx"):
            import docx
            return "\n".join([p.text for p in docx.Document(path).paragraphs])
        else: # txt
            for enc in ["utf-8","windows-1256","utf-8-sig"]:
                try:
                    with open(path,"r",encoding=enc,errors="ignore") as f:
                        return f.read()
                except: pass
    except: return ""
    return ""

def find_excuse_local(query, text):
    ql=query.lower()
    target=""
    if "وفاة" in ql: target="وفاة"
    elif "ولادة" in ql: target="ولادة"
    elif "زواج" in ql: target="زواج"
    elif "مرض" in ql: target="مرض"
    elif "حادث" in ql: target="حادث"
    if not target: return ""
    
    for line in text.splitlines():
        ll=line.lower()
        if target in ll and any(k in ll for k in ["يوم","ساعة","خلال","مدة","ثلاثة","يومين","24","48","72"]):
            if "مستثنى" in ll or "إلى سعادة" in ll: continue
            if len(line.strip())>5 and len(line.strip())<300:
                return line.strip()
    return ""

if btn and user_query:
    all_files=[f for f in os.listdir(".") if f.lower().endswith((".pdf",".txt",".docx",".xlsx",".xls"))]
    excuse_files=[f for f in all_files if "عذر" in f or "اعذار" in f or "ضوابط" in f.lower()]
    
    # اقرأ ملفات الأعذار فقط (الـ TXT أولا لأنه أضمن)
    excuse_text=""
    for f in excuse_files:
        excuse_text+=read_file_text(f)+"\n"
    
    # لو ما لقينا ملفات باسم عذر، اقرأ كل ملفات txt و docx
    if len(excuse_text.strip())<20:
        for f in all_files:
            if f.lower().endswith((".txt",".docx")):
                excuse_text+=read_file_text(f)+"\n"

    ans=find_excuse_local(user_query, excuse_text)

    if not ans:
        # جرب Gemini لكن أرسل فقط ملفات الأعذار وليس كل الملفات
        try:
            from google import genai
            from google.genai import types
            client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            parts=[]
            for f in excuse_files[:2]: # أرسل ملفين فقط حتى لا يعلق
                if f.lower().endswith(".pdf"):
                    try:
                        with open(f,"rb") as file:
                            parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                    except: pass
            
            # أرسل النص المستخرج من TXT أيضا
            parts.append(types.Part.from_text(text=f"نص ضوابط الأعذار:\n{excuse_text[:10000]}\n\nالسؤال: {user_query}\nأجب باختصار بالمدة فقط بدون ذكر اسم ملف. اذا غير موجود قل: {OUT_MSG}"))
            
            r=client.models.generate_content(model="gemini-1.5-flash", contents=[types.Content(role="user", parts=parts)], config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=300))
            if r.text: ans=r.text.strip()
        except:
            ans=""

    if not ans or len(ans)<3:
        ans=OUT_MSG

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
