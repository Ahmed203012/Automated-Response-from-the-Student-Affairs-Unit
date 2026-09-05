import os, re, streamlit as st
st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; font-weight:bold!important; }
.answer-box { background:#eaf7f0; padding:20px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; white-space:pre-wrap; line-height:1.9; }
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

def read_all():
    text=""
    for f in os.listdir("."):
        low=f.lower()
        if "عذر" in f or "excuse" in low or "ضوابط" in f or low.endswith((".docx",".txt")):
            try:
                if low.endswith(".docx"):
                    import docx
                    t="\n".join([p.text for p in docx.Document(f).paragraphs if p.text.strip()!=""])
                    text+=t+"\n"
                elif low.endswith(".pdf"):
                    try:
                        import fitz
                        t="\n".join([p.get_text() for p in fitz.open(f)])
                    except:
                        import PyPDF2
                        t="\n".join([(p.extract_text() or "") for p in PyPDF2.PdfReader(f).pages])
                    text+=t+"\n"
                elif low.endswith(".txt"):
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

def extract_duration(query, full_text):
    ql=query.lower()
    if "ولادة" in ql or "وضع" in ql: keywords=["الولادة","الوضع","ولادة"]
    elif "وفاة" in ql: keywords=["الوفاة","وفاه","وفاة"]
    elif "زواج" in ql: keywords=["الزواج","زواج"]
    elif "مرض" in ql: keywords=["المرض","مرض"]
    else: keywords=[]
    
    if not keywords: return ""

    for kw in keywords:
        idx=full_text.find(kw)
        while idx!=-1:
            # خذ 600 حرف بعد كلمة الولادة
            snippet=full_text[idx:idx+600]
            # ابحث عن مدة
            m=re.search(r"(\d+|ثلاثة|أربعة|خمسة|ثلاث|يومين|ثلاثة أيام|خمسة أيام|30 يوم|3 أيام|5 أيام).*?(?:يوم|أيام|ساعة)", snippet)
            if m:
                # نظف الفقرة
                # خذ من بداية الجملة إلى نهاية المدة
                start=max(0, snippet.rfind("\n", 0, 50))
                end=snippet.find("\n", len(m.group(0))+50)
                if end==-1: end=len(snippet)
                res=snippet[start:end].strip()
                if len(res)>20 and len(res)<400:
                    return res
            idx=full_text.find(kw, idx+1)
    return ""

if btn and q:
    full=read_all()
    ans=extract_duration(q, full)
    if not ans:
        # بحث احتياطي: أي سطر فيه الولادة + يوم
        for line in full.splitlines():
            if "الولادة" in line and "يوم" in line and len(line)<400:
                ans=line.strip()
                break
            if "الوفاة" in line and "يوم" in line and len(line)<400:
                ans=line.strip()
                break
    if not ans:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
