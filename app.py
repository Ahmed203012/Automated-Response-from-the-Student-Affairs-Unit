import os
import re
import streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stApp"] {
    direction: rtl !important;
    text-align: right !important;
}
* {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}
div[data-testid="stImage"] { display: flex !important; justify-content: center !important; }
div[data-testid="stButton"] > button {
    background-color: #c5a880!important; color: white!important;
    border-radius: 12px!important; width: 100%!important; font-weight: bold!important;
    direction: rtl!important;
}
input[type="text"] {
    direction: rtl!important;
    text-align: right!important;
}
.answer-box {
    background-color: #eaf7f0; 
    padding: 20px; 
    border-radius: 12px; 
    line-height: 1.9; 
    border: 1px solid #c3e6cb; 
    font-size: 18px; 
    white-space: pre-wrap;
    direction: rtl!important;
    text-align: right!important;
}
.disclaimer-box {
    background-color: #fef9e7; 
    padding: 18px; 
    border-radius: 12px; 
    border: 1px solid #f5d78e; 
    margin-top: 20px; 
    line-height: 1.8;
    direction: rtl!important;
    text-align: right!important;
}
h1, h2, h3, p, div {
    direction: rtl!important;
    text-align: right!important;
}
</style>
""", unsafe_allow_html=True)

c1,c2,c3=st.columns([1,1,1])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", width=140)
    elif os.path.exists("Logo.png"): st.image("Logo.png", width=140)
    else: st.write("")

st.markdown("<h1 style='text-align: center !important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center !important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: right !important; font-size:18px;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

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

def read_txt(path):
    for enc in ["utf-8","windows-1256"]:
        try:
            with open(path,"r",encoding=enc,errors="ignore") as f: return f.read()
        except: pass
    return ""

if btn and user_query:
    all_files=[f for f in os.listdir(".") if f.lower().endswith((".pdf",".xlsx",".xls",".docx",".txt"))]

    # تصنيف الملفات حسب النوع
    council_files=[f for f in all_files if "مجلس" in f and "الكلية" in f]  # مجلس الكلية فقط للمناصب
    excuse_files=[f for f in all_files if "عذر" in f or "اعذار" in f or "ضوابط" in f]  # الأعذار فقط
    tazalum_files=[f for f in all_files if "تظلم" in f]  # التظلمات فقط
    student_council_files=[f for f in all_files if ("طلاب" in f or "طالب" in f) and "مجلس" in f]  # مجلس الطلاب فقط
    email_files=[f for f in all_files if "ايميل" in f or "بريد" in f or "هيئة" in f or "تدريس" in f]  # إيميلات أعضاء التدريس

    q_low=user_query.lower()
    target_text=""
    selected_file_names=[]

    # توجيه السؤال للملف الصحيح
    if any(k in q_low for k in ["عميد","وكيل","رئيس قسم","جودة","منصب","ادارة"]):
        selected_file_names=council_files
        for f in council_files:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+read_docx(f)+"\n"

    elif any(k in q_low for k in ["عذر","غياب","وفاة","ولادة","مرض","حرمان","مدة تقديم"]):
        selected_file_names=excuse_files
        for f in excuse_files:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+read_docx(f)+"\n"

    elif any(k in q_low for k in ["تظلم","اعتراض","شكوى"]):
        selected_file_names=tazalum_files
        for f in tazalum_files:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+"\n"

    elif any(k in q_low for k in ["مجلس الطلاب","مجلس طلاب","اتحاد الطلاب"]):
        selected_file_names=student_council_files
        for f in student_council_files:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+"\n"

    elif any(k in q_low for k in ["ايميل","إيميل","بريد","تواصل","عضو هيئة","استاذ"]):
        selected_file_names=email_files
        for f in email_files:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+"\n"

    else:
        # سؤال عام: ابحث في كل اللوائح ما عدا المجلس
        other=[f for f in all_files if f not in council_files]
        for f in other:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+"\n"

    # لو ما لقينا ملفات مطابقة، نستخدم كل شيء
    if not target_text.strip():
        for f in all_files:
            if f.lower().endswith(".pdf"): target_text+=read_pdf(f)+"\n"
            else: target_text+=read_excel(f)+read_docx(f)+read_txt(f)+"\n"

    ans=""
    try:
        from google import genai
        from google.genai import types
        client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        pdf_parts=[]
        for f in selected_file_names[:3]:
            if f.lower().endswith(".pdf"):
                try:
                    with open(f,"rb") as file:
                        pdf_parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                except: pass

        # تعليمات صارمة حسب طلبك
        system_instruction="انت مساعد شؤون الطلبة في كليات الرؤية بالرياض.\n"
        system_instruction+="قواعد صارمة:\n"
        system_instruction+="- ممنوع ذكر اسم أي ملف أو لائحة أو رقم مادة نهائيا\n"
        system_instruction+="- الإجابة من اليمين لليسار وباللغة العربية فقط\n"
        system_instruction+="- الأعذار: اجب فقط من ضوابط الأعذار الطلابية\n"
        system_instruction+="- المناصب: اجب فقط من ملف مجلس الكلية\n"
        system_instruction+="- التظلمات: اجب فقط من ملف التظلمات\n"
        system_instruction+="- الإيميلات: الإجابة تكون مختصرة جدا مع ذكر التواصل عبر الإيميل الرسمي فقط\n"
        system_instruction+="- الإجابة مختصرة جدا ومباشرة على قد السؤال\n"
        system_instruction+=f"- اذا غير موجود اجب فقط: {OUT_MSG}\n"

        prompt=f"{system_instruction}\nالسؤال: {user_query}\n\nالنصوص المعتمدة:\n{target_text[:15000]}"
        
        parts=pdf_parts+[types.Part.from_text(text=prompt)]
        r=client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=350)
        )
        ans=r.text.strip() if r and r.text else OUT_MSG
    except:
        # fallback محلي لو Gemini فشل
        lines=[l.strip() for l in target_text.splitlines() if len(l.strip())>10]
        for line in lines:
            if any(k in line.lower() for k in q_low.split() if len(k)>2):
                if "إلى سعادة" not in line and "التحقيق" not in line:
                    ans=line
                    break
        if not ans: ans=OUT_MSG

    # تأكد أن الإجابة يمين
    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a></div>", unsafe_allow_html=True)
