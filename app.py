import os
import streamlit as st

st.set_page_config(page_title="Vision Colleges", layout="centered")

css_code = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"], p, div, h1, h2, h3 {
    direction: rtl!important;
    text-align: right!important;
    font-family: 'Tajawal', sans-serif!important;
}
div[data-testid="stImage"] { display: flex; justify-content: center; }
div[data-testid="stButton"] > button {
    background-color: #c5a880!important;
    color: white!important;
    border-radius: 12px!important;
    width: 100%!important;
    font-weight: bold!important;
}
.answer-box {
    background-color: #eaf7f0;
    padding: 20px;
    border-radius: 12px;
    line-height: 2.1;
    border: 1px solid #c3e6cb;
    font-size: 17px;
    white-space: pre-wrap;
}
.disclaimer-box {
    background-color: #fef9e7;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #f5d78e;
    margin-top: 20px;
    line-height: 1.9;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

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

def find_best_pdfs(query, max_files=5):
    pdfs = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
    if not pdfs:
        return []
    q = query.lower()
    scored = []
    for pdf in pdfs:
        name = pdf.lower()
        score = 0
        if "وفاة" in q or "وفاه" in q or "عذر" in q:
            if "عذر" in name or "اعذار" in name:
                score += 100
        if "ولادة" in q or "ولاده" in q:
            if "عذر" in name or "اعذار" in name:
                score += 100
        if "تظلم" in q:
            if "تظلم" in name or "لائحة" in name:
                score += 100
        if "مجلس" in q and "طلابي" in q:
            if "مجلس" in name:
                score += 100
        if "نشاط" in q:
            if "الانشطة" in name or "نشاط" in name:
                score += 100
        if "تقويم" in q:
            if "تقويم" in name:
                score += 100
        if "اختبار" in q:
            if "الاختبارات" in name or "قواعد" in name:
                score += 80
        if "لائحة" in name:
            score += 10
        scored.append((score, pdf))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored[0][0] == 0:
        return pdfs[:max_files]
    top = [p for s,p in scored[:max_files]]
    return top

if btn and user_query:
    best_pdfs = find_best_pdfs(user_query)
    ans = ""
    try:
        from google import genai
        from google.genai import types
        API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=API_KEY)
        try:
            available_models = list(client.models.list())
            flash_models = [m.name.replace("models/","") for m in available_models if "flash" in m.name.lower()]
        except:
            flash_models = []
        preferred = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.5-flash-8b"]
        all_to_try = flash_models + [m for m in preferred if m not in flash_models]
        seen = []
        uniq = []
        for m in all_to_try:
            if m not in seen:
                seen.append(m)
                uniq.append(m)
        all_to_try = uniq
        parts = []
        for pdf_file in best_pdfs:
            try:
                with open(pdf_file, "rb") as f:
                    pdf_bytes = f.read()
                parts.append(types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))
            except:
                pass
        prompt = f"""
انت مساعد اكاديمي ذكي وشامل في كليات الرؤية بالرياض. امامك {len(best_pdfs)} ملفات لوائح مرفقة.
السؤال الحالي من الطالب هو: "{user_query}"
تعليماتك:
1. اقرأ جميع الملفات المرفقة بعناية وابحث عن الفقرة التي تجيب على السؤال مباشرة.
2. اذا كان السؤال عن:
   - "عذر الوفاة": فقرة (ت) حالات الوفاة: المدة 5 أيام إجازة، تقديم ما يثبت خلال أسبوع عمل، الأقارب من الدرجة الأولى فقط.
   - "عذر الولادة": فقرة (ث) حالات الولادة (للطالبات): المدة أسبوع واحد فقط من تاريخ الولادة، تقديم شهادة ميلاد المولود، كشف طبي، أو شهادة ميلاد خلال عذرة أيام عمل.
   - "التظلمات": ابحث في لائحة التظلمات.
   - "المجلس الطلابي": ابحث في ملف شروط قائمة العميد او لائحة المجلس.
3. لا تقول "غير متوفر" اذا كان النص موجود في الملفات. اذكر النص كما هو مع التوضيح.
4. اجب بالعربية الفصحى الواضحة في نقاط مرتبة.
"""
        parts.append(types.Part.from_text(text=prompt))
        for model_name in all_to_try:
            try:
                r = client.models.generate_content(
                    model=model_name,
                    contents=[types.Content(role="user", parts=parts)]
                )
                if r and r.text and len(r.text.strip()) > 20:
                    ans = r.text
                    break
            except:
                continue
        if not ans:
            ans = "عذرا، لم اتمكن من قراءة اللوائح المرفقة حاليا."
    except Exception as e:
        ans = f"خطأ في الاتصال: {str(e)[:600]}"
    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    disc = "<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>"
    st.markdown(disc, unsafe_allow_html=True)
