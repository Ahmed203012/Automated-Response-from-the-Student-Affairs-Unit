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
                        # تقسيم النص بالأسطر المباشرة لدعم ملفات الروابط والأسطر القصيرة
                        lines = [p.strip() for p in text.split('\n') if len(p.strip()) > 3]
                        
                        # تجميع كل سطرين متتاليين لضمان عدم فصل العنوان عن الرابط
                        for i in range(len(lines)):
                            chunk = lines[i]
                            if i + 1 < len(lines):
                                chunk += "\n" + lines[i+1]
                            
                            paragraphs_db.append({
                                'original': chunk,
                                'clean': normalize_arabic(chunk)
                            })
            except Exception as e:
                print(f"Error reading PDF {file}: {e}")
    return paragraphs_db

indexed_db = load_and_index_documents()

def get_relevant_context(query, db):
    clean_query = normalize_arabic(query)
    keywords = [w for w in clean_query.split() if len(w) > 1 and w not in ['ماهي', 'ما هي', 'كم', 'متى', 'كيف', 'عن', 'في', 'من']]
    
    scored = []
    for item in db:
        score = sum(1 for kw in keywords if kw in item['clean'])
        if score > 0:
            scored.append((score, item['original']))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    best_chunks = [item[1] for item in scored[:5]]
    return "\n---\n".join(best_chunks) if best_chunks else ""

# ==========================================
# 3. الاتصال المباشر عبر Groq
# ==========================================
def generate_direct_answer(query, db):
    if not GROQ_API_KEY:
        return "⚠️ لم يتم العثور على `GROQ_API_KEY` في Streamlit Secrets."

    relevant_context = get_relevant_context(query, db)
    
    if not relevant_context:
        return "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح والروابط المرفقة."

    prompt = f"""
    أنت مساعد أكاديمي دقيق جداً. أجب على سؤال الطالب بناءً على النص المقتطع المرفق أدناه فقط.

    النص المقتطع من المستندات واللوائح:
    \"\"\"
    {relevant_context}
    \"\"\"

    سؤال الطالب: "{query}"

    التعليمات الصارمة:
    1. التزم بالنص المرفق فقط ولا تخترع أو تفترض وسائل تقديم من عندك.
    2. إذا كان النص يحتوي على رابط إلكتروني (URL مثل https://Forms.office.com/...) يخص موضوع السؤال، يجب عليك طباعة الرابط كاملاً وصريحاً للطالب.
    3. أجب بأسلوب مباشر ومختصر دون إطالة.
    """

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ خطأ في الاتصال بـ Groq: `{str(e)}`"

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
st.title("🎓 المجيب الأكاديمي الذكي")
st.write("أهلاً بك! اكتب استفسارك وسيجيبك النظام فوراً وبشكل مباشر.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هو رابط تقديم الأعذار؟)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("جاري استخراج الإجابة..."):
            answer = generate_direct_answer(prompt, indexed_db)
            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
