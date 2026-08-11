import streamlit as st
import pypdf
import os
import google.generativeai as genai

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="المجيب الآلي لللوائح الأكاديمية",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stTextInput input { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. تهيئة الذكاء الاصطناعي واستخراج النص (مرة واحدة فقط)
# ==========================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def load_and_cache_pdf_text():
    """قراءة كل ملفات الـ PDF وتخزينها في الذاكرة مرة واحدة فقط عند تشغيل التطبيق"""
    combined_text = ""
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        combined_text += text + "\n"
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return combined_text

# تحميل اللوائح مرة واحدة فقط في الذاكرة لتسريع الأداء لـ 0 ثانية
regulations_context = load_and_cache_pdf_text()

# ==========================================
# 3. دالة توليد الإجابة المباشرة (Streaming like ChatGPT)
# ==========================================
def stream_ai_response(query, context):
    if not GEMINI_API_KEY:
        yield "⚠️ يرجى إدخال مفتاح GEMINI_API_KEY في إعدادات Secrets لتشغيل المجيب."
        return

    prompt = f"""
    أنت مساعد أكاديمي ذكي لشؤون الطلاب. أجب على سؤال الطالب استناداً إلى اللوائح المرفقة أدناه فقط.
    
    اللوائح:
    \"\"\"
    {context}
    \"\"\"
    
    سؤال الطالب: "{query}"
    
    التعليمات:
    - أجب بشكل مباشر ودقيق وسريع جداً.
    - اذكر المهل والأيام المحددة صراحة (مثل: أسبوع عمل، 5 أيام).
    - إذا لم تكن الإجابة موجودة باللوائح، قل: "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة."
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # تفعيل خاصية الكتابة الفورية التدريجية
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"حدث خطأ: {str(e)}"

# ==========================================
# 4. الواجهة الرئيسية وشات المحادثة
# ==========================================
st.title("🤖 المجيب الآلي لللوائح والاستفسارات")
st.write("أهلاً بك! اكتب استفسارك الأكاديمي وسيجيبك النظام فوراً.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال والكتابة الفورية
if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي مهلة تقديم عذر الوفاة؟)..."):
    # عرض سؤال الطالب
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # إنشاء رد المساعد والكتابة الحية (Stream)
    with st.chat_message("assistant"):
        response_placeholder = st.write_stream(stream_ai_response(prompt, regulations_context))
        
    st.session_state.messages.append({"role": "assistant", "content": response_placeholder})
