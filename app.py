import os
import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
from docx import Document
import pandas as pd
from groq import Groq

# 1. إعداد الصفحة
st.set_page_config(page_title="استفسار شؤون الطلبة - كليات الرؤية", page_icon="🎓", layout="centered")

# 2. حقن CSS لدعم اتجاه RTL والتنسيق العربي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"], div, p, span, input, button {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stApp {
        direction: rtl !important;
        text-align: right !important;
    }
    
    h1, h2, h3, h4, .stMarkdown p {
        text-align: right !important;
        direction: rtl !important;
    }
    
    .stTextInput input {
        text-align: right !important;
        direction: rtl !important;
    }
    
    .stButton button {
        width: 100% !important;
        background-color: #8C7355 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: none !important;
    }
    
    .stButton button:hover {
        background-color: #6e5a42 !important;
        color: white !important;
    }
    
    .answer-box {
        background-color: #f4f4f6;
        border-right: 5px solid #8C7355;
        padding: 18px;
        border-radius: 8px;
        margin-top: 15px;
        direction: rtl !important;
        text-align: right !important;
        font-size: 16px;
        line-height: 1.7;
    }
    
    .disclaimer-box {
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #e0e0e0;
        font-size: 13px;
        color: #666666;
        text-align: right !important;
        direction: rtl !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. الشعار والعناوين
st.image("Logo.png", width=160)
st.title("كليات الرؤية - Vision Colleges")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
st.write("مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

# 4. إعداد Groq Client
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# 5. قراءة الملفات بالتخزين المؤقت
@st.cache_data(ttl=3600)
def read_all_chunks():
    chunks = []
    folder_path = "."
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith(".pdf"):
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            chunks.append(f"--- المصدر: {file} (صفحة {i+1}) ---\n{text}")
            except Exception:
                try:
                    doc = fitz.open(file_path)
                    for i, page in enumerate(doc):
                        text = page.get_text()
                        if text:
                            chunks.append(f"--- المصدر: {file} (صفحة {i+1}) ---\n{text}")
                except Exception:
                    pass
        elif file.endswith(".docx"):
            try:
                doc = Document(file_path)
                full_text = [p.text for p in doc.paragraphs if p.text.strip()]
                if full_text:
                    chunks.append(f"--- المصدر: {file} ---\n" + "\n".join(full_text))
            except Exception:
                pass
        elif file.endswith(".xlsx") or file.endswith(".xls"):
            try:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    text = df.to_string()
                    if text:
                        chunks.append(f"--- المصدر: {file} (ورقة: {sheet_name}) ---\n{text}")
            except Exception:
                pass
                
    return chunks

# 6. المدخلات ومعالجة الاستفسار
q = st.text_input("أدخل استفسارك هنا:", placeholder="ما هي المدة المسموح بها لتقديم عذر الوفاة؟")

btn = st.button("للرد على استفسارك اضغط هنا")

if btn or q:
    if not q.strip():
        st.warning("يرجى كتابة السؤال أولاً.")
    elif not client:
        st.error("مفتاح GROQ_API_KEY غير معرف في بيئة العمل.")
    else:
        with st.spinner("جاري جلب الإجابة..."):
            all_chunks = read_all_chunks()
            corpus = "\n\n".join(all_chunks)
            
            # اقتطاع النص المرجعي لحماية الطلب من تجاوز حجم الـ Context Limit الخاص بـ Groq
            truncated_corpus = corpus[:12000]
            
            prompt = f"""أنت مساعد آلي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.
إليك النص المرجعي من اللوائح والأنظمة الرسمية للكلية:

النص المرجعي:
{truncated_corpus}

السؤال: {q}

الإجابة: بناءً على اللوائح المرفقة فقط، أجب على سؤال الطالب بدقة ووضوح وبأسلوب مهذب ومباشر باللغة العربية. إذا لم تجد الإجابة في النص المرجعي، أخبر الطالب بلباقة أن يراجع وحدة شؤون الطلبة مباشرة."""

            # جلب النماذج المتاحة ديناميكياً لتفادي خطأ 404
            ans = ""
            try:
                available_models = [m.id for m in client.models.list().data if "whisper" not in m.id and "safetensors" not in m.id]
                
                # اختيار نموذج مناسب
                selected_model = None
                for target in ["llama-3.3-70b", "llama-3.1-8b", "llama3", "mixtral", "gemma"]:
                    match = [m for m in available_models if target in m]
                    if match:
                        selected_model = match[0]
                        break
                
                if not selected_model and available_models:
                    selected_model = available_models[0]
                
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                ans = completion.choices[0].message.content.strip()
            except Exception as e:
                ans = f"خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}"

            st.markdown(f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True)

# 7. التنويه السفلي
st.markdown("""
<div class='disclaimer-box'>
تنبيـه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المستمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية:<br>
<a href='https://elearning.vision.edu.sa/course/view.php?id=788' target='_blank'>https://elearning.vision.edu.sa/course/view.php?id=788</a>
</div>
""", unsafe_allow_html=True)
