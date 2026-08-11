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
# 2. تهيئة الذكاء الاصطناعي واستخراج النص
# ==========================================
# قم بوضع مفتاح Gemini API هنا أو عبر Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(file_path):
    """استخراج النص الكامل من ملف الـ PDF"""
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"خطأ في قراءة الملف {file_path}: {e}")
    return text

@st.cache_data
def load_all_regulations():
    """تحميل كل ملفات PDF المرفقة في المشروع"""
    combined_text = ""
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            combined_text += f"\n--- محتوى ملف: {file} ---\n"
            combined_text += extract_text_from_pdf(file)
    return combined_text

def ask_ai_about_regulations(query, context):
    """إرسال السؤال والنص للذكاء الاصطناعي لاستخراج الإجابة المباشرة"""
    if not GEMINI_API_KEY:
        return "⚠️ يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات التطبيق لتفعيل المجيب الذكي."
    
    prompt = f"""
    أنت مساعد أكاديمي ذكي لشؤون الطلاب. مهمتك هي الإجابة على سؤال الطالب استناداً فقط إلى اللوائح والأنظمة المرفقة أدناه.
    
    اللوائح والأنظمة المعتمدة:
    \"\"\"
    {context}
    \"\"\"
    
    سؤال الطالب:
    "{query}"
    
    التعليمات:
    1. أجب بدقة ووضوح وبأسلوب سلس ومباشر بناءً على اللوائح أعلاه.
    2. اذكر المدة أو الشرط بالتفصيل (مثل: عدد الأيام، الشروط المطلوب تقديمها).
    3. إذا لم تجد إجابة للسؤال في اللوائح المرفقة نهائياً، أجب بـ: "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة. يرجى مراجعة إدارة الشؤون الأكاديمية."
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بالمجيب الآلي: {str(e)}"

# ==========================================
# 3. واجهة التطبيق
# ==========================================
regulations_context = load_all_regulations()

st.sidebar.title("⚙️ إدارة اللوائح")
st.sidebar.info("📚 يتم قراءة اللوائح والأعذار المرفقة في المشروع تلقائياً بواسطة الذكاء الاصطناعي.")

st.title("🤖 المجيب الآلي لللوائح والاستفسارات")
st.write("أهلاً بك! اكتب استفسارك الأكاديمي وسيجيبك النظام فوراً من واقع اللوائح المعتمدة.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي مهلة تقديم عذر الوفاة؟)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("جاري مراجعة اللوائح والإجابة..."):
        ai_response = ask_ai_about_regulations(prompt, regulations_context)

    with st.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
