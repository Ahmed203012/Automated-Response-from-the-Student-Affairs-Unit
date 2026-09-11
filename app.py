import os
import re
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة والتصميم (Streamlit Config)
# ==========================================
st.set_page_config(
    page_title="كليات الرؤية - وحدة شؤون الطلبة", page_icon="🎓", layout="centered"
)

# تحسين مظهر الواجهة بدعم اتجاه النص من اليمين لليسار (RTL)
st.markdown(
    """
    <style>
    .main {
        direction: rtl;
        text-align: right;
    }
    div.stButton > button {
        width: 100%;
        background-color: #8b1538;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
    div.stButton > button:hover {
        background-color: #6a102a;
        color: white;
    }
    .footer-warning {
        font-size: 0.85rem;
        color: #666;
        border-top: 1px solid #ccc;
        padding-top: 10px;
        margin-top: 30px;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. رأس الصفحة والعنوان (Header)
# ==========================================
st.title("كليات الرؤية - Vision Colleges")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
st.caption(
    "مرحباً بكم في كلية الرؤية بالرياض. نرحب باستفساراتكم حول لوائح وأنظمة الكلية."
)

# ==========================================
# 3. إدخال الاستفسار من قبل الطالب
# ==========================================
user_query = st.text_input(
    "أدخل استفسارك هنا:", placeholder="ما هو الزي الرسمي للطلاب؟"
)

submit_btn = st.button("للرد على استفسارك اضغط هنا")

# ==========================================
# 4. النص المرجعي التفصيلي + التعليمات (System Prompt & Knowledge Base)
# ==========================================
SYSTEM_INSTRUCTIONS = """
Role: Official AI assistant for Student Affairs at Vision Colleges in Riyadh.

CRITICAL DIRECTIVES:
1. Do NOT output any internal monologue, reasoning, chain-of-thought, or thinking process (e.g., "Here's a thinking process", "Analyze User Input", "Scan Reference Text", "Instruction 1 says...", etc.).
2. Output ONLY the direct final answer in Arabic intended for the user.
3. Answer user questions directly based on the provided Reference Data below.

Instructions:
- Provide a direct, polished, final answer in clear Arabic only.
- Do not use raw markdown symbols like asterisks (*) in a distorted or messy way.
- Extract details accurately from the Reference Data.

=================== REFERENCE DATA / النص المرجعي المعتمد ===================

[1] قواعد وأحكام الزي الرسمي والسلوك العام (Dress Code & Behavior):
- يجب على جميع الطلاب الالتزام بالزي الرسمي المحتشم والمناسب للبيئة الأكاديمية والطبية داخل حرم الكلية.
- الزي الرسمي للطلاب في الكليات السريرية والطبية: السكراب (Scrap) الطبي المعتمد باللون المحدد لكل تخصص أو المعطف الأبيض (Lab Coat) والنظافة العامة.
- الزي الرسمي في القاعات النظرية: الثوب السعودي الرسمي أو الملابس الاحتشامية غير المخالفة للذوق العام.
- يُحظر ارتداء الملابس غير اللائقة، الشورتات، أو الملابس التي تحتوي على شعارات غير مناسبة داخل الحرم الجامعي.

[2] خطة الأنشطة الطلابية اللاصفية:
- تتضمن خطة الأنشطة مجالات متعددة: الوعي الرقمي، البحث العلمي، اللغة الإنجليزية، المبادرات المجتمعية، والأنشطة الرياضية والفنية.
- الجداول المالية والتنفيذية تمحور الأنشطة حول رؤية المملكة 2030 وتطوير مهارات الطلاب.

[3] اللجان الإدارية والأكاديمية وأعضاؤها:
- لجنة حقوق الطلاب والتظلمات: تعنى بالنظر في استفسارات وتظلمات الطلاب الشكاوى.
- لجنة الإرشاد الأكاديمي والبحث العلمي وتطوير المهارات.
- إذا تم السؤال عن عضو هيئة تدريس أو شخص محدد (مثل د. أحمد مرسي أو غيره)، يتم ذكر لجنته ودوره بدقة بناءً على القرار الإداري المعتمد.
============================================================================
"""


# ==========================================
# 5. دالة معالجة وتنقية النص (Thinking Cleanup)
# ==========================================
def sanitize_llm_response(raw_text: str) -> str:
    """تضمن هذه الدالة إزالة أي أجزاء تفكير قد يتسرب صدورها من النموذج

    وتعطي الطالب النص العربي النهائي المباشر فقط.
    """
    if not raw_text:
        return ""

    clean_text = raw_text

    # في حال تسرب نص التفكير بالإنجليزية، يتم استخراج الأسطر العربية فقط
    if "Here's a thinking process" in clean_text or "Analyze User Input" in clean_text:
        arabic_lines = [
            line.strip()
            for line in clean_text.split("\n")
            if line.strip()
            and not line.strip().startswith("Step")
            and not line.strip().startswith("Instruction")
            and not re.search(r"^[A-Za-z0-9\s\.\:\-\[\]\(\)]+$", line.strip())
        ]
        if arabic_lines:
            clean_text = "\n".join(arabic_lines)

    return clean_text.strip()


# ==========================================
# 6. تنفيذ طلب الـ API واستدعاء النموذج
# ==========================================
if submit_btn:
    if not user_query.strip():
        st.warning("يرجى كتابة الاستفسار أولاً.")
    else:
        with st.spinner("جاري البحث في اللوائح والأنظمة..."):
            try:
                import google.generativeai as genai

                api_key = os.environ.get("GEMINI_API_KEY", "")
                if api_key:
                    genai.configure(api_key=api_key)

                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=SYSTEM_INSTRUCTIONS,
                )

                prompt = f"استفسار الطالب: {user_query}"
                response = model.generate_content(prompt)

                # استخراج وتصفية النص
                raw_response = response.text
                final_answer = sanitize_llm_response(raw_response)

                # عرض الإجابة المباشرة للطالب
                st.success(final_answer)

            except Exception as e:
                st.error("حدث خطأ أثناء معالجة الاستفسار، يرجى المحاولة لاحقاً.")

# ==========================================
# 7. التنويه والرابط المرجعي (Footer)
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
