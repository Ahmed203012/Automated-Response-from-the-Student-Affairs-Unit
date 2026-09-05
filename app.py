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
.answer-box {
    background-color: #eaf7f0; padding: 20px; border-radius: 12px;
    line-height: 1.6; border: 1px solid #c3e6cb; font-size: 17px; white-space: pre-wrap;
}
.disclaimer-box {
    background-color: #fef9e7; padding: 18px; border-radius: 12px;
    border: 1px solid #f5d78e; margin-top: 20px; line-height: 1.6;
}
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

# --- دوال قراءة الأربع أنواع ---
def read_excel_text(path):
    try:
        import pandas as pd
        xls = pd.ExcelFile(path)
        txt = ""
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            txt += f"\n[ملف {os.path.basename(path)} - {sheet}]\n"
            txt += df.to_string(index=False) + "\n"
        return txt
    except Exception as e:
        return f"[خطأ قراءة اكسل {path}: {e}]"

def read_word_text(path):
    try:
        import docx
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        return ""

def read_txt_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        try:
            with open(path, "r", encoding="windows-1256", errors="ignore") as f:
                return f.read()
        except:
            return ""

def find_best_files(query, max_files=6):
    all_files = [f for f in os.listdir(".") if f.lower().endswith((".pdf",".xlsx",".xls",".docx",".doc",".txt"))]
    if not all_files:
        return []
    q = query.lower()
    scored = []
    for fname in all_files:
        name = fname.lower()
        score = 0
        # عميد ومجلس
        if any(k in q for k in ["عميد","مجلس","وكيل","رئيس قسم","الدهشم"]):
            if "مجلس" in name:
                score += 150
        # اعذار
        if any(k in q for k in ["عذر","غياب","حرمان","وفاة","ولادة"]):
            if "عذر" in name:
                score += 100
        if "تظلم" in q and "تظلم" in name:
            score += 100
        if "اختبار" in q and ("اختبار" in name or "قواعد" in name):
            score += 80
        if score == 0:
            score = 5
        scored.append((score, fname))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for s, p in scored[:max_files]]

if btn and user_query:
    best_files = find_best_files(user_query)
    try:
        from google import genai
        from google.genai import types
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)
        parts = []
        combined_text = ""

        for f in best_files:
            low = f.lower()
            if low.endswith(".pdf"):
                try:
                    with open(f, "rb") as file:
                        parts.append(types.Part.from_bytes(data=file.read(), mime_type="application/pdf"))
                except:
                    pass
            elif low.endswith((".xlsx",".xls")):
                combined_text += "\n" + read_excel_text(f) + "\n"
            elif low.endswith((".docx",".doc")):
                combined_text += f"\n[ملف وورد {f}]\n" + read_word_text(f) + "\n"
            elif low.endswith(".txt"):
                combined_text += f"\n[ملف نصي {f}]\n" + read_txt_text(f) + "\n"

        prompt_text = "انت مساعد شؤون الطلبة في كليات الرؤية.\n"
        prompt_text += f"السؤال: {user_query}\n"
        if combined_text:
            prompt_text += f"\nالبيانات المستخرجة من ملفات الاكسل والوورد والنصوص:\n{combined_text[:12000]}\n"
        prompt_text += "\nالتعليمات الصارمة:\n"
        prompt_text += f"1- اذا السؤال خارج الملفات المرفقة (PDF/Excel/Word/Txt)، اجب فقط: {OUT_MSG}\n"
        prompt_text += "2- ممنوع تذكر اسم اللائحة او رقم المادة. اذكر المعلومة فقط.\n"
        prompt_text += "3- الاجابة مختصرة جدا على قد السؤال.\n"
        prompt_text += "4- لا تغير الارقام.\n"

        parts.append(types.Part.from_text(text=prompt_text))

        r = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(temperature=0.0, top_p=0.1, max_output_tokens=500)
        )
        ans = r.text.strip() if r and r.text else OUT_MSG
    except Exception as e:
        ans = OUT_MSG

    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>", unsafe_allow_html=True)
