import os, re, streamlit as st
st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; font-weight:bold!important; }
.answer-box { background:#eaf7f0; padding:20px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; white-space:pre-wrap; }
.disclaimer-box { background:#fef9e7; padding:18px; border-radius:12px; border:1px solid #f5d78e; margin-top:20px; line-height:1.8; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center!important;'>كليات الرؤية - Vision Colleges</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:right!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

q=st.text_input(" ", placeholder="مثال: ما المدة المسموح بها لتقديم عذر الولادة")
btn=st.button("اضغط هنا للحصول على الإجابة")
LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_docx_text(path):
    try:
        import docx
        doc=docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()!=""])
    except Exception as e:
        return f"خطأ قراءة docx {e}"

def read_pdf_text(path):
    try:
        import fitz
        return "\n".join([p.get_text() for p in fitz.open(path)])
    except:
        try:
            import PyPDF2
            return "\n".join([(p.extract_text() or "") for p in PyPDF2.PdfReader(path).pages])
        except: return ""

def get_all_excuse_text():
    text=""
    logs=[]
    for f in os.listdir("."):
        low=f.lower()
        # اقرأ أي ملف فيه كلمة عذر أو excuse
        if "عذر" in f or "excuse" in low or "ضوابط" in f:
            logs.append(f"أقرأ: {f}")
            if low.endswith(".docx"):
                text+=read_docx_text(f)+"\n"
            elif low.endswith(".pdf"):
                text+=read_pdf_text(f)+"\n"
            elif low.endswith(".txt"):
                try:
                    with open(f,"r",encoding="utf-8",errors="ignore") as file:
                        text+=file.read()+"\n"
                except: pass
    return text, logs

if btn and q:
    excuse_text, logs = get_all_excuse_text()
    
    # اعرض في الشريط الجانبي ماذا قرأ - لكي تتأكد
    st.sidebar.write("قرأ هذه الملفات:")
    for l in logs: st.sidebar.write(l)
    st.sidebar.write(f"طول النص المستخرج: {len(excuse_text)} حرف")
    if len(excuse_text)>0:
        st.sidebar.write(excuse_text[:1000])

    ans=OUT
    ql=q.lower()
    
    # 1- بحث محلي سريع
    target=""
    if "ولادة" in ql: target="ولادة"
    elif "وفاة" in ql: target="وفاة"
    elif "زواج" in ql: target="زواج"
    
    if target:
        for line in excuse_text.splitlines():
            if target in line and any(k in line for k in ["يوم","أيام","خلال","ساعة","ثلاثة","يومين"]):
                if len(line.strip())<400 and "مستثنى" not in line:
                    ans=line.strip()
                    break

    # 2- لو ما لقينا، استخدم Gemini لكن بالنص المقروء فقط
    if ans==OUT and len(excuse_text.strip())>20:
        try:
            from google import genai
            from google.genai import types
            client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            prompt=f"أنت مساعد شؤون الطلبة. أجب باختصار بالمدة المسموح بها فقط بدون ذكر اسم ملف. السؤال: {q}\nالنص:\n{excuse_text[:12000]}\nاذا غير موجود قل {OUT}"
            r=client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            if r.text: ans=r.text.strip()
        except Exception as e:
            st.sidebar.write(f"خطأ Gemini: {e}")

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
