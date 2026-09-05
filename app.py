import os, streamlit as st
st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; }
.answer-box { background:#eaf7f0; padding:20px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)

q=st.text_input(" ", placeholder="اكتب سؤالك هنا... مثال: الوفاة")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank'>{LINK}</a>"

# --- كاشف المشكلة ---
files=os.listdir(".")
st.sidebar.write("الملفات في السيرفر:", files)
found=False
for f in files:
    if "a3zar" in f.lower():
        found=True
        size=os.path.getsize(f)
        st.sidebar.write(f"وجدت ملف الأعذار: {f} حجمه {size} بايت")
        try:
            with open(f,"r",encoding="utf-8",errors="ignore") as file:
                preview=file.read()[:500]
                st.sidebar.write("أول 500 حرف:", preview)
        except Exception as e:
            st.sidebar.write("خطأ قراءة:", str(e))

if not found:
    st.sidebar.error("ملف a3zar.txt غير موجود في السيرفر! تأكد أنك رفعته بجانب app.py")

def read_all_a3zar():
    text=""
    for f in os.listdir("."):
        if "a3zar" in f.lower() or "عذر" in f or f.lower().endswith((".txt",".docx")):
            try:
                if f.lower().endswith(".docx"):
                    import docx
                    text+="\n".join([p.text for p in docx.Document(f).paragraphs])+"\n"
                elif f.lower().endswith(".pdf"):
                    import fitz
                    text+="\n".join([p.get_text() for p in fitz.open(f)])+"\n"
                else:
                    for enc in ["utf-8","utf-8-sig","windows-1256"]:
                        try:
                            with open(f,"r",encoding=enc,errors="ignore") as file:
                                t=file.read()
                                if len(t)>10:
                                    text+=t+"\n"
                                    break
                        except: pass
            except: pass
    return text

if btn and q:
    all_text=read_all_a3zar()
    ans=OUT
    ql=q.lower()
    # بحث محلي مباشر
    for line in all_text.splitlines():
        if "وفاة" in ql and "وفاة" in line and "يوم" in line and len(line)<300:
            ans=line.strip()
            break
        if "ولادة" in ql and "ولادة" in line and "يوم" in line and len(line)<300:
            ans=line.strip()
            break
        if "زواج" in ql and "زواج" in line and "يوم" in line:
            ans=line.strip()
            break

    if ans==OUT and all_text.strip()=="":
        ans="الملف غير مقروء - الشريط الجانبي يوضح المشكلة"
    elif ans==OUT:
        # جرب Gemini كمحاولة أخيرة
        try:
            from google import genai
            client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            prompt=f"السؤال: {q}\nالنص:\n{all_text[:10000]}\nأجب بالمدة فقط. اذا غير موجود قل {OUT}"
            r=client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            if r.text: ans=r.text.strip()
        except: pass

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#fef9e7; padding:15px; border-radius:12px; margin-top:15px;'>{TANWIH}</div>", unsafe_allow_html=True)
