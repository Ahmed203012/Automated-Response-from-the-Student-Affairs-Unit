%%writefile app.py
import streamlit as st
import os

try:
    from google import genai
except ImportError:
    os.system("pip install -q google-genai")
    from google import genai

try:
    import pypdf
except ImportError:
    os.system("pip install -q pypdf")
    import pypdf

# ضبط إعدادات الصفحة
st.set_page_config(page_title="كليات الرؤية - Vision Colleges", layout="centered")

# إدراج تنسيق CSS لدعم اتجاه اللغة العربية من اليمين لليسار (RTL)
st.markdown("""
    <style>
    /* تطبيق محاذاة اليمين على الصفحة كاملة */
    html, body, [class*="css"], div, p, span, input, button, label {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* محاذاة صندوق النص والزر */
    .stTextInput > div > div > input {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* تنسيق زر الإجابة */
    .stButton > button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    
    /* محاذاة عناوين الإجابات */
    .stAlert, .stMarkdown {
        text-align: right !important;
        direction: rtl !important;
    }
    </style>
""", unsafe_unsafe_html=True)

API_KEY = "AQ.Ab8RN6KzXlK-oCzASuzgsAfBGCdHDEypywVfasmG79T4vOtVCQ"

@st.cache_data
def load_all_documents():
    extracted_text = ""
    for file in os.listdir('.'):
        if file.startswith('.'):
            continue
        if file.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            except Exception:
                pass
        elif file.endswith('.txt') and file not in ['app.py', 'requirements.txt']:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    extracted_text += f.read() + "\n"
            except Exception:
                pass
    return extracted_text.strip()

context = load_all_documents()

# عرض شعار الكلية إذا كان مرفوعاً باسم logo.png
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", width=180)

# العناوين الرئيسية
st.title("كليات الرؤية - Vision Colleges")
st.subheader("الإستفسار الآلي - وحدة شؤون الطلبة")
st.write("أهلاً بك، يمكنك طرح أي سؤال متعلق باللوائح والتعليمات الأكاديمية.")

# صندوق إدخال السؤال
user_query = st.text_input("اسأل سؤالك هنا:")

# زر إرسال السؤال بالنص الجديد
submit_button = st.button("اضغط هنا للحصول على الإجابة")

if (submit_button or user_query) and user_query:
    if not context:
        st.error("عذراً، لم يتم العثور على أي لوائح أو مستندات مرفوعة للنظام.")
    else:
        with st.spinner("جاري البحث داخل اللائحة المرفقة..."):
            try:
                client = genai.Client(api_key=API_KEY)
                
                strict_prompt = f"""
أنت مساعد أكاديمي لشؤون الطلبة في كليات الرؤية.
تنبيه صارم جداً: أجب على سؤال الطالب بناءً على النص المرفق أدناه فقط لا غير.
إذا لم تكن الإجابة مذكورة بوضوح وصراحة داخل النص المرفق، أجب بالحرف الواحد: "عذراً، هذه المعلومة غير مذكورة في اللائحة الأكاديمية المرفقة."
يُمنع منعاً باتاً استخدام أي معلومات أو معارف عامة من خارج هذا النص.

المستندات المرفقة:
{context}

سؤال الطالب:
{user_query}
"""
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=strict_prompt,
                )
                
                st.markdown("### الإجابة من واقع اللائحة:")
                st.write(response.text)
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاستعلام: {e}")
