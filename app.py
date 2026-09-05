import os
import re
import streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; font-weight:bold!important; }
input[type="text"] { direction:rtl!important; text-align:right!important; }
.answer-box { background:#eaf7f0; padding:20px; border-radius:12px; line-height:1.9; border:1px solid #c3e6cb; font-size:18px; white-space:pre-wrap; direction:rtl!important; text-align:right!important; }
.disclaimer-box { background:#fef9e7; padding:18px; border-radius:12px; border:1px solid #f5d78e; margin-top:20px; line-height:1.8; direction:rtl!important; text-align:right!important; }
</style>
""", unsafe_allow_html=True)

c1,c2,c3=st.columns([1,1,1])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", width=140)
    elif os.path.exists("Logo.png"): st.image("Logo.png", width=140)
    else: st.write("")

st.markdown("<h1 style='text-align:center!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:right!important; font-size:18px;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

user_query=st.text_input(" ", placeholder="اكتب سؤالك هنا...")
btn=st.button("اضغط هنا للحصول على الإجابة")
LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT_MSG="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."

def read_pdf(path):
    try:
        import fitz
        return "\n".join([p.get_text() for p in fitz.open(path)])
    except:
        try:
            import PyPDF2
            return "\n".join([(p.extract_text() or "") for p in PyPDF2.PdfReader(path).pages])
        except: return ""

def read_excel(path):
    try:
        import pandas as pd
        xls=pd.ExcelFile(path)
        t=""
        for sh in xls.sheet_names:
            df=xls.parse(sh,dtype=str).fillna("")
            for _,row in df.iterrows():
                line=" | ".join([str(v).strip() for v in row.values if str(v).strip()!=""])
                if line: t+=line+"\n"
        return t
    except: return ""

def read_docx(path):
    try:
        import docx
        return "\n".join([p.text for p in docx.Document(path).paragraphs])
    except: return ""

# --- دوال البحث الدقيق ---

def find_email_exact(query, text):
    # استخرج كل الأسطر اللي فيها @
    email_lines=[l for l in text.splitlines() if "@" in l and "." in l]
    # كلمات الاسم المطلوب (بدون كلمة ايميل)
    q=query.replace("ما","").replace("ماهو","").replace("ايميل","").replace("إيميل","").replace("بريد","").strip()
    q_tokens=[w.strip() for w in q.split() if len(w.strip())>2]
    
    best=""
    max_score=0
    for line in email_lines:
        low=line.lower()
        score=0
        for tok in q_tokens:
            if tok in line:  # لازم الاسم كامل موجود
                score+=1
        # لازم كل كلمات الاسم تكون موجودة (احمد + حسين) وليس احمد فقط
        if score==len(q_tokens) and score>0:
            return line.strip()
        if score>max_score:
            max_score=score
            best=line.strip()
    # لو ما لقينا تطابق كامل، لا ترجع أي شيء - حتى لا يرجع اسم خطأ
    if max_score < len(q_tokens):
        return ""
    return best

def find_excuse_duration(query, text):
    q_low=query.lower()
    target_type=""
    if "ولادة" in q_low: target_type="الولادة"
    elif "وفاة" in q_low: target_type="الوفاة"
    elif "مرض" in q_low: target_type="المرض"
    elif "زواج" in q_low: target_type="الزواج"
    
    if not target_type:
        return ""

    # ابحث عن السطر اللي فيه نوع العذر + مدة بالأرقام
    for line in text.splitlines():
        ll=line.lower()
        if target_type.lower() in ll and any(x in ll for x in ["يوم","ساعة","خلال","مدة","ثلاثة","يومين","24","72"]):
            # استبعد اسطر المستثنى والشروط
            if "مستثنى" in ll or "في حال تعذر" in ll:
                continue
            if len(line.strip())<250:
                return line.strip()
    
    # بحث ثاني: فقرة كاملة عن العذر
    pattern=re.compile(rf"{target_type}.*?(?:\d+.*?(?:يوم|ساعة)|ثلاثة أيام|يومين)", re.IGNORECASE|re.DOTALL)
    m=pattern.search(text)
    if m:
        return m.group(0)[:200]
    return ""

if btn and user_query:
    all_files=[f for f in os.listdir(".") if f.lower().endswith((".pdf",".xlsx",".xls",".docx",".txt"))]
    council_files=[f for f in all_files if "مجلس" in f and "الكلية" in f]
    excuse_files=[f for f in all_files if "عذر" in f or "ضوابط" in f]
    tazalum_files=[f for f in all_files if "تظلم" in f]
    email_files=[f for f in all_files if "ايميل" in f or "بريد" in f or "هيئة" in f or "تدريس" in f or "اعضاء" in f]

    q_low=user_query.lower()
    target_text=""
    selected=[]

    if any(k in q_low for k in ["عميد","وكيل","رئيس قسم","جودة"]):
        selected=council_files
    elif any(k in q_low for k in ["عذر","غياب","وفاة","ولادة","مدة تقديم","المسموح"]):
        selected=excuse_files
    elif any(k in q_low for k in ["تظلم"]):
        selected=tazalum_files
    elif any(k in q_low for k in ["ايميل","إيميل","بريد","احمد حسين"]):
        selected=email_files
    else:
        selected=all_files

    full=""
    for f in selected:
        if f.lower().endswith(".pdf"): full+=read_pdf(f)+"\n"
        else: full+=read_excel(f)+read_docx(f)+"\n"

    if not full.strip():
        for f in all_files:
            if f.lower().endswith(".pdf"): full+=read_pdf(f)+"\n"
            else: full+=read_excel(f)+"\n"

    ans=""

    # 1- الإيميل: مطابقة دقيقة للاسم كامل
    if any(k in q_low for k in ["ايميل","إيميل","بريد"]):
        ans=find_email_exact(user_query, full)
        if ans:
            # اجعل الإجابة مختصرة: الاسم | الإيميل فقط
            ans=ans[:120]

    # 2- الأعذار: استخراج المدة
    elif any(k in q_low for k in ["مدة","المسموح","تقديم عذر"]):
        ans=find_excuse_duration(user_query, full)

    # 3- المناصب: من المجلس فقط
    if not ans and any(k in q_low for k in ["عميد","وكيل","رئيس"]):
        for line in full.splitlines():
            if len(line)<5 or "إلى سعادة" in line or "التحقيق" in line: continue
            if "عميد" in q_low and "عميد" in line and "د." in line:
                ans=line.strip(); break
            if "وكيل" in q_low and "وكيل" in line and "د." in line:
                ans=line.strip(); break

    # 4- لو ما لقينا، استخدم Gemini بتعليمات صارمة
    if not ans:
        try:
            from google import genai
            from google.genai import types
            client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            pdf_parts=[]
            for f in selected[:2]:
                if f.lower().endswith(".pdf"):
                    try:
                        with open(f,"rb") as file:
                            pdf_parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                    except: pass

            instr="انت مساعد شؤون الطلبة. ممنوع ذكر اسم ملف. الإجابة مختصرة جدا من النص فقط.\n"
            instr+="- للايميل: اذا سئل عن شخص معين، يجب ان يحتوي السطر على الاسم كامل (مثلا احمد حسين يجب ان يحتوي السطر على احمد وحسين معا وليس احمد فقط) + ايميله\n"
            instr+="- للأعذار: اذكر المدة فقط (مثلا: ثلاثة أيام عمل) بدون شرح المستثنى\n"
            instr+=f"- اذا غير موجود: {OUT_MSG}\n"

            prompt=f"{instr}\nالسؤال: {user_query}\n\nالنص:\n{full[:12000]}"
            parts=pdf_parts+[types.Part.from_text(text=prompt)]
            r=client.models.generate_content(model="gemini-1.5-flash", contents=[types.Content(role="user", parts=parts)], config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=250))
            ans=r.text.strip() if r and r.text else OUT_MSG
        except:
            ans=OUT_MSG

    if not ans or len(ans)<3: ans=OUT_MSG
    # منع
