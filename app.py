import os
import re
import streamlit as st

st.set_page_config(page_title="Vision Colleges", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl!important; text-align: right!important; font-family: 'Tajawal', sans-serif!important; }
div[data-testid="stImage"] { display: flex; justify-content: center; }
div[data-testid="stButton"] > button { background-color: #c5a880!important; color: white!important; border-radius: 12px!important; width: 100%!important; font-weight: bold!important; }
.answer-box { background-color: #eaf7f0; padding: 20px; border-radius: 12px; line-height: 1.8; border: 1px solid #c3e6cb; font-size: 18px; white-space: pre-wrap; }
.disclaimer-box { background-color: #fef9e7; padding: 18px; border-radius: 12px; border: 1px solid #f5d78e; margin-top: 20px; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([2,1,2])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    elif os.path.exists("Logo.png"): st.image("Logo.png", width=120)
    else: st.write("")

st.markdown("<h1 style='text-align:center;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"
OUT_MSG = "هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."

def read_pdf_text(path):
    txt=""
    try:
        import fitz
        doc=fitz.open(path)
        for page in doc: txt+=page.get_text()+"\n"
        return txt
    except: pass
    try:
        import PyPDF2
        reader=PyPDF2.PdfReader(path)
        for p in reader.pages: txt+=(p.extract_text() or "")+"\n"
        return txt
    except: return ""

def read_excel_text(path):
    try:
        import pandas as pd
        xls=pd.ExcelFile(path)
        txt=""
        for sheet in xls.sheet_names:
            df=xls.parse(sheet,dtype=str).fillna("")
            for _,row in df.iterrows():
                line=" | ".join([str(v).strip() for v in row.values if str(v).strip()!=""])
                if line: txt+=line+"\n"
        return txt
    except: return ""

def read_word_text(path):
    try:
        import docx
        doc=docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except: return ""

def read_txt_text(path):
    for enc in ["utf-8","windows-1256"]:
        try:
            with open(path,"r",encoding=enc,errors="ignore") as f: return f.read()
        except: pass
    return ""

def extract_council_members(full_text):
    members=[]
    for line in full_text.splitlines():
        line=line.strip()
        if len(line)<5: continue
        # السطر لازم فيه منصب + اسم (د. أو أ.د.)
        if any(k in line for k in ["عميد","وكيل","رئيس","مدير","مشرف","مسؤول"]) and ("د." in line or "أ." in line or "الدهمش" in line or "المريخي" in line):
            # استبعد أسطر اللوائح اللي فيها "إلى سعادة وكيل"
            if "إلى سعادة" in line or "رفع التوصيات" in line or "التحقيق" in line:
                continue
            members.append(line)
    return members

if btn and user_query:
    all_files=[f for f in os.listdir(".") if f.lower().endswith((".pdf",".xlsx",".xls",".docx",".txt"))]
    council_files=[f for f in all_files if "مجلس" in f.lower()]
    other_files=[f for f in all_files if "مجلس" not in f.lower()]

    # نقرأ ملفات المجلس أولاً
    council_text=""
    other_text=""
    pdf_parts=[]
    try:
        from google.genai import types
        for f in council_files+other_files:
            low=f.lower()
            if low.endswith(".pdf"):
                t=read_pdf_text(f)
                if "مجلس" in f: council_text+=t+"\n"
                else: other_text+=t+"\n"
                try:
                    with open(f,"rb") as file:
                        pdf_parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                except: pass
            elif low.endswith((".xlsx",".xls")):
                t=read_excel_text(f)
                if "مجلس" in f: council_text+=t+"\n"
                else: other_text+=t+"\n"
            elif low.endswith(".docx"):
                t=read_word_text(f)
                council_text+=t+"\n"
            elif low.endswith(".txt"):
                t=read_txt_text(f)
                other_text+=t+"\n"
    except:
        pass

    full_corpus=council_text+"\n"+other_text
    members=extract_council_members(council_text if council_text.strip()!="" else full_corpus)

    q_low=user_query.lower()
    ans=""

    # بحث ذكي في أعضاء المجلس فقط
    if any(k in q_low for k in ["عميد","وكيل","رئيس","جودة","شؤون الطلبة","مجلس"]):
        q_keywords=[k for k in ["عميد","وكيل","الاكاديمية","الاكاديمي","شؤون الطلبة","الجودة","التطوير","القبول","رئيس قسم"] if k in q_low]
        if not q_keywords:
            q_keywords=re.findall(r'[\w\u0600-\u06FF]+', q_low)

        for m in members:
            ml=m.lower()
            if any(kw in ml for kw in q_keywords):
                ans=m
                break
        # لو سأل "من هو عميد الكلية" وما لقينا بالكلمات، خذ أول واحد فيه عميد
        if not ans and "عميد" in q_low:
            for m in members:
                if "عميد" in m:
                    ans=m
                    break

    if not ans:
        try:
            from google import genai
            from google.genai import types
            API_KEY=st.secrets["GEMINI_API_KEY"]
            client=genai.Client(api_key=API_KEY)
            parts=pdf_parts[:6]
            prompt=f"السؤال: {user_query}\n\nنص مجلس الكلية:\n{council_text[:8000]}\n\nنص باقي اللوائح:\n{other_text[:8000]}\n\nتعليمات: اجب باختصار من نص مجلس الكلية فقط اذا السؤال عن منصب. بدون ذكر اسم لائحة. اذا غير موجود: {OUT_MSG}"
            parts.append(types.Part.from_text(text=prompt))
            r=client.models.generate_content(model="gemini-1.5-flash", contents=[types.Content(role="user", parts=parts)], config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=400))
            ans=r.text.strip() if r and r.text else OUT_MSG
        except:
            ans=OUT_MSG

        # لو Gemini رجع كلام طويل من اللوائح وليس اسم، ارجع للبحث المحلي
        if len(ans)>150 or "التحقيق" in ans or "التوصيات" in ans:
            if members:
                # ابحث مرة أخرى
                for m in members:
                    if any(k in m.lower() for k in q_low.split()):
                        ans=m
                        break
                if len(ans)>150:
                    ans=members[0] if members else OUT_MSG
            else:
                ans=OUT_MSG

    if not ans: ans=OUT_MSG
    st.markdown("<div class='answer-box'>"+ans+"</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank'>{LINK}</a></div>", unsafe_allow_html=True)
