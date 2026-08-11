import streamlit as st
import pypdf # لتشغيل قراءة ملفات PDF

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="المساعد الآلي لللوائح الأكاديمية",
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
# 2. إدارة اللوائح والنصوص المرفقة
# ==========================================
if "regulations_text" not in st.session_state:
    # يمكنك كتابة اللوائح الافتراضية هنا مباشرة بين العلامات
    st.session_state["regulations_text"] = """
    مادة (1): الحضور والغياب: يتوجب على الطالب تقديم عذر غياب مقبول خلال 5 أيام عمل من تاريخ الانقطاع.
    مادة (2): إعادة التصحيح: يتم تقديم طلب إعادة تصحيح الاختبار عبر البوابة خلال أسبوعين من إعلان النتائج.
    مادة (3): الإنسحاب من المقرر: يحق للطالب الإنسحاب من المقرر قبل الأسبوع العاشر من الفصل الدراسي.
    """

def extract_text_from_pdf(uploaded_file):
    """استخراج النصوص من ملفات PDF"""
    pdf_reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def find_auto_answer(query, context):
    """البحث في نصوص اللوائح وإرجاع الإجابة المناسبة"""
    if not query.strip():
        return "يرجى كتابة استفسارك أولاً."
    
    lines = context.split('\n')
    matched_lines = []
    query_words = [w for w in query.split() if len(w) > 2]

    for line in lines:
        if any(word in line for word in query_words):
            if line.strip():
                matched_lines.append(line.strip())

    if matched_lines:
        return "📌 **بناءً على اللوائح الأكاديمية المعتمدة:**\n\n" + "\n\n".join(matched_lines)
    else:
        return "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة. يرجى مراجعة إدارة الشؤون الأكاديمية."

# ==========================================
# 3. القائمة الجانبية لرفع اللوائح
# ==========================================
st.sidebar.title("⚙️ إدارة اللوائح والملفات")
uploaded_files = st.sidebar.file_uploader(
    "قم برفع ملفات اللوائح (PDF أو TXT):", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    combined_text = ""
    for file in uploaded_files:
        if file.type == "text/plain":
            combined_text += file.read().decode("utf-8") + "\n"
        elif file.type == "application/pdf":
            combined_text += extract_text_from_pdf(file) + "\n"
    st.session_state["regulations_text"] = combined_text
    st.sidebar.success("✅ تم تحميل اللوائح بنجاح!")

# ==========================================
# 4. الواجهة الرئيسية واستقبال الاستفسارات
# ==========================================
st.title("🤖 المجيب الآلي لللوائح والاستفسارات")
st.write("أهلاً بك! اكتب استفسارك الأكاديمي أدناه وسيقوم النظام بالرد عليك فوراً طبقاً لللوائح المرفقة.")

st.divider()

# سِجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال مدخلات الطالب والتجاوب الفوري
if prompt := st.chat_input("اكتب استفسارك هنا (مثال: ما هي شروط إعادة التصحيح؟)..."):
    # عرض سؤال الطالب
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد وإظهار الرد الفوري
    response = find_auto_answer(prompt, st.session_state["regulations_text"])
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
