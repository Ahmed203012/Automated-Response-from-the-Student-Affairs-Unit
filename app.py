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
    text = ""
    try:
        import pandas as pd
        xls = pd.ExcelFile(path)
        for sheet in xls.sheet_names:
            df = xls.parse(sheet, dtype=str)
            df = df.fillna("")
            text += f"\n--- {os.path.basename(path)} - {sheet} ---\n"
            for _, row in df.iterrows():
                row_text = " | ".join([str(v) for v in row.values if str(v).strip()!=""])
                if row_text.strip():
                    text += row_text + "\n"
    except Exception as e:
        text += f" [خطأ قراءة {path}: {e}] "
    return text

def read_word_text(path):
    try:
        import docx
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()!=""])
    except:
        return ""

def read_txt_text(path):
    for enc in ["utf-8","windows-1256","cp1256"]:
        try:
            with open(path,"r",encoding=enc,errors="ignore") as f:
                return f.read()
        except:
            pass
    return ""

def get_all_files():
    exts = (".pdf",".xlsx",".xls",".docx",".txt")
    return [f for f in os.listdir(".") if f.lower().endswith(exts)]

if btn and user_query:
    all_files = get_all_files()
    q_low = user_query.lower()
    is_dean_query = any(k in q_low for k in ["عميد","مجلس","الدهشم","دهمش"])
    
    try:
        from google import genai
        from google.genai import types
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)
        parts = []
        combined_text = ""

        # لو سؤال عن العميد: اقرأ كل ملفات المجلس والاكسل أولاً
        files_to_send = all_files
        if is_dean_query:
            priority = [f for f in all_files if "مجلس" in f]
            others = [f for f in all_files if "مجلس" not in f]
            files_to_send = priority + others

        for f in files_to_send[:8]:
            low = f.lower()
            if low.endswith(".pdf"):
                try:
                    with open(f,"rb") as file:
                        parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                except:
                    pass
            elif low.endswith((".xlsx",".xls")):
                combined_text += read_excel_text(f) + "\n"
            elif low.endswith(".docx"):
                combined_text += f"\n[{f}]\n" + read_word_text(f) + "\n"
            elif low.endswith(".txt"):
                combined_text += f"\n[{f}]\n" + read_txt_text(f) + "\n"

        # نص إضافي ثابت من ملفك لضمان الجواب حتى لو فشلت قراءة الإكسل
        combined_text += "\n مجلس كلية الرؤية بالرياض: أ.د. عبد الله بن محمد الدهمش - عميد كلية الرؤية بالرياض | د. نهال بنت أحمد المريخي - وكيل الكلية للشؤون الأكاديمية \n"

        prompt_text = f"السؤال: {user_query}\n\n"
        prompt_text += f"البيانات من ملفات الكلية (PDF/Excel/Word/Txt):\n{combined_text[:15000]}\n\n"
        prompt_text += f"تعليمات:\n"
        prompt_text += f"1- إذا السؤال عن عميد الكلية، أجب: أ.د. عبد الله بن محمد الدهمش هو عميد كلية الرؤية بالرياض\n"
        prompt_text += f"2- إذا السؤال موجود في البيانات أعلاه أجب باختصار بدون ذكر اسم لائحة أو مادة\n"
        prompt_text += f"3- إذا غير موجود، أجب فقط: {OUT_MSG}\n"

        parts.append(types.Part.from_text(text=prompt_text))

        r = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=500)
        )
        ans = r.text.strip() if r and r.text else OUT_MSG
    except Exception as e:
        ans = f"{OUT_MSG} - تفاصيل: {str(e)[:200]}"

    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank'>{LINK}</a></div>", unsafe_allow_html=True)
    
    # للتشخيص فقط - يظهر الملفات التي قرأها
    with st.expander("الملفات التي تمت قراءتها"):
        st.write(all_files)
