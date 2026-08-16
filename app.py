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

# الرد الثابت المعتمد عند عدم وجود المعلومة بالنصوص المرفقة
FIXED_NO_INFO_RESPONSE = "عذراً، هذه المعلومة غير متوفرة في اللوائح المرفقة حالياً، وجاري العمل على تحديثها والرد عليك في وقت لاحق."

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
    keywords = [w for w in clean_query.split() if len(w) > 1 and w not in ['ماهي', 'ما هي', 'كم', 'متى', 'كيف', 'عن', 'في', 'من', 'طريقه', 'طريقة', 'هل']]
    
    scored = []
    for item in db:
        score = sum(1 for kw in keywords if kw in item['clean'])
        
        if item['has_url'] and any(w in clean_query for w in ['رابط', 'تقديم', 'طريقه', 'طريقة', 'نموذج', 'انشطة', 'تظلم', 'عذر', 'اعذار', 'الكترونيا', 'الكتروني']):
            score += 5
            
        if score > 0:
            scored.append((score, item['original']))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    best_chunks = [item[1] for item in scored[:6]]
    return "\n---\n".join(best_chunks) if best_chunks else ""

# ==========================================
# 3. الاتصال المباشر عبر Groq
# ==========================================
def generate_direct_answer(query, db):
    if not GROQ_API_KEY:
        return "⚠️ لم يتم العثور على `GROQ_API_KEY` في Streamlit Secrets."

    relevant_context = get_relevant_context(query, db)
    
    # إذا لم يجد أي كلمة مطابقة في المستندات يُرجع الرد الثابت فوراً
    if not relevant_context:
        return FIXED_NO_INFO_RESPONSE

    system_instruction = f"""
    أنت محرك بحث دقيق ومغلق. مهمتك الحصرية هي الإجابة عن سؤال الطالب اعتماداً فقط وحصرياً على "النص المقتطع" المرفق.

    قواعد صارمة جداً:
    1. يمنع منعاً باتاً الاستعانة بأي معلومات خارجية أو عامة من الإنترنت (مثل منصة صحتي، أو إجراءات خارج المستند).
    2. إذا كانت إجابة السؤال غير مذكورة صراحة وضمنياً في "النص المقتطع"، يُمنع التخمين أو الاجتهاد، ويجب عليك كتابة هذا النص بالضبط وبدون أي زيادة:
       "{FIXED_NO_INFO_RESPONSE}"
    3. إذا احتوى النص على رابط إلكتروني (URL) يخص الموضوع، اكتبه كاملاً وبوضوح.
    """

    user_prompt = f"""
    النص المقتطع من اللوائح والمستندات:
    \"\"\"
    {relevant_context}
    \"\"\"

    سؤال الطالب: "{query}"
    """

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0  # إيقاف الابتكار كلياً للالتزام بالنص الحرفي
        )
        return response.choices[0].message.content
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
