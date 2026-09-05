import os, streamlit as st
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

if btn and user_query:
    ans=OUT_MSG
    try:
        from google import genai
        from google.genai import types
        client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        parts=[]
        # أرسل كل ملفات PDF كصور ليقرأها Gemini حتى لو كانت صورة
        for f in os.listdir("."):
            if f.lower().endswith(".pdf"):
                try:
                    with open(f,"rb") as file:
                        parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                except: pass
            elif f.lower().endswith((".xlsx",".xls")):
                try:
                    import pandas as pd
                    xls=pd.ExcelFile(f)
                    txt=""
                    for sh in xls.sheet_names:
                        df=xls.parse(sh,dtype=str).fillna("")
                        for _,row in df.iterrows():
                            line=" | ".join([str(v) for v in row.values if str(v).strip()!=""])
                            if line: txt+=line+"\n"
                    if txt.strip():
                        parts.append(types.Part.from_text(text=f"ملف {f}:\n{txt[:8000]}"))
                except: pass

        q_low=user_query.lower()
        instr=""
        if "ايميل" in q_low or "إيميل" in q_low or "بريد" in q_low:
            instr="للايميل: ابحث عن السطر الذي يحتوي الاسم كاملا (مثلا احمد حسين يجب ان يحتوي على احمد وحسين) + ايميله. ممنوع ترجع اسم فيه احمد فقط اذا المطلوب احمد حسين. "
        elif "عذر" in q_low or "وفاة" in q_low or "ولادة" in q_low:
            instr="للأعذار: ابحث فقط في ملف ضوابط الأعذار الطلابية. اذكر المدة المسموح بها فقط (مثلا 3 ايام). "
        elif "عميد" in q_low or "وكيل" in q_low:
            instr="للمناصب: ابحث فقط في ملف مجلس الكلية. "

        prompt=f"""{instr}
قواعد: ممنوع ذكر اسم ملف او لائحة. إجابة مختصرة جدا ومباشرة. من اليمين لليسار.
اذا غير موجود قل: {OUT_MSG}

السؤال: {user_query}
"""
        parts.append(types.Part.from_text(text=prompt))

        r=client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=400)
        )
        if r.text and r.text.strip():
            ans=r.text.strip()
            # حماية من الخطأ السابق
            if "احمد حسين" in q_low and "akandil" in ans.lower():
                ans=OUT_MSG
    except Exception as e:
        ans=OUT_MSG

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
