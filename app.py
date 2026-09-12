import os
import re
from flask import Flask, request, render_template_string, jsonify
from functools import lru_cache
import pymupdf
from docx import Document
import pandas as pd
from groq import Groq

app = Flask(__name__)

# إعداد Groq Client
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

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
                    # قراءة حتى 2000 صف لضمان عدم تفويت أي اسم
                    df = pd.read_excel(file, sheet_name=sheet, nrows=2000).dropna(how='all')
                    lines = []
                    for _, row in df.iterrows():
                        row_str = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                        if row_str.strip():
                            lines.append(row_str[:500])
                    if lines:
                        # عدم قطع النص عند حد معين، وترك المساحة للذكاء الاصطناعي
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

def get_relevant_context(query, chunks, max_chars=25000):
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
            score += 20 # مضاعفة النقاط عند وجود تطابق حرفي
        if score > 0:
            scored.append((score, item))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    
    selected = ""
    # زيادة عدد الأجزاء المختارة لضمان جمع كل اللجان المذكورة في الملفات
    for _, item in scored[:20]:
        entry = f"المصدر [{item['source']}]:\n{item['text']}\n\n"
        if len(selected) + len(entry) <= max_chars:
            selected += entry
            
    if not selected and chunks:
        selected = "\n".join([c["text"][:800] for c in chunks[:6]])
        
    return selected

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>كليات الرؤية - استفسار شؤون الطلبة</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
<style>
* { font-family: 'Tajawal', sans-serif; box-sizing: border-box; }
body { background: #fafaf9; margin:0; padding:0; direction: rtl; text-align: right; }
.container { max-width: 800px; margin: 0 auto; padding: 30px 20px; }
.header { text-align:center; padding: 20px 0; }
.header h1 { font-size: 26px; margin:10px 0 5px; color: #1a1a1a; }
.header h2 { font-size: 18px; color: #8C7355; margin:0; }
.header p { color: #666; font-size: 15px; margin-top:10px; }
.search-box { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-top:20px; }
.search-box input { width:100%; padding:14px 16px; border:1.5px solid #e5e5e5; border-radius: 10px; font-size:16px; text-align:right; direction:rtl; }
.search-box input:focus { outline:none; border-color:#8C7355; }
.search-box button { width:100%; margin-top:15px; background:#8C7355; color:white; border:none; padding:13px; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer; }
.search-box button:hover { background:#6e5a42; }
.answer-box { background:#f4f4f6; border-right:5px solid #8C7355; padding:20px; border-radius:10px; margin-top:20px; line-height:1.8; white-space: pre-wrap; font-size: 16px; color: #222; }
.loader { text-align:center; padding:20px; display:none; color:#8C7355; font-weight:bold; }
.disclaimer { margin-top:50px; padding-top:15px; border-top:1px solid #e0e0e0; font-size:12px; color:#888; text-align:right; line-height: 1.6; }
.disclaimer a { color:#8C7355; text-decoration:none; font-weight:bold; }
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>كليات الرؤية - Vision Colleges</h1>
<h2>الاستفسار الآلي - وحدة شؤون الطلبة</h2>
<p>مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية والأنشطة الطلابية.</p>
</div>

<div class="search-box">
<input type="text" id="q" placeholder="مثال: من هو وكيل الكلية؟" onkeypress="if(event.key==='Enter') ask()">
<button id="btn" onclick="ask()">للرد على استفسارك اضغط هنا</button>
<div class="loader" id="loader">جاري البحث في اللوائح والقرارات...</div>
<div id="answer"></div>
</div>

<div class="disclaimer">
تنبيه: هذا برنامج رد آلي. اللوائح الرسمية المعلنة عبر الرابط التالي هي المرجع المعتمد:<br>
<a href="https://elearning.vision.edu.sa/course/view.php?id=788" target="_blank">https://elearning.vision.edu.sa/course/view.php?id=788</a>
</div>
</div>

<script>
async function ask(){
  const q = document.getElementById('q').value.trim();
  if(!q){ alert('يرجى كتابة السؤال أولاً'); return; }
  const btn = document.getElementById('btn'); 
  const loader = document.getElementById('loader'); 
  const answerDiv = document.getElementById('answer');
  
  btn.disabled = true; 
  loader.style.display = 'block'; 
  answerDiv.innerHTML = '';
  
  try {
    const res = await fetch('/ask', { 
      method:'POST', 
      headers:{'Content-Type':'application/json'}, 
      body: JSON.stringify({question: q}) 
    });
    const data = await res.json();
    if(data.answer){ 
      answerDiv.innerHTML = `<div class="answer-box">${data.answer}</div>`; 
    } else { 
      answerDiv.innerHTML = `<div class="answer-box" style="border-color:#ef4444;background:#fef2f2;">${data.error || 'حدث خطأ'}</div>`; 
    }
  } catch(e){ 
    answerDiv.innerHTML = `<div class="answer-box" style="border-color:#ef4444;background:#fef2f2;">خطأ اتصال بالسيرفر</div>`; 
  }
  btn.disabled = false; 
  loader.style.display = 'none';
}
</script>
</body>
</html>
"""

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
            return jsonify({"error": "GROQ_API_KEY غير موجود في Render"})
            
        chunks = read_all_chunks()
        context = get_relevant_context(q, chunks, max_chars=25000)
        
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]
        
        # تم تحسين التعليمات لضمان البحث عن الاسم في كل السطور وذكر جميع اللجان
        prompt = f"""أنت مساعد آلي رسمي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.

التعليمات:
1. أجب باللغة العربية المباشرة والواضحة فقط.
2. لا تكتب أي تفكير أو جمل إنجليزية.
3. استخرج الإجابة بدقة وبإيجاز من النص المرجعي.
4. إذا سأل الطالب عن اسم شخص (مثل "ملاذ" أو "أحمد مرسي") أو عن لجانه ووحداته، يجب عليك قراءة كامل النص المرجعي والبحث عن هذا الاسم بدقة، ثم ذكر **كل اللجان أو الوحدات** التي ورد فيها هذا الاسم دون استثناء أو نسيان أي منها. لا تكتفِ بذكر لجنة واحدة.
5. ركز جيداً على الأسماء والإيميلات وأرقام التواصل إن وجدت في النص المرجعي.
6. إذا لم تجد الإجابة بعد البحث الكامل، أجب بـ: "عذراً، لا توجد معلومات صريحة في المصادر المرفقة. يُرجى مراجعة وحدة شؤون الطلبة."

النص المرجعي:
{context}

سؤال الطالب: {q}

الإجابة المباشرة:"""

        last_err = ""
        for model_name in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "أنت مساعد يجيب باللغة العربية المباشرة فقط."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2048
                )
                raw_ans = completion.choices[0].message.content.strip()
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
