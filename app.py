import os
import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
from docx import Document
import pandas as pd
from groq import Groq

# 1. إعداد واجهة Streamlit
st.set_page_config(page_title="استفسار شؤون الطلبة - كليات الرؤية", page_icon="🎓", layout="centered")

# شعار الكلية والعنوان
st.image("Logo.png", width=150)
st.title("كليات الرؤية - Vision Colleges")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
st.write("مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية.")

# 2. إعداد العميل لـ Groq
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    # يمكنك وضع مفتاح API هنا بشكل مباشر إذا لم تضفه في متغيرات البيئة
    api_key = "ضع_مفتاح_GROQ_هنا"

client = Groq(api_key=api_key)

# 3. دالة قراءة الملفات واستخراج النصوص مع التخزين المؤقت لتسريع الأداء
@st.cache_data(ttl=3600)
def read_all_chunks():
    chunks = []
    folder_path = "."  # المجلد الحالي
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # قراءة ملفات PDF
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
                    
        # قراءة ملفات Word
        elif file.endswith(".docx"):
            try:
                doc = Document(file_path)
                full_text = [p.text for p in doc.paragraphs if p.text.strip()]
                if full_text:
                    chunks.append(f"--- المصدر: {file} ---\n" + "\n".join(full_text))
            except Exception:
                pass
                
        # قراءة ملفات Excel
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

# 4. واجهة المدخلات
q = st.text_input("أدخل استفسارك هنا:", placeholder="ما هي المدة المسموح بها لتقديم عذر الوفاة؟")

if st.button("للرد على استفسارك اضغط هنا") or q:
    if not q.strip():
        st.warning("يرجى كتابة السؤال أولاً.")
    else:
        with st.spinner("جاري جلب الإجابة من اللوائح والأنظمة..."):
            # جلب كل النصوص المخزنة
            all_chunks = read_all_chunks()
            corpus = "\n\n".join(all_chunks)
            
            # صياغة الـ Prompt للنموذج
            prompt = f"""أنت مساعد آلي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.
إليك النص المرجعي من اللوائح والأنظمة الرسمية للكلية:

النص المرجعي:
{corpus}

السؤال: {q}

الإجابة: بناءً على اللوائح المرفقة فقط، أجب على سؤال الطالب بدقة ووضوح وبأسلوب مهذب ومباشر. إذا لم تجد الإجابة في النص المرجعي، أخبر الطالب بلباقة أن يراجع وحدة شؤون الطلبة مباشرة."""

            # قائمة النماذج المتاحة للتجربة التلقائية (منعاً لأي خطأ 404 أو Decommissioned)
            available_models = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "gemma2-9b-it"
            ]
            
            completion = None
            last_error = ""

            # محاولة الاتصال بالنماذج بالترتيب
            for model_name in available_models:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                    )
                    if completion and completion.choices:
                        break
                except Exception as e:
                    last_error = str(e)
                    continue

            # عرض الإجابة أو معالجة الخطأ
            if completion and completion.choices:
                ans = completion.choices[0].message.content.strip()
                st.markdown(f"<div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; dir: rtl;'>{ans}</div>", unsafe_allow_html=True)
            else:
                st.error(f"خطأ في الاتصال بالذكاء الاصطناعي: {last_error}")

# التنويه السفلي
st.markdown("---")
st.caption("تنويه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المعتمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية.")
