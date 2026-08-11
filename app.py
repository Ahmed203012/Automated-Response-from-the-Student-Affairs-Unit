import streamlit as st
import pypdf
import os
import re
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
# 2. تهيئة الذكاء الاصطناعي وقراءة اللوائح
# ==========================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def normalize_arabic(text):
    """توحيد الحروف لتسهيل فلترة النصوص بسرعة"""
    if not text: return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    return text.lower()

@st.cache_resource
def load_and_index_documents():
    """قراءة وتقسيم اللوائح إلى فقرات وتخزينها في الذاكرة لسرعة الوصول"""
    paragraphs_db = []
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        # تقسيم الصفحة لفقرات
                        chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 15]
                        if not chunks:
                            chunks = [p.strip() for p in text.split('\n') if len(p.strip()) > 15]
                        
                        for chunk in chunks:
                            paragraphs_db.append({
                                'original': chunk,
                                'clean': normalize_arabic(chunk)
                            })
            except Exception as e:
                print(f"Error loading {file}: {e}")
    return paragraphs_db

# تحميل الفهرس مرة واحدة فقط عند إقلاع التطبيق
indexed_db = load_and_index_documents()

def get_relevant_context(query, db):
    """فلترة الفقرات ذات الصلة فقط لتقليل حجم البيانات المرسلة للـ AI"""
    clean_query = normalize_arabic(query)
    keywords = [w for w in clean_query.split() if len(w) > 2 and w not in ['ماهي', 'ما هي', 'كم', 'متى', 'كيف', 'عن', 'في', 'من']]
    
    scored = []
    for item in db:
        score = sum(1 for kw in keywords if kw in item['clean'])
        if score > 0:
            scored.append((score, item['original']))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    # أخذ أفضل فقرتين فقط
    best_chunks = [item[1] for item in scored[:2]]
    return "\n---\n".join(best_chunks) if best_chunks else ""

# ==========================================
# 3. دالة توليد الإجابة السريعة (Streaming)
# ==========================================
def stream_direct_answer(query, db):
    if not GEMINI_API_KEY:
        yield "⚠️ يرجى إضافة مفتاح GEMINI_API_KEY في Streamlit Secrets."
        return

    # فلترة سريعة للنص المطلوب فقط
    relevant_context = get_relevant_context(query, db)
    
    if not relevant_context:
        yield "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المعتمدة."
        return

    prompt = f"""
    أنت مساعد أكاديمي ذكي. أجب على سؤال الطالب بناءً على النص اقتطافياً ومباشرة.

    النص المقتطع من اللائحة:
    \"\"\"
    {relevant_context}
    \"\"\"

    سؤال الطالب: "{query}"

    التعليمات:
    - أجب بأسلوب مباشر ومقتضب جداً (في سطر أو سطرين فقط).
    - اذكر المهل والأرقام والشروط فوراً دون مقدمات أو إطالة.
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # تفعيل البث المباشر للإجابة فوراً
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"حدث خطأ: {str(e)}"

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
st.title("🎓 المجيب الأكاديمي الذكي")
st.write("أهلاً بك! اكتب استفسارك وسيجيبك النظام فوراً وبشكل مباشر.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال والكتابة الفورية
if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي مهلة تقديم عذر الوفاة؟)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # كتابة الرد تدريجياً فوراً على الشاشة
        full_response = st.write_stream(stream_direct_answer(prompt, indexed_db))
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
