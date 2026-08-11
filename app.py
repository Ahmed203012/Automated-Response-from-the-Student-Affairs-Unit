import streamlit as st
import pypdf
import os
import google.generativeai as genai

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="المجيب الأكاديمي الذكي",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stTextInput input { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. قراءة اللوائح وتجهيز الذكاء الاصطناعي
# ==========================================
# استدعاء مفتاح API من إعدادات Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@st.cache_data
def load_all_documents():
    """قراءة كل ملفات الـ PDF وتخزينها في الذاكرة لتكون سرعة الرد فائقة"""
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
                print(f"Error loading {file}: {e}")
    return combined_text

regulations_context = load_all_documents()

# ==========================================
# 3. محرك الاستخراج الذكي للإجابة المباشرة
# ==========================================
def get_direct_answer(query, context):
    if not GEMINI_API_KEY:
        return "⚠️ لم يتم ضبط مفتاح GEMINI_API_KEY في إعدادات Secrets."

    prompt = f"""
    أنت مساعد أكاديمي موجه للطلاب. مهمتك هي استخراج الإجابة المباشرة والمحددة فقط لسؤال الطالب بناءً على اللائحة المرفقة.

    اللائحة الأكاديمية:
    \"\"\"
    {context}
    \"\"\"

    سؤال الطالب: "{query}"

    شروط الإجابة الصارمة:
    1. أجب في سطر أو سطرين فقط بالإجابة المباشرة والواضحة للسؤال.
    2. لا تطبع اللائحة كاملة ولا تجلب الفقرات التي لا تعني السؤال.
    3. اذكر الأرقام والمدد الزمنية بدقة كما وردت (مثال: أسبوع عمل من تاريخ الوفاة، 5 أيام).
    4. إذا لم يذكر السؤال في اللائحة نهائياً، أجب فقط بـ: "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المعتمدة."
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"حدث خطأ أثناء معالجة الطلب: {str(e)}"

# ==========================================
# 4. واجهة المحادثة
# ==========================================
st.title("🎓 المجيب الأكاديمي الذكي")
st.write("أهلاً بك! اكتب استفسارك وسيقوم النظام بإجابتك فوراً بأسلوب مباشر.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال وإعطاء إجابة مقتضبة مباشرة
if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي مهلة تقديم عذر الوفاة؟)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("جاري استخراج الإجابة..."):
        direct_answer = get_direct_answer(prompt, regulations_context)

    with st.chat_message("assistant"):
        st.markdown(direct_answer)
    
    st.session_state.messages.append({"role": "assistant", "content": direct_answer})
