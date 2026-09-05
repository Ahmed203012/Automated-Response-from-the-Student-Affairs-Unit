import os, streamlit as st
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

q=st.text_input(" ", placeholder="مثال: الوفاة")
btn=st.button("اضغط هنا للحصول على الإجابة")

LINK="https://elearning.vision.edu.sa/course/view.php?id=188"
OUT="هذه المعلومة غير متوفرة حاليا في اللوائح المعتمدة لدينا يرجى مراجعة وحدة شؤون الطلبة."
TANWIH=f"تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='{LINK}' target='_blank' style='direction:ltr; display:inline-block;'>{LINK}</a>"

def read_all_txt():
    full=""
    logs=[]
    for fname in os.listdir("."):
        low=fname.lower()
        if low.endswith(".txt"):  # هذا يضمن قراءة كل ملفات text
            for enc in ["utf-8","utf-8-sig","windows-1256","cp1256"]:
                try:
                    with open(fname,"r",encoding=enc,errors="ignore") as f:
                        t=f.read()
                        if len(t.strip())>20:
                            full+=t+"\n"
                            logs.append(f"{fname} -> {len(t)} حرف")
                            break
                except: pass
    return full, logs

if btn and q:
    full_text, logs = read_all_txt()
    
    # اعرض ما قرأه للتأكد
    st.sidebar.write("الملفات المقروءة:")
    for l in logs: st.sidebar.write(l)
    
    ql=q.strip()
    ans=OUT
    
    # ابحث عن كلمة الوفاة أو الولادة بأي شكل
    search_key=""
    if "وفاة" in ql or "وفاه" in ql or "الوفاة" in ql:
        search_key="وفا"  # يمسك وفاة و وفاه و الوفاة
    elif "ولادة" in ql or "ولاده" in ql:
        search_key="ولاد"
    elif "زواج" in ql:
        search_key="زواج"
    
    if search_key and search_key in full_text:
        idx=full_text.find(search_key)
        # خذ 700 حرف حول الكلمة حتى لو لم يجد كلمة يوم
        start=max(0, idx-150)
        end=min(len(full_text), idx+600)
        snippet=full_text[start:end].strip()
        # نظف
        snippet=snippet.replace("\n\n","\n").strip()
        if len(snippet)>15:
            ans=snippet[:600]
            st.sidebar.write("وجدت الفقرة:")
            st.sidebar.write(snippet[:500])
    else:
        st.sidebar.error(f"لم أجد كلمة {search_key} في النص")
        st.sidebar.write(full_text[:2000])

    st.markdown(f"<div class='answer-box' dir='rtl'>{ans}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='disclaimer-box' dir='rtl'>{TANWIH}</div>", unsafe_allow_html=True)
