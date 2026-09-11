import os
import fitz  # PyMuPDF
from docx import Document
import pandas as pd
import pdfplumber
from groq import Groq
import streamlit as st

# 1. إعداد الصفحة والتصميم
st.set_page_config(
    page_title="استفسار شؤون الطلبة - كليات الرؤية",
    page_icon="🎓",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    html, body, [class*="css"], div, p, span, input, button {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stApp { direction: rtl !important; text-align: right !important; }
    .stTextInput input { text-align: right !important; direction: rtl !important; }
    
    .stButton button {
        width: 100% !important;
        background-color: #8C7355 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: none !important;
    }
    .stButton button:hover { background-color: #6e5a42 !important; color: white !important; }
    
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
""",
    unsafe_allow_html=True,
)

# 2. الشعار والعناوين
if os.path.exists("Logo.png"):
    st.image("Logo.png", width=160)

st.title("كليات الرؤية - Vision Colleges")
st.subheader("الاستفسار الآلي - وحدة شؤون الطلبة")
st.write(
    "مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية."
)

# 3. إعداد Groq Client
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None


# 4. دالة متطورة لقراءة الإكسيل والـ PDF والـ Word
@st.cache_data(ttl=3600)
def read_all_chunks():
    chunks = []
    folder_path = "."

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        # قراءة ملفات PDF
        if file.endswith(".pdf"):
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text and len(text.strip()) > 5:
                            chunks.append(
                                {"source": f"{file} (صفحة {i+1})", "text": text}
                            )
            except Exception:
                try:
                    doc = fitz.open(file_path)
                    for i, page in enumerate(doc):
                        text = page.get_text()
                        if text and len(text.strip()) > 5:
                            chunks.append(
                                {"source": f"{file} (صفحة {i+1})", "text": text}
                            )
                except Exception:
                    pass

        # قراءة ملفات Word
        elif file.endswith(".docx"):
            try:
                doc = Document(file_path)
                full_text = [p.text for p in doc.paragraphs if p.text.strip()]
                if full_text:
                    chunks.append({"source": file, "text": "\n".join(full_text)})
            except Exception:
                pass

        # قراءة ملفات Excel وتحويل كل صف لنص مقروء صراحة
        elif file.endswith(".xlsx") or file.endswith(".xls"):
            try:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    df = df.fillna("")  # تفريغ الخانات الفارغة

                    sheet_lines = []
                    for idx, row in df.iterrows():
                        row_str = " | ".join(
                            [
                                f"{col}: {val}"
                                for col, val in row.items()
                                if str(val).strip() != ""
                            ]
                        )
                        if row_str.strip():
                            sheet_lines.append(row_str)

                    full_sheet_text = "\n".join(sheet_lines)
                    if full_sheet_text:
                        chunks.append(
                            {
                                "source": f"{file} (ورقة: {sheet_name})",
                                "text": full_sheet_text,
                            }
                        )
            except Exception as e:
                pass

    return chunks


# 5. دالة تصفية واختيار النصوص المناسبة
def get_relevant_context(query, chunks, max_chars=12000):
    query_words = [
        w.strip().lower() for w in query.split() if len(w.strip()) > 1
    ]

    scored_chunks = []
    for item in chunks:
        score = 0
        text_lower = item["text"].lower()
        for word in query_words:
            if word in text_lower:
                score += 3  # إعطاء مطابقة الكلمات وزناً أسرع

        # إعطاء أولوية لملفات الإكسيل والإيميلات عند وجود كلمة إيميل أو بريد أو عضو
        if any(
            k in query.lower()
            for k in ["إيميل", "ايميل", "بريد", "دكتور", "أستاذ", "استاذ", "من هو"]
        ):
            if "xlsx" in item["source"] or "xls" in item["source"]:
                score += 5

        scored_chunks.append((score, item))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    selected_text = ""
    for score, item in scored_chunks:
        chunk_entry = f"--- المصدر: {item['source']} ---\n{item['text']}\n\n"
        if len(selected_text) + len(chunk_entry) <= max_chars:
            selected_text += chunk_entry
        else:
            break

    return selected_text


# 6. المدخلات والاستعلام
q = st.text_input(
    "أدخل استفسارك هنا:",
    placeholder="ما هي المدة المسموح بها لتقديم عذر الوفاة؟",
)
btn = st.button("للرد على استفسارك اضغط هنا")

if btn or q:
    if not q.strip():
        st.warning("يرجى كتابة السؤال أولاً.")
    elif not client:
        st.error("مفتاح GROQ_API_KEY غير معرف في بيئة العمل.")
    else:
        with st.spinner("جاري البحث في الملفات واللوائح..."):
            all_chunks = read_all_chunks()
            relevant_context = get_relevant_context(q, all_chunks)

            prompt = f"""أنت مساعد آلي رسمي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.

التعليمات الصارمة:
1. قدم الإجابة النهائية المباشرة باللغة العربية فقط.
2. يمنع منعاً باتاً كتابة أفكارك أو تفكيرك أو أي جمل باللغة الإنجليزية.
3. استخرج الإجابة المباشرة (مثل البريد الإلكتروني أو المعلومة) من النص المرجعي أدناه.
4. إذا لم تجد الإجابة صراحة في النص، وجّه الطالب بلباقة لمراجعة وحدة شؤون الطلبة.

النص المرجعي المستخرج من الملفات:
{relevant_context}

سؤال الطالب: {q}

الإجابة النهائية المباشرة بالعربية:"""

            ans = ""
            try:
                # استخدام النموذج المستقر والسريع llama-3.1-8b-instant أو llama3-70b-8192
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "أجب باللغة العربية المباشرة فقط دون كتابة أفكار إنجليزية.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )
                if completion and completion.choices:
                    ans = completion.choices[0].message.content.strip()
            except Exception as ex:
                ans = f"حدث خطأ أثناء الاتصال بالنموذج: {str(ex)}"

            st.markdown(
                f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True
            )

# 7. التنويه السفلي
st.markdown(
    """
<div class='disclaimer-box'>
تنبيـه: هذا برنامج رد آلي ويمكن أن تكون الإجابات في بعض الأحيان غير دقيقة، وعليه تعتبر اللوائح والأنظمة الرسمية المستمدة والمعلنة عبر الرابط التالي هي المرجع المعتمد والأخير للكلية:<br>
<a href='https://elearning.vision.edu.sa/course/view.php?id=788' target='_blank'>https://elearning.vision.edu.sa/course/view.php?id=788</a>
</div>
""",
    unsafe_allow_html=True,
)
