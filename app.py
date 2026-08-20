import streamlit as st
import pypdf
import os
import re
from groq import Groq

# ==========================================
# 1. إعدادات الصفحة والواجهة
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

FIXED_NO_INFO_RESPONSE = "عذراً، هذه المعلومة غير متوفرة في اللوائح المرفقة حالياً، وجاري العمل على تحديثها والرد عليكم في وقت لاحق."

# ==========================================
# 2. قراءة مفتاح الـ API والملفات
# ==========================================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "").strip()

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
                        lines = [p.strip() for p in text.split('\n') if len(p.strip()) > 3]
                        for i in range(len(lines)):
                            chunk = lines[i]
                            if i + 1 < len(lines):
                                chunk += "\n" + lines[i+1]
                            
                            paragraphs_db.append({
                                'original': chunk,
                                'clean': normalize_arabic(chunk),
                                'has_url': 'http' in chunk.lower()
                            })
            except Exception as e:
                print(f"Error reading PDF {file}: {e}")
    return paragraphs_db

indexed_db = load_and_index_documents()

def get_relevant_context(query, db):
    clean_query = normalize_arabic(query)
    stop_words = {'ماهي', 'ما', 'هي', 'كم', 'متى', 'كيف', 'عن', 'في', 'من', 'طريقه', 'طريقة', 'هل', 'يمكن', 'كيفية'}
    keywords = [w for w in clean_query.split() if len(w) > 2 and w not in stop_words]
    
    if not keywords:
        return ""

    scored = []
    for item in db:
        matches = sum(1 for kw in keywords if kw in item['clean'])
        
        if matches >= 1:
            score = matches
            if item['has_url'] and any(w in clean_query for w in ['رابط', 'تقديم', 'نماذج', 'الكتروني', 'الكترونيا']):
                score += 5
            scored.append((score, item['original']))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    best_chunks = [item[1] for item in scored[:4]]
    return "\n---\n".join(best_chunks) if best_chunks else ""

# ==========================================
# 3. الاتصال المباشر بنموذج Groq الرسمي المعتمد
# ==========================================
def generate_direct_answer(query, db):
    if not GROQ_API_KEY:
        return "⚠️ لم يتم العثور على `GROQ_API_KEY` في Streamlit Secrets."

    relevant_context = get_relevant_context(query, db)
    
    if not relevant_context:
        return FIXED_NO_INFO_RESPONSE

    system_instruction = f"""
    أنت نظام إجابة آلي صارم ومغلق تماماً.
    تعتمد فقط وحصرياً على "النص المرفق" للإجابة.

    التعليمات الإلزامية:
    1. يمنع منعاً باتاً إضافة أي معلومة من خارج النص المرفق أدناه، حتى لو كانت معلومة عامة أو صحيحة.
    2. إذا لم تكن الإجابة المباشرة والصريحة موجودة داخل "النص المرفق"، يجب عليك كتابة هذه الجملة فقط دون أي تعديل أو إضافة:
       "{FIXED_NO_INFO_RESPONSE}"
    3. لا تذكر مصطلحات مثل (صحتي، وزارات، منصات خارجية) إلا إذا كانت مكتوبة بالكامل في النص المرفق.
    """

    user_prompt = f"""
    النص المرفق:
    \"\"\"
    {relevant_context}
    \"\"\"

    السؤال: "{query}"
    """

    client = Groq(api_key=GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ خطأ في الاتصال: `{str(e)}`"

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
st.title("🎓 المجيب الأكاديمي الذكي")
st.write("أهلاً بك! اكتب استفسارك وسيجيبك النظام فوراً وبشكل مباشر من واقع اللوائح المرفقة.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب استفسارك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("جاري مراجعة اللوائح..."):
            answer = generate_direct_answer(prompt, indexed_db)
            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
