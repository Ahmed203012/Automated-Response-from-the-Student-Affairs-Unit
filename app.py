import os, streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; }
.answer-box { background:#eaf7f0; padding:20px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; direction:rtl!important; text-align:right!important; }
</style>
""", unsafe_allow_html=True)

c1,c2,c3=st.columns([1,1,1])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", width=130)

st.markdown("<h1 style='text-align:center!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:right!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

q=st.text_input(" ", placeholder="اكتب سؤالك هنا...")
btn=st.button("اضغط هنا للحصول على الإجابة")
LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."

if btn and q:
    ql=q.lower()
    # قراءة سريعة بدون ما يعلق
    ans=OUT
    try:
        import pandas as pd
        for f in os.listdir("."):
            if "مجلس" in f and f.lower().endswith((".xlsx",".xls")) and any(k in ql for k in ["عميد","وكيل","رئيس"]):
                df=pd.read_excel(f, dtype=str).fillna("")
                for _,row in df.iterrows():
                    line=" | ".join([str(v) for v in row.values if str(v).strip()!=""])
                    if "عميد" in ql and "عميد" in line: ans=line; break
                    if "وكيل" in ql and "وكيل" in line: ans=line; break
    except: pass
    
    if ans==OUT:
        # لو ما لقينا في الاكسل، جرب Gemini بسرعة
        try:
            from google import genai
            from google.genai import types
            client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            txt=""
            for f in os.listdir(".")[:5]:
                if f.lower().endswith(".pdf"):
                    try:
                        import fitz
                        txt+=fitz.open(f).get_text()[:4000]
                    except: pass
            prompt=f"السؤال:{q}\nالنص:{txt[:8000]}\nأجب باختصار بدون ذكر اسم ملف. اذا غير موجود قل: {OUT}"
            r=client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            if r.text: ans=r.text.strip()
        except: ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#fef9e7; padding:15px; border-radius:12px; margin-top:15px; direction:rtl; text-align:right;'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات غير دقيقة، والمرجع الرسمي هو:<br><a href='{LINK}' target='_blank'>{LINK}</a></div>", unsafe_allow_html=True)
