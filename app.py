import os
import streamlit as st
import pdfplumber
from google import genai

st.set_page_config(page_title="Vision Colleges", layout="centered")

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

@st.cache_data
def load_data():
    chunks = []
    for fname in os.listdir("."):
        if fname.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(fname) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
                        if t and len(t.strip()) > 30:
                            chunks.append(t)
            except:
                pass
    return chunks

ALL_CHUNKS = load_data()

def get_context(q):
    q2 = q.replace("ة","ه")
    found = []
    for ch in ALL_CHUNKS:
        if any(w in ch for w in q2.split() if len(w) > 2):
            found.append(ch)
            if len(found) >= 2:
                break
    if not found:
        found = ALL_CHUNKS[:2]
    txt = ""
    for f in found:
        txt = txt + "\n" + f
    return txt[:6000]

if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
elif os.path.exists("Logo.png"):
    st.image("Logo.png", width=150)

st.title("Vision Colleges - كليات الرؤية")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
st.write("مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وانظمة الكلية، يمكنكم طرح اي سؤال وسيتم الرد عليكم مباشرة من واقع اللوائح المعتمدة.")

user_query = st.text_input(" ", placeholder="اكتب سؤالك هنا")
btn = st.button("اضغط هنا للحصول على الاجابة")

LINK = "https://elearning.vision.edu.sa/course/view.php?id=188"

if btn and user_query:
    ctx = get_context(user_query)
    ans = ""
    try:
        prompt = "اجب فقط من هذه اللوائح. اذا غير موجود قل غير موجود. اللوائح: " + ctx + " السؤال: " + user_query
        r = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        ans = r.text
    except:
        ans = "من واقع اللوائح: " + ctx[:1500]
    if not ans:
        ans = "عذرا، هذه المعلومة غير متوفرة في اللوائح."
    st.success(ans)
    st.warning("تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية: " + LINK)
    st.markdown(LINK)
