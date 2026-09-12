import os
import re
from flask import Flask, request, render_template_string, jsonify
from functools import lru_cache
import fitz
from docx import Document
import pandas as pd
from groq import Groq

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def normalize_arabic(text):
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

@lru_cache(maxsize=1)
def read_all_chunks():
    chunks = []
    for file in os.listdir("."):
        if not os.path.isfile(os.path.join(".", file)):
            continue
        low = file.lower()
        if file.startswith(".") or low in ["app.py","requirements.txt"] or "venv" in low:
            continue
        if low.endswith(".pdf"):
            try:
                doc = fitz.open(file)
                for i, page in enumerate(doc):
                    try:
                        text = page.get_text("text")
                        if text and len(text.strip()) > 20:
                            if len(text) > 2000:
                                text = text[:2000]
                            chunks.append({"source": f"{file} (ص {i+1})", "text": text})
                    except:
                        continue
                doc.close()
            except:
                pass
        elif low.endswith(".docx"):
            try:
                doc = Document(file)
                txt = "\n".join([p.text for p in doc.paragraphs if p.text.strip()][:50])
                if txt:
                    chunks.append({"source": file, "text": txt[:2000]})
            except:
                pass
        elif low.endswith((".xlsx",".xls")):
            try:
                df = pd.read_excel(file, nrows=100).dropna(how='all')
                lines = []
                for _, row in df.iterrows():
                    row_str = " | ".join([str(v) for v in row.values if pd.notna(v)])
                    if row_str.strip():
                        lines.append(row_str[:200])
                    if len(lines) >= 30:
                        break
                if lines:
                    chunks.append({"source": file, "text": "\n".join(lines)[:2000]})
            except:
                pass
    return chunks

def get_relevant_context(query, chunks, max_chars=7000):
    norm_query = normalize_arabic(query)
    query_words = [w for w in norm_query.split() if len(w) > 2]
    scored = []
    for item in chunks:
        score = 0
        norm_text = normalize_arabic(item["text"])
        for w in query_words:
            if w in norm_text:
                score += 1
        if norm_query in norm_text:
            score += 10
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = ""
    for _, item in scored[:10]:
        entry = f"{item['source']}: {item['text']}\n\n"
        if len(selected) + len(entry) <= max_chars:
            selected += entry
    if not selected and chunks:
        selected = "\n".join([c["text"][:600] for c in chunks[:4]])
    return selected

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>كليات الرؤية - استفسار شؤون الطلبة</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
<style>
* { font-family: 'Tajawal', sans-serif; }
body { background: #fafaf9; margin:0; direction: rtl; }
.container { max-width: 800px; margin: 0 auto; padding: 30px 20px; }
.header { text-align:center; padding: 20px 0; }
.header h1 { font-size: 26px; margin:10px 0 5px; }
.header h2 { font-size: 18px; color: #8C7355; margin:0; }
.header p { color: #666; font-size: 15px; margin-top:10px; }
.search-box { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-top:20px; }
.search-box input { width:100%; padding:14px 16px; border:1.5px solid #e5e5e5; border-radius: 10px; font-size:16px; box-sizing: border-box; text-align:right; }
.search-box button { width:100%; margin-top:15px; background:#8C7355; color:white; border:none; padding:13px; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer; }
.answer-box { background:#f4f4f6; border-right:5px solid #8C7355; padding:20px; border-radius:10px; margin-top:20px; line-height:1.8; white-space: pre-wrap; }
.loader { text-align:center; padding:20px; display:none; color:#8C7355; }
.disclaimer { margin-top:50px; padding-top:15px; border-top:1px solid #e0e0e0; font-size:12px; color:#888; }
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
<input type="text" id="q" placeholder="مثال: من هو وكيل الكلية؟">
<button id="btn" onclick="ask()">للرد على استفسارك اضغط هنا</button>
<div class="loader" id="loader">جاري البحث في اللوائح...</div>
<div id="answer"></div>
</div>
<div class="disclaimer">تنبيه: اللوائح الرسمية عبر: <a href="https://elearning.vision.edu.sa/course/view.php?id=788" target="_blank">الرابط الرسمي</a></div>
</div>
<script>
async function ask(){
  const q = document.getElementById('q').value.trim();
  if(!q){ alert('اكتب السؤال'); return; }
  const btn = document.getElementById('btn'); const loader = document.getElementById('loader'); const answerDiv = document.getElementById('answer');
  btn.disabled = true; loader.style.display = 'block'; answerDiv.innerHTML = '';
  try {
    const res = await fetch('/ask', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question: q}) });
    const data = await res.json();
    if(data.answer){ answerDiv.innerHTML = `<div class="answer-box">${data.answer}</div>`; }
    else { answerDiv.innerHTML = `<div class="answer-box" style="border-color:red;background:#fff1f1;">${data.error}</div>`; }
  } catch(e){ answerDiv.innerHTML = `<div class="answer-box" style="border-color:red;">خطأ اتصال: ${e}</div>`; }
  btn.disabled = false; loader.style.display = 'none';
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string
