import streamlit as st
import pypdf
import os
import re

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="المجيب الآلي لللوائح والأستفسارات",
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
# 2. قراءة واستخراج النصوص من ملفات PDF
# ==========================================
def extract_text_from_pdf(file_path):
    """استخراج النص من ملف PDF محلي"""
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text

def normalize_arabic(text):
    """تنظيف وتوحيد الأحرف العربية لضمان دقة البحث"""
    text = re.sub(r'[\u064B-\u0652]', '', text) # إزالة التشكيل
    text = re.sub(r'[إأآا]', 'ا', text)         # توحيد الألفات
    text = re.sub(r'ة', 'ه', text)              # توحيد التاء المربوطة
    text = re.sub(r'ى', 'ي', text)              # توحيد الألف المقصورة
    return text

@st.cache_data
def load_all_documents():
    """تحميل كل ملفات الـ PDF المرفوقة في المستودع تلقائياً"""
    combined_text = ""
    # قراءة كافة ملفات PDF في مجلد المشروع
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            combined_text += f"\n--- {file} ---\n"
            combined_text += extract_text_from_pdf(file)
    return combined_text

# ==========================================
# 3. محرك البحث الذكي في اللوائح
# ==========================================
def smart_search(query, full_text):
    if not query.strip():
        return "يرجى كتابة استفسارك أولاً."

    # توحيد الاستعلام والنص للبحث المرن
    norm_query = normalize_arabic(query)
    keywords = [w for w in norm_query.split() if len(w) > 2]
    
    # تقسيم النص إلى فقرات
    paragraphs = full_text.split('\n\n')
    if len(paragraphs) < 3:
        paragraphs = full_text.split('\n')

    matches = []
    for p in paragraphs:
        norm_p = normalize_arabic(p)
        # حساب عدد الكلمات المتطابقة في الفقرة
        score = sum(1 for word in keywords if word in norm_p)
        if score > 0 and len(p.strip()) > 20:
            matches.append((score, p.strip()))

    # ترتيب النتائج حسب الأكثر تطابقاً
    matches.sort(key=lambda x: x[0], reverse=True)

    if matches:
        # أخذ أفضل فقرتين مرتبطتين بالموضوع
        best_results = [m[1] for m in matches[:2]]
        response = "📌 **بناءً على اللوائح التنفيذية المعتمدة:**\n\n"
        response += "\n\n---\n\n".join(best_results)
        return response
    else:
        return "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة. يرجى مراجعة إدارة الشؤون الأكاديمية."

# ==========================================
# 4. تحميل البيانات والواجهة الرئيسية
# ==========================================
# تحميل اللوائح تلقائياً من ملفات الـ PDF الموجودة في المشروع
regulations_db = load_all_documents()

# القائمة الجانبية لإدارة ورؤية حالة الملفات
st.sidebar.title("⚙️ إدارة اللوائح والملفات")
st.sidebar.info("📚 يتم قراءة اللوائح والأعذار المرفقة في النظام تلقائياً.")

uploaded_files = st.sidebar.file_uploader(
    "رفع ملفات إضافية (PDF):", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    extra_text = ""
    for file in uploaded_files:
        extra_text += extract_text_from_pdf(file) + "\n"
    regulations_db += extra_text
    st.sidebar.success("✅ تم إضافة الملفات الجديدة للبحث!")

# الواجهة الرئيسية
st.title("🤖 المجيب الآلي لللوائح والاستفسارات")
st.write("أهلاً بك! اكتب استفسارك الأكاديمي أدناه وسيقوم النظام بالرد عليك فوراً طبقاً لللوائح المعتمدة.")
st.divider()

# سِجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب استفسارك هنا (مثال: الإجازات المرضية)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # البحث الفوري وإظهار الإجابة
    response = smart_search(prompt, regulations_db)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
