import os
import re
from flask import Flask, request, render_template_string, jsonify
from functools import lru_cache
import pymupdf
from docx import Document
import pandas as pd
from google import genai

app = Flask(__name__)

# إعداد Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def normalize_arabic(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def clean_llm_response(text):
    if not text:
        return ""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    if "Here's" in text or "Analyze User Input" in text:
        match = re.search(r'[\u0600-\u06FF].*', text, re.DOTALL)
        if match:
            text = match.group(0)
    lines = [line for line in text.split('\n') if not re.match(r'^\s*:[A-Za-z\s]+\d*', line)]
    return "\n".join(lines).strip()

@lru_cache(maxsize=1)
def read_all_chunks():
    chunks = []
    for file in os.listdir("."):
        if not os.path.isfile(os.path.join(".", file)):
            continue
        low = file.lower()
        if file.startswith(".") or low in ["app.py", "requirements.txt"] or "venv" in low:
            continue
            
        if low.endswith(".pdf"):
            try:
                doc = pymupdf.open(file)
                for i, page in enumerate(doc):
                    try:
                        text = page.get_text("text")
                        if text and len(text.strip()) > 20:
                            if len(text) > 3000:
                                text = text[:3000]
                            chunks.append({"source": f"{file} (ص {i+1})", "text": text})
                    except Exception:
                        continue
                doc.close()
            except Exception:
                pass
                
        elif low.endswith(".docx"):
            try:
                doc = Document(file)
                txt = "\n".join([p.text for p in doc.paragraphs if p.text.strip()][:100])
                if txt:
                    chunks.append({"source": file, "text": txt[:3000]})
            except Exception:
                pass
                
        elif low.endswith((".xlsx", ".xls")):
            try:
                excel_file = pd.ExcelFile(file)
                for sheet in excel_file.sheet_names:
                    # قراءة 500 صف فقط لتوفير التوكنات
                    df = pd.read_excel(file, sheet_name=sheet, nrows=500).dropna(how='all')
                    lines = []
                    for _, row in df.iterrows():
                        row_str = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                        if row_str.strip():
                            lines.append(row_str[:400])
                    if lines:
                        chunks.append({"source": f"{file} ({sheet})", "text": "\n".join(lines)})
            except Exception:
                pass
                
        elif low.endswith(".txt"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    txt = f.read()
                    if txt and len(txt.strip()) > 20:
                        chunks.append({"source": file, "text": txt[:3000]})
            except Exception:
                pass
                
    return chunks

def get_relevant_context(query, chunks, max_chars=12000):
    norm_query = normalize_arabic(query)
    stop_words = ["ما", "هي", "من", "في", "على", "عن", "التي", "الذي", "ماهي", "اين", "اللجان", "الوحدات"]
    query_words = [w for w in norm_query.split() if len(w) > 2 and w not in stop_words]
    
    scored = []
    for item in chunks:
        score = 0
        norm_text = normalize_arabic(item["text"])
        for w in query_words:
            if w in norm_text:
                score += 2
        if norm_query in norm_text:
            score += 20
        if score > 0:
            scored.append((score, item))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    
    selected = ""
    # اختيار أفضل 5 أجزاء فقط لتقليل حجم الطلب
    for _, item in scored[:5]:
        entry = f"المصدر [{item['source']}]:\n{item['text']}\n\n"
        if len(selected) + len(entry) <= max_chars:
            selected += entry
            
    if not selected and chunks:
        selected = "\n".join([c["text"][:500] for c in chunks[:3]])
        
    return selected

# ... (باقي كود HTML_TEMPLATE والـ routes كما هو تماماً دون أي تغيير) ...

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        q = data.get("question", "").strip()
        if not q:
            return jsonify({"error": "يرجى كتابة السؤال"})
        if not client:
            return jsonify({"error": "GEMINI_API_KEY غير موجود في Render"})
            
        chunks = read_all_chunks()
        context = get_relevant_context(q, chunks, max_chars=12000)
        
        # النماذج الرسمية الحديثة من Gemini
        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.1-pro-preview"
        ]
        
        prompt = f"""أنت مساعد آلي رسمي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.

التعليمات:
1. أجب باللغة العربية المباشرة والواضحة فقط، وبإيجاز شديد.
2. لا تكتب أي تفكير أو جمل إنجليزية.
3. استخرج الإجابة بدقة من النص المرجعي.
4. إذا سأل الطالب عن اسم شخص (مثل "ملاذ") أو عن لجانه ووحداته، اذكر **كل اللجان** التي ورد فيها هذا الاسم في النص المرجعي.
5. إذا لم تجد الإجابة، أجب بـ: "عذراً، لا توجد معلومات صريحة في المصادر المرفقة. يُرجى مراجعة وحدة شؤون الطلبة."

النص المرجعي:
{context}

سؤال الطالب: {q}

الإجابة المباشرة:"""

        last_err = ""
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                raw_ans = response.text.strip()
                ans = clean_llm_response(raw_ans)
                if ans:
                    return jsonify({"answer": ans})
            except Exception as e:
                last_err = str(e)
                continue
                
        return jsonify({"error": f"تعذر الاتصال بكافة النماذج. آخر خطأ: {last_err[:400]}"})
    except Exception as e:
        return jsonify({"error": f"خطأ داخلي: {str(e)[:500]}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
