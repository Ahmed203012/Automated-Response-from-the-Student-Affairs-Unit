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

q=st.text_input(" ", placeholder="مثال: ما الفترة المسموح بها لتقديم عذر الوفاة")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_all_txt():
    full=""
    logs=[]
    for fname in os.listdir("."):
        low=fname.lower()
        # هذا الشرط يضمن قراءة كل ملفات .txt مهما كان اسمها
        if low.endswith(".txt"):
            try:
                # جرب كل الترميزات العربية
                for enc in ["utf-8","utf-8-sig","windows-1256","cp1256"]:
                    try:
                        with open(fname,"r",encoding=enc,errors="ignore") as f:
                            t=f.read()
                            if len(t.strip())>20:
                                full+=t+"\n"
                                logs.append(f"{fname} -> {len(t)} حرف")
                                break
                    except: pass
            except Exception as e:
                logs.append(f"{fname} خطأ {e}")
    return full, logs

def extract_duration(query, text):
    # حدد نوع العذر
    if "وفاة" in query: keys=["وفاة","الوفاة"]
    elif "ولادة" in query or "وضع" in query: keys=["ولادة","الولادة","الوضع"]
    elif "زواج" in query: keys=["زواج","الزواج"]
    else: keys=[]

    for k in keys:
        # ابحث عن الكلمة وخذ 800 حرف بعدها
        for m in re.finditer(k, text):
            idx=m.start()
            snippet=text[idx:idx+800]
            # نظف
            snippet_clean=snippet.replace("\r"," ").replace("\n"," ")
            # ابحث عن رقم + يوم داخل الفقرة
            dur=re.search(r"(\d+\s*(?:يوم|أيام|ساعة|ساعات)|ثلاثة أيام|ثلاثة|يومين|ثلاثة أيام عمل|خلال\s+\d+\s+أيام)", snippet_clean)
            if dur:
                # ارجع الفقرة كاملة حتى المدة
                return snippet[:snippet.find(dur.group(0))+len(dur.group(0))+100].strip()[:500]
            # لو ما وجد رقم، ارجع الفقرة نفسها
            if len(snippet.strip())>20:
                return snippet[:400].strip()
    return ""

if btn and q:
    full_text, logs = read_all_txt()
    
    # للتصحيح - يظهر في الشريط الجانبي
    st.sidebar.write("الملفات المقروءة:")
    for l in logs: st.sidebar.write(l)
    st.sidebar.write(f"إجمالي النص: {len(full_text)} حرف")
    
    ans=extract_duration(q, full_text)
    
    if not ans:
        # بحث احتياطي سطر بسطر
        for line in full_text.splitlines():
            if "وفاة" in q and "وفاة" in line and len(line.strip())>10:
                ans=line.strip()
                # أضف السطر التالي لأنه فيه المدة
                idx=full_text.splitlines().index(line)
                if idx+1 < len(full_text.splitlines()):
                    ans+=" "+full_text.splitlines()[idx+1].strip()
                break
            if "ولادة" in q and "ولادة" in line and len(line.strip())>10:
                ans=line.strip()
                idx=full_text.splitlines().index(line)
                if idx+1 < len(full_text.splitlines()):
                    ans+=" "+full_text.splitlines()[idx+1].strip()
                break

    if not ans or len(ans)<5:
        ans=OUT

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
