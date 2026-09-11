import os
import re
import fitz  # PyMuPDF لقراءة ملفات الـ PDF المرفقة
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


PDF_KNOWLEDGE_BASE = load_context_from_pdfs()

# ==========================================
# 3. عرض الشعار ورأس الصفحة
# ==========================================
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
1. Do NOT output any internal monologue, reasoning, chain-of-thought, or thinking process.
2. Output ONLY the direct final answer in Arabic intended for the user.
3. Answer user questions directly based on the provided Reference Data below.

=================== REFERENCE DATA / النص المرجعي المعتمد ===================
{PDF_KNOWLEDGE_BASE}
============================================================================
"""


def clean_response(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(
        r"(<think>.*?</think>|Here's a thinking process.*?\n\n)",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return cleaned.strip()


# ==========================================
# 6. معالجة الإرسال عبر Groq API
# ==========================================
if submit_btn:
    if not user_query.strip():
        st.warning("يرجى كتابة الاستفسار أولاً.")
    else:
        with st.spinner("جاري البحث في اللوائح والأنظمة..."):
            try:
                api_key = os.environ.get("GROQ_API_KEY", "")

                if not api_key:
                    st.error(
                        "لم يتم العثور على مفتاح GROQ_API_KEY في إعدادات Render."
                    )
                else:
                    client = Groq(api_key=api_key)

                    # استخدام النموذج المستقر llama3-70b-8192
                    response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                            {"role": "user", "content": user_query},
                        ],
                        temperature=0.2,
                    )

                    raw_answer = response.choices[0].message.content
                    final_answer = clean_response(raw_answer)

                    st.success(final_answer)

            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الطلب: {str(e)}")

# ==========================================
# 7. التنويه السفلي بالمرجع المعتمد
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
