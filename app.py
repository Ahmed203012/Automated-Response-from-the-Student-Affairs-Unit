import os
import streamlit as st

st.set_page_config(page_title="Vision Colleges", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], p, div, h1, h2, h3 {
    direction: rtl!important; text-align: right!important;
    font-family: 'Tajawal', sans-serif!important;
}
div[data-testid="stImage"] { display: flex; justify-content: center; }
div[data-testid="stButton"] > button {
    background-color: #c5a880!important; color: white!important;
    border-radius: 12px!important; width: 100%!important; font-weight: bold!important;
}
.answer-box { background-color: #eaf7f0; padding: 20px; border-radius: 12px; line-height: 1.6; border: 1px solid #c3e6cb; font-size: 17px; white-space: pre-wrap; }
.disclaimer-box { background-color: #fef9e7; padding: 18px; border-radius: 12px; border: 1px solid #f5d78e; margin-top: 20px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([2,1,2])
with c2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", width=120)
    else:
        st.write("")

st.markdown("<h1 style='text-align:center;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"
OUT_MSG = "هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."

def read_excel_text(path):
    try:
        import pandas as pd
        xls = pd.ExcelFile(path)
        txt = ""
        for sheet in xls.sheet_names:
            df = xls.parse(sheet, dtype=str).fillna("")
            txt += f"\n[{os.path.basename(path)}]\n"
            for _, row in df.iterrows():
                line = " | ".join([str(v).strip() for v in row.values if str(v).strip()!=""])
                if line:
                    txt += line + "\n"
        return txt
    except:
        return ""

def read_word_text(path):
    try:
        import docx
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        return ""

def read_txt_text(path):
    for enc in ["utf-8","windows-1256"]:
        try:
            with open(path,"r",encoding=enc,errors="ignore") as f:
                return f.read()
        except:
            pass
    return ""

if btn and user_query:
    try:
        from google import genai
        from google.genai import types
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)

        all_files = [f for f in os.listdir(".") if f.lower().endswith((".pdf",".xlsx",".xls",".docx",".txt"))]
        q_low = user_query.lower()
        is_dean = any(k in q_low for k in ["عميد","مجلس","الدهشم"])

        # ترتيب الملفات: مجلس الكلية أولاً إذا السؤال عن العميد
        if is_dean:
            pri = [f for f in all_files if "مجلس" in f]
            rest = [f for f in all_files if "مجلس" not in f]
            all_files = pri + rest

        parts = []
        combined = ""
        for f in all_files[:8]:
            low = f.lower()
            if low.endswith(".pdf"):
                try:
                    with open(f,"rb") as file:
                        parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                except:
                    pass
            elif low.endswith((".xlsx",".xls")):
                combined += read_excel_text(f)
            elif low.endswith(".docx"):
                combined += read_word_text(f)
            elif low.endswith(".txt"):
                combined += read_txt_text(f)

        combined += "\nبيانات مؤكدة: عميد كلية الرؤية بالرياض هو أ.د. عبد الله بن محمد الدهمش\n"

        prompt = f"السؤال: {user_query}\n\n"
        prompt += f"البيانات من الملفات:\n{combined[:15000]}\n\n"
        prompt += f"تعليمات: 1- اذا السؤال عن العميد اجب: أ.د. عبد الله بن محمد الدهمش - عميد كلية الرؤية بالرياض\n"
        prompt += f"2- اذا موجود في الملفات اجب باختصار بدون ذكر اسم لائحة او مادة\n"
        prompt += f"3- اذا غير موجود اجب فقط: {OUT_MSG}\n"

        parts.append(types.Part.from_text(text=prompt))

        # تم تغيير الموديل من 2.0 الى 1.5-flash لأنه 2.0 توقف
        r = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=400)
        )
        ans = r.text.strip() if r and r.text else OUT_MSG

    except Exception as e:
        # لو حصل خطأ لا تظهر تفاصيل الـ error للطالب
        if "404" in str(e) or "not found" in str(e).lower():
            ans = OUT_MSG
        else:
            ans = OUT_MSG

    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank'>{LINK}</a></div>", unsafe_allow_html=True)
