import streamlit as st
import pypdf
import os
import re

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
# 2. معالجة النصوص واللوائح
# ==========================================
def normalize_arabic(text):
    """تنظيف وتوحيد الحروف العربية لتسهيل البحث الشامل"""
    if not text:
        return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)  # إزالة التشكيل
    text = re.sub(r'[إأآا]', 'ا', text)          # توحيد الألف
    text = re.sub(r'ة', 'ه', text)               # توحيد التاء المربوطة
    text = re.sub(r'ى', 'ي', text)               # توحيد الألف المقصورة
    return text.lower()

@st.cache_data
def load_all_documents():
    """قراءة كل ملفات الـ PDF وتخزينها في الذاكرة لتكون سرعة الرد فائقة"""
    all_chunks = []
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        # تقسيم الصفحة إلى فقرات منظمة
                        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 10]
                        if not paragraphs:
                            paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 10]
                        
                        for p in paragraphs:
                            all_chunks.append({
                                'original': p,
                                'clean': normalize_arabic(p)
                            })
            except Exception as e:
                print(f"Error loading {file}: {e}")
    return all_chunks

# تحميل اللوائح مرة واحدة فقط في الذاكرة
chunks_db = load_all_documents()

# ==========================================
# 3. محرك البحث السريع والإجابة المباشرة
# ==========================================
def find_best_answers(query, db):
    if not query.strip():
        return "يرجى كتابة استفسارك أولاً."

    clean_query = normalize_arabic(query)
    # استخراج الكلمات المفتاحية
    keywords = [word for word in clean_query.split() if len(word) > 2 and word not in ['ما هي', 'ماهو', 'كم', 'متى', 'كيف', 'عن', 'في', 'من']]
    
    if not keywords:
        keywords = clean_query.split()

    scored_results = []
    for chunk in db:
        score = 0
        for kw in keywords:
            if kw in chunk['clean']:
                score += 1
        if score > 0:
            scored_results.append((score, chunk['original']))

    # ترتيب النتائج من الأفضل للأقل
    scored_results.sort(key=lambda x: x[0], reverse=True)

    if scored_results:
        # دمج أفضل نتيجة أو نتيجتين
        top_answers = list(dict.fromkeys([item[1] for item in scored_results[:2]]))
        formatted_response = "📌 **بناءً على اللوائح التنفيذية المعتمدة:**\n\n"
        formatted_response += "\n\n---\n\n".join(top_answers)
        return formatted_response
    else:
        return "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة. يرجى مراجعة إدارة الشؤون الأكاديمية."

# ==========================================
# 4. واجهة المحادثة الرئيسية
# ==========================================
st.title("🤖 المجيب الآلي لللوائح والاستفسارات")
st.write("أهلاً بك! اكتب استفسارك الأكاديمي وسيجيبك النظام فوراً.")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض سوابق المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال سؤال الطالب
if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي مهلة تقديم عذر الوفاة؟)..."):
    # 1. عرض سؤال الطالب
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. إيجاد الإجابة الفورية وعرضها
    answer = find_best_answers(prompt, chunks_db)

    with st.chat_message("assistant"):
        st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
