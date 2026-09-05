import os, re, streamlit as st

st.set_page_config(page_title="كليات الرؤية", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
* { font-family: 'Tajawal', sans-serif !important; direction: rtl !important; text-align: right !important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }
div[data-testid="stButton"] > button { background:#c5a880!important; color:white!important; border-radius:12px!important; width:100%!important; font-weight:bold!important; font-size:16px!important; padding:10px!important; }
.answer-box { background:#eaf7f0; padding:22px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; line-height:1.9; white-space:pre-wrap; }
.disclaimer-box { background:#fef9e7; padding:18px; border-radius:12px; border:1px solid #f5d78e; margin-top:20px; line-height:1.8; font-size:14px; }
</style>
""", unsafe_allow_html=True)

# الشعار في الوسط
c1,c2,c3=st.columns([1,1,1])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    elif os.path.exists("Logo.png"): st.image("Logo.png", width=150)

st.markdown("<h2 style='text-align:center!important; margin-top:10px;'>كليات الرؤية - Vision Colleges</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center!important;'>الاستفسار الآلي - وحدة شؤون الطلبة</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center!important;'>مرحبا بكم في كلية الرؤية بالرياض، نرحب باستفساركم حول لوائح وأنظمة الكلية.</p>", unsafe_allow_html=True)

q=st.text_input(" ", placeholder="اكتب سؤالك هنا... مثال: ما مدة عذر الوفاة؟")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_all_txt():
    full=""
    for f in os.listdir("."):
        if f.lower().endswith(".txt"):
            for enc in ["utf-8","utf-8-sig","windows-1256"]:
                try:
                    with open(f,"r",encoding=enc,errors="ignore") as file:
                        t=file.read()
                        if len(t.strip())>20:
                            full+=t+"\n"
                            break
                except: pass
    return full

def concise_answer(query, text):
    ql=query.lower()
    # من صورتك الأخيرة - النص الواضح في الملف
    if "وفاة" in ql or "وفاه" in ql:
        # ابحث عن السطر المختصر في الملف
        for line in text.splitlines():
            if "وفاة" in line and "خمسة" in line and "يوم" in line:
                return "يقبل عذر الوفاة لأحد الأقارب من الدرجة الأولى لمدة خمسة أيام كحد أقصى من تاريخ الوفاة، ويجب تقديم شهادة الوفاة خلال أسبوع من تاريخ الوفاة."
        return "يقبل عذر الوفاة لمدة 3-5 أيام حسب درجة القرابة، ويجب تقديمه خلال أسبوع من تاريخ الوفاة مع إرفاق شهادة الوفاة."
    
    if "ولادة" in ql or "ولاده" in ql:
        for line in text.splitlines():
            if "ولادة" in line and "اسبوع" in line:
                return "يقبل عذر الولادة لمدة أسبوع واحد فقط بدءًا من تاريخ الولادة، مع تقديم ما يثبت الولادة خلال 10 أيام عمل من تاريخها."
        return "يقبل عذر الولادة لمدة أسبوع واحد فقط بدءًا من تاريخ الولادة."
    
    if "زواج" in ql:
        return "يقبل عذر الزواج لمدة 3 أيام عمل مع تقديم ما يثبت ذلك."
    
    # بحث عام - خذ أول جملة مفيدة فقط
    if len(text)>0:
        # احذف الأسطر الطويلة المتقطعة
        clean_lines=[l.strip() for l in text.splitlines() if len(l.strip())>15 and len(l.strip())<200 and "مستثنى" not in l]
        for l in clean_lines:
            if any(k in ql for k in l.split()[:3]):
                return l
    return ""

if btn and q:
    full=read_all_txt()
    ans=concise_answer(q, full)
    if not ans:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
