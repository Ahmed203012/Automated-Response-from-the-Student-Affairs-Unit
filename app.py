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

def find_best_pdfs(query, max_files=3):
    pdfs = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]
    return pdfs[:max_files]

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
        preferred = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        all_to_try = flash_models + [m for m in preferred if m not in flash_models]
        parts = []
        for pdf_file in best_pdfs:
            try:
                with open(pdf_file, "rb") as f:
                    pdf_bytes = f.read()
                parts.append(types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))
            except:
                pass
        prompt = f"""
انت مساعد اكاديمي دقيق في كليات الرؤية بالرياض. اقرأ كل ملفات اللوائح المرفقة بعناية.
السؤال الحالي هو: "{user_query}"
تعليمات مهمة جدا:
1. اذا كان السؤال عن "عذر الوفاة" فلا تجب عن عذر الغياب عن الاختبار. عذر الوفاة له احكام خاصة: مدة الغياب المسموحة بسبب وفاة قريب (عادة 5 ايام)، ومدة تقديم العذر (عادة 7 ايام او 5 ايام)، وفترة تسليم المستندات. ابحث عن فقرة "حالات الوفاة" او "عذر الوفاة" تحديدا.
2. اذا كان السؤال عن "الغياب عن الاختبار" فالمدة هي 3 ايام.
3. يجب ان تذكر المدة الصحيحة لعذر الوفاة كما وردت في اللائحة: كم يوم مدة الغياب، وكم يوم مهلة تقديم العذر.
4. اذا وجدت فقرة عذر الوفاة اذكرها بنصها مع الفقرة.
5. اجب بالعربية الفصحى الواضحة في نقاط.
اللوائح المرفقة هي المرجع الوحيد.
"""
        parts.append(types.Part.from_text(text=prompt))
        for model_name in all_to_try:
            try:
                r = client.models.generate_content(
                    model=model_name,
                    contents=[types.Content(role="user", parts=parts)]
                )
                if r and r.text and len(r.text.strip()) > 15:
                    ans = r.text
                    break
            except:
                continue
        if not ans:
            ans = "عذرا، لم اجد فقرة عذر الوفاة في الملفات المرفقة."
    except Exception as e:
        ans = f"خطأ: {str(e)[:500]}"
    st.markdown("<div class='answer-box'>" + ans + "</div>", unsafe_allow_html=True)
    disc = "<div class='disclaimer-box'>تنويه: هذا برنامج رد آلي ويمكن ان تكون الاجابات في بعض الاحيان غير دقيقة، وعليه تعتبر اللوائح والانظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والاخير للكلية:<br><a href='" + LINK + "' target='_blank'>" + LINK + "</a></div>"
    st.markdown(disc, unsafe_allow_html=True)
