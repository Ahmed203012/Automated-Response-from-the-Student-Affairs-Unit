import streamlit as st
import pypdf
import os
import re
import google.generativeai as genai

# ==========================================
# 1. إعدادات الصفحة والتصميم
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
# 2. إعداد مفتاح Gemini
# ==========================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    return text.lower()

@st.cache_resource
def load_and_index_documents():
    paragraphs_db = []
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 10]
                        if not chunks:
                            chunks = [p.strip() for p in text.split('\n') if len(p.strip()) > 10]
                        
                        for chunk in chunks:
                            paragraphs_db.append({
                                'original': chunk,
                                'clean': normalize_arabic(chunk)
                            })
            except Exception as e:
                print(f"Error reading PDF: {e}")
    return paragraphs_db

indexed_db = load_and_index_documents()

def get_relevant_context(query, db):
    clean_query = normalize_arabic(query)
    keywords = [w for w in clean_query.split() if len(w) > 2 and w not in ['ماهي', 'ما هي', 'كم', 'متى', 'كيف', 'عن', 'في', 'من']]
    
    scored = []
    for item in db:
        score = sum(1 for kw in keywords if kw in item['clean'])
        if score > 0:
            scored.append((score, item['original']))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    best_chunks = [item[1] for item in scored[:3]]
    return "\n---\n".join(best_chunks) if best_chunks else ""

# ==========================================
# 3. استدعاء Gemini مع التوافقية وإظهار الأخطاء
# ==========================================
def generate_direct_answer(query, db):
    if not GEMINI_API_KEY:
        return "⚠️ لم يتم العثور على `GEMINI_API_KEY` في Streamlit Secrets. يرجى إضافته أولاً."

    relevant_context = get_relevant_context(query, db)
    
    if not relevant_context:
        return "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة."

    prompt = f"""
    أنت مساعد أكاديمي ذكي. أجب على سؤال الطالب بناءً على النص المقتطع التالي فقط.

    النص المقتطع من اللائحة:
    \"\"\"
    {relevant_context}
    \"\"\"

    سؤال الطالب: "{query}"

    التعليمات:
    1. أجب بأسلوب مباشر ومقتضب جداً (في سطر أو سطرين فقط).
    2. اذكر المهل والشروط والأرقام فوراً.
    3. لا تطبع النص الكامل للائحة.
    """

    # تجربة النموذج الرئيسي، وفي حال فشله استخدام النموذج البديل
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e1:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            return f"❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي:\n\n`{str(e1)}`"

# ==========================================
# 4. واجهة التطبيق
# ==========================================
st.title("🎓 المجيب الأكاديمي الذكي")
st.write("أهلاً بك! اكتب استفسارك وسيجيبك النظام فوراً وبشكل مباشر.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض السجل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال سؤال الطالب
if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي مهلة تقديم عذر الوفاة؟)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("جاري استخراج الإجابة..."):
            answer = generate_direct_answer(prompt, indexed_db)
            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
