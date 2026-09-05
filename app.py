import os, re, streamlit as st
st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; }
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
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank'>{LINK}</a>"

def read_all_excuse():
    text=""
    logs=[]
    for f in os.listdir("."):
        low=f.lower()
        if "عذر" in f or "excuse" in low or "ضوابط" in f or f.lower().endswith(".docx"):
            if low.endswith(".docx"):
                try:
                    import docx
                    t="\n".join([p.text for p in docx.Document(f).paragraphs if p.text.strip()!=""])
                    text+=t+"\n"
                    logs.append(f"{f} -> {len(t)} حرف")
                except: pass
            elif low.endswith(".pdf"):
                try:
                    import fitz
                    t="\n".join([p.get_text() for p in fitz.open(f)])
                    text+=t+"\n"
                    logs.append(f"{f} -> {len(t)} حرف")
                except: pass
            elif low.endswith(".txt"):
                try:
                    with open(f,"r",encoding="utf-8",errors="ignore") as file:
                        t=file.read()
                        text+=t+"\n"
                        logs.append(f"{f} -> {len(t)} حرف")
                except: pass
    return text, logs

def find_duration_smart(query, full_text):
    ql=query.lower()
    target=""
    if "ولادة" in ql or "وضع" in ql: target="الولاد"
    elif "وفاة" in ql: target="الوفاة"
    elif "زواج" in ql: target="الزواج"
    elif "مرض" in ql: target="المرض"
    
    if not target: return ""

    # ابحث بفقرة كاملة: الولادة + حتى 300 حرف + يوم
    pattern = rf"{target}[^\n]{{0,300}}?(?:\d+|ثلاثة|أربعة|خمسة|ستة|سبعة|ثلاث|يومين|ثلاثة أيام).*?(?:يوم|أيام|ساعة)"
    m=re.search(pattern, full_text, re.IGNORECASE|re.DOTALL)
    if m:
        # نظف النتيجة
        res=m.group(0).strip()
        if len(res)>400: res=res[:400]
        return res

    # بحث ثاني: السطر + السطر اللي بعده
    lines=full_text.splitlines()
    for i,line in enumerate(lines):
        if target in line:
            combined=line
            if i+1<len(lines): combined+=" "+lines[i+1]
            if i+2<len(lines): combined+=" "+lines[i+2]
            if any(k in combined for k in ["يوم","أيام","ساعة"]):
                if len(combined)<500:
                    return combined.strip()
    return ""

if btn and q:
    full_text, logs = read_all_excuse()
    
    st.sidebar.write("الملفات المقروءة:")
    for l in logs: st.sidebar.write(l)
    st.sidebar.write(f"الإجمالي: {len(full_text)} حرف")

    ans=find_duration_smart(q, full_text)

    if ans=="":
        # لو البحث الذكي فشل، استخدم Gemini بالنص الكامل
        try:
            from google import genai
            client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            prompt=f"استخرج فقط مدة تقديم عذر الولادة أو الوفاة من النص التالي باختصار. بدون ذكر اسم ملف.\nالسؤال: {q}\nالنص:\n{full_text[:15000]}\nاذا غير موجود قل {OUT}"
            r=client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            if r.text and len(r.text.strip())>3:
                ans=r.text.strip()
        except Exception as e:
            st.sidebar.write(f"Gemini error: {e}")

    if ans=="": ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
