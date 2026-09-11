import os
import re
import fitz  # PyMuPDF لقراءة ملفات الـ PDF المرفقة بالمستودع
import streamlit as st
from groq import Groq

# ==========================================
# 1. إعدادات الصفحة والتصميم العنابي ودعم RTL
# ==========================================
st.set_page_config(
    page_title="كليات الرؤية - وحدة شؤون الطلبة", page_icon="🎓", layout="centered"
)

st.markdown(
    """
    <style>
    /* محاذاة الصفحة كاملة من اليمين إلى اليسار RTL */
    html, body, [data-testid="stAppViewContainer"], .main {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* ضبط إدخال النصوص وحقول الإدخال */
    input, textarea, div[data-baseweb="input"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* تنسيق زر الإرسال العنابي المميز */
    div.stButton > button {
        width: 100%;
        background-color: #8b1538 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1rem !important;
        border: none !important;
    }
    div.stButton > button:hover {
        background-color: #6a102a !important;
        color: white !important;
    }
    
    /* تنويه الأسفل Footer */
    .footer-warning {
        font-size: 0.85rem;
        color: #555;
        border-top: 1px solid #ddd;
        padding-top: 12px;
        margin-top: 35px;
        text-align: center !important;
        direction: rtl;
    }
    
    /* إخفاء القوائم غير الضرورية لتنظيف الواجهة */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. دالة لقراءة ملفات الـ PDF المرفقة في المجلد
# ==========================================
@st.cache_data
def load_context_from_pdfs():
    """تقوم هذه الدالة بقراءة جميع ملفات الـ PDF المرفقة بالمستودع تلقائياً

    لتوفير النص الكامل واللوائح للنموذج بدقة.
    """
    pdf_text = ""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for file in os.listdir(current_dir):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(current_dir, file)
            try:
                doc = fitz.open(pdf_path)
                pdf_text += f"\n\n--- محتوى ملف: {file} ---\n"
                for page in doc:
                    pdf_text += page.get_text()
            except Exception as e:
                pass

    return pdf_text


# تحميل نصوص اللوائح من ملفات PDF المرفقة
PDF_KNOWLEDGE_BASE = load_context_from_pdfs()

# ==========================================
# 3. عرض الشعار ورأس الصفحة
# ==========================================
# عرض logo.png إذا كان موجوداً بالمستودع
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

st.title("كليات الرؤية - Vision Colleges")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
st.caption(
    "مرحباً بكم في كلية الرؤية بالرياض. نرحب باستفساراتكم حول لوائح وأنظمة الكلية."
)

# ==========================================
# 4. حقل إدخال السؤال
# ==========================================
user_query = st.text_input(
    "أدخل استفسارك هنا:", placeholder="ما هو الزي الرسمي للطلاب؟"
)

submit_btn = st.button("للرد على استفسارك اضغط هنا")

# ==========================================
# 5. تعليمات النظام ونصوص المرجع لـ Groq
# ==========================================
SYSTEM_INSTRUCTIONS = f"""
Role: Official AI assistant for Student Affairs at Vision Colleges in Riyadh.

CRITICAL DIRECTIVES:
1. Do NOT output any internal monologue, reasoning, chain-of-thought, or thinking process (e.g., "Here's a thinking process", "Analyze User Input", "Scan Reference Text", etc.).
2. Output ONLY the direct final answer in Arabic intended for the user.
3. Answer user questions directly based on the provided Reference Data below.

Instructions:
- Provide a direct, polished, final answer in clear Arabic only.
- Do not use raw markdown symbols like asterisks (*) in a distorted or messy way.
- Format lists with clear Arabic bullet points or numbered lists.

=================== REFERENCE DATA / النص المرجعي المعتمد ===================

[1] الزي الرسمي والسلوك العام (Dress Code & Behavior):
- يجب على جميع الطلاب الالتزام بالزي الرسمي المحتشم والمناسب للبيئة الأكاديمية والطبية داخل حرم الكلية.
- الزي الرسمي للطلاب في الكليات السريرية والطبية: السكراب (Scrap) الطبي المعتمد باللون المحدد لكل تخصص أو المعطف الأبيض (Lab Coat) والنظافة العامة.
- الزي الرسمي في القاعات النظرية: الثوب السعودي الرسمي أو الملابس الاحتشامية غير المخالفة للذوق العام.
- يُحظر ارتداء الملابس غير اللائقة، الشورتات، أو الملابس التي تحتوي على شعارات غير مناسبة داخل الحرم الجامعي.

[2] التسجيل والعبء الدراسي والساعات المسموح بها:
- الحد الأدنى للعبء الدراسي في الفصل الاعتيادي هو 12 ساعة معتمدة.
- الحد الأقصى للعبء الدراسي يعتمد على المعدل التراكمي للطالب ويصل إلى 18-20 ساعة معتمدة حسب اللائحة الأكاديمية.

[3] محتوى اللوائح والقرارات من الملفات الرسمية المرفقة:
{PDF_KNOWLEDGE_BASE}
============================================================================
"""


# ==========================================
# 6. دالة تنقية الإجابة من أي تفكير مسرب
# ==========================================
def clean_response(text: str) -> str:
    if not text:
        return ""
    # إزالة مقاطع التفكير في حال ظهرت
    cleaned = re.sub(
        r"(<think>.*?</think>|Here's a thinking process.*?\n\n)",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return cleaned.strip()


# ==========================================
# 7. معالجة الإرسال عبر Groq API
# ==========================================
if submit_btn:
    if not user_query.strip():
        st.warning("يرجى كتابة الاستفسار أولاً.")
    else:
        with st.spinner("جاري البحث في اللوائح والأنظمة..."):
            try:
                # جلب المفتاح المسمى GROQ_API_KEY من بيئة Render
                api_key = os.environ.get("GROQ_API_KEY", "")

                if not api_key:
                    st.error(
                        "لم يتم العثور على مفتاح GROQ_API_KEY. يرجى التأكد من إضافته في إعدادات Render (Environment)."
                    )
                else:
                    client = Groq(api_key=api_key)

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                            {"role": "user", "content": user_query},
                        ],
                        temperature=0.2,
                    )

                    raw_answer = response.choices[0].message.content
                    final_answer = clean_response(raw_answer)

                    # عرض النتيجة المباشرة
                    st.success(final_answer)

            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الطلب: {str(e)}")

# ==========================================
# 8. التنويه السفلي بالمرجع المعتمد
# ==========================================
st.markdown(
    """
    <div class="footer-warning">
        تنبيه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المستمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية:<br>
        <a href="https://elearning.vision.edu.sa/course/view.php?id=788" target="_blank">https://elearning.vision.edu.sa/course/view.php?id=788</a>
    </div>
""",
    unsafe_allow_html=True,
)
