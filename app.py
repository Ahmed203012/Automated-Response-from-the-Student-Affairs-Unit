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

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
if os.path.exists("logo.png"):
st.image("logo.png", width=120)
elif os.path.exists("Logo.png"):
st.image("Logo.png", width=120)

st.markdown("<h1 style='text-align:center;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:right;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الإجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"
OUT_MSG = "هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."

def find_best_pdfs(query, max_files=4):
pdfs = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
if not pdfs:
return []
q = query.lower()
scored = []
for pdf in pdfs:
name = pdf.lower()
score = 0
if any(k in q for k in ["عذر","غياب","حرمان","وفاة","ولادة","مرض"]):
if "عذر" in name:
score += 100
if "تظلم" in q and "تظلم" in name:
score += 100
if "اختبار" in q and ("اختبار" in name or "قواعد" in name):
score += 80
scored.append((score, pdf))
scored.sort(key=lambda x: x[0], reverse=True)
if scored and scored[0][0] == 0:
return pdfs[:max_files]
return [p for s, p in scored[:max_files]]

if btn and user_query:
best_pdfs = find_best_pdfs(user_query)
try:
from google import genai
from google.genai import types
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)
parts = []
for pdf_file in best_pdfs:
try:
with open(pdf_file, "rb") as f:
parts.append(types.Part.from_bytes(data=f.read(), mime_type="application/pdf"))
except:
pass

prompt_text = (
"انت مساعد شؤون الطلبة في كليات الرؤية.\n"
f"السؤال: {user_query}\n"
"التعليمات:\n"
f"1- اذا السؤال خارج اللوائح المرفقة، اجب فقط بهذه الجملة: {OUT_MSG}\n"
"2- ممنوع تذكر اسم اللائحة او رقم المادة. اذكر المعلومة فقط.\n"
"3- الاجابة مختصرة جدا على قد السؤال بدون شرح طويل.\n"
"4- لا تغير الارقام (ثلاثة ايام عمل، 75%، 50%).\n"
)
parts.append(types.Part.from_text(text=prompt_text))

r = client.models.generate_content(
model="gemini-2.0-flash",
contents=[types.Content(role="user", parts=parts)],
config=types.GenerateContentConfig(temperature=0.0, top_p=0.1, max_output_tokens=300)
)
ans = r.text.strip() if r and r.text else OUT_MSG
except:
ans = OUT_MSG

st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
st.markdown("<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>", unsafe_allow_html=True)

