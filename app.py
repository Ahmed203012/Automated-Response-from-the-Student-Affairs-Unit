import os
import re
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

def normalize_arabic(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = text.replace("عبد ", "عبد")
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

# 5. قراءة واستخراج النصوص على مستوى المقاطع (Chunks) لكل الـ 27 ملفاً
@st.cache_data(ttl=3600)
def read_all_chunks():
    chunks = []
    folder_path = "."
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # قراءة ملفات PDF
        if file.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text and len(text.strip()) > 10:
                            chunks.append({"source": f"{file} (صفحة {i+1})", "text": text})
            except Exception:
                try:
                    doc = fitz.open(file_path)
                    for i, page in enumerate(doc):
                        text = page.get_text()
                        if text and len(text.strip()) > 10:
                            chunks.append({"source": f"{file} (صفحة {i+1})", "text": text})
                except Exception:
                    pass
                    
        # قراءة ملفات Word
        elif file.lower().endswith(".docx"):
            try:
                doc = Document(file_path)
                full_text = [p.text for p in doc.paragraphs if p.text.strip()]
                if full_text:
                    chunks.append({"source": file, "text": "\n".join(full_text)})
            except Exception:
                pass
                
        # قراءة ملفات Excel
        elif file.lower().endswith(".xlsx") or file.lower().endswith(".xls"):
            try:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name).dropna(how='all')
                    sheet_lines = []
                    for _, row in df.iterrows():
                        row_str = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                        if row_str.strip():
                            sheet_lines.append(row_str)
                    
                    if sheet_lines:
                        step = 25
                        for i in range(0, len(sheet_lines), step):
                            chunk_text = "\n".join(sheet_lines[i:i+step])
                            chunks.append({"source": f"{file} (ورقة: {sheet_name} - صفوف {i+1}-{i+len(sheet_lines[i:i+step])})", "text": chunk_text})
            except Exception:
                pass
                
    return chunks

# 6. دالة تصفية المقاطع الذكية وتوسيع نطاق البحث للأسماء واللجان
def get_relevant_context(query, chunks, max_chars=16000):
    norm_query = normalize_arabic(query)
    # استخراج الكلمات المعنوية (أكثر من حرفين واستبعاد أدوات الاستفهام)
    stop_words = ["ما", "هي", "ماهي", "من", "في", "على", "عن", "التي", "الذي", "بها", "ماهي", "اين"]
    query_words = [w for w in norm_query.split() if len(w) > 2 and w not in stop_words]
    
    scored_chunks = []
    for item in chunks:
        score = 0
        norm_text = normalize_arabic(item["text"])
        
        # إعطاء أولوية عالية جداً لمطابقة اسم الشخص
        for word in query_words:
            if word in norm_text:
                score += 3
        
        # مطابقة الاسم بالكامل
        if norm_query in norm_text:
            score += 15
            
        # إذا كان المقطع قراراً إدارياً أو يحتوي على كلمة لجنة/لجان
        if "لجنة" in norm_text or "قرار" in norm_text or "مجلس" in norm_text:
            score += 2
            
        scored_chunks.append((score, item))
    
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    selected_text = ""
    for score, item in scored_chunks:
        chunk_entry = f"--- المصدر: {item['source']} ---\n{item['text']}\n\n"
        if len(selected_text) + len(chunk_entry) <= max_chars:
            selected_text += chunk_entry
        else:
            break
            
    return selected_text if selected_text else "".join([f"--- المصدر: {c['source']} ---\n{c['text']}\n\n" for c in chunks])[:max_chars]

# 7. المدخلات ومعالجة الاستفسار
q = st.text_input("أدخل استفسارك هنا:", placeholder="ما هي اللجان التي بها أحمد مرسي؟")

btn = st.button("للرد على استفسارك اضغط هنا")

if btn or q:
    if not q.strip():
        st.warning("يرجى كتابة السؤال أولاً.")
    elif not client:
        st.error("مفتاح GROQ_API_KEY غير معرف في بيئة العمل.")
    else:
        with st.spinner("جاري البحث في اللوائح والقرارات الإدارية..."):
            all_chunks = read_all_chunks()
            
            relevant_context = get_relevant_context(q, all_chunks)
            
            prompt = f"""أنت مساعد آلي رسمي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.

التعليمات الصارمة:
1. قدم الإجابة النهائية المباشرة باللغة العربية فقط.
2. يمنع منعاً باتاً كتابة أفكارك أو خطوات البحث باللغة الإنجليزية.
3. استخرج الإجابة بناءً على النص المرجعي المرفق بأسلوب مهذب ومباشر.
4. إذا سُئلت عن اللجان أو التكاليف الخاصة بعضو معين، استخرج كافة اللجان والقرارات الإدارية التي ورد اسمه فيها مع ذكر اسم اللجنة ورقم/تاريخ القرار إن وجد.
5. إذا لم تجد الإجابة صراحة في النص المرجعي، وجّه الطالب بلباقة لمراجعة وحدة شؤون الطلبة.

النص المرجعي المستخرج:
{relevant_context}

سؤال الطالب: {q}

الإجابة النهائية (بالعربية فقط):"""

            ans = ""
            last_err = ""

            try:
                models_list = client.models.list().data
                valid_models = [
                    m.id for m in models_list 
                    if not any(x in m.id for x in ["whisper", "safetensors", "canopylabs", "guard", "vision"])
                ]

                for model_name in valid_models:
                    try:
                        completion = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "أنت مساعد آلي تجيب باللغة العربية المباشرة فقط دون تفكير بالإنجليزية."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.1,
                        )
                        if completion and completion.choices:
                            ans = completion.choices[0].message.content.strip()
                            break
                    except Exception as ex:
                        last_err = str(ex)
                        continue
            except Exception as e:
                last_err = str(e)

            if not ans:
                ans = f"عذراً، تعذر الاتصال بالذكاء الاصطناعي: {last_err}"

            st.markdown(f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True)

# 8. التنويه السفلي
st.markdown("""
<div class='disclaimer-box'>
تنبيـه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المستمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية:<br>
<a href='https://elearning.vision.edu.sa/course/view.php?id=788' target='_blank'>https://elearning.vision.edu.sa/course/view.php?id=788</a>
</div>
""", unsafe_allow_html=True)
