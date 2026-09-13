import os
import re
import base64
from flask import Flask, request, render_template_string, jsonify, send_from_directory
from functools import lru_cache
import pymupdf
from docx import Document
import pandas as pd
from groq import Groq

# استيراد البيانات الثابتة من قاعدة المعرفة
try:
    from knowledge_base import HARDCODED_DATA
except ImportError:
    HARDCODED_DATA = []

app = Flask(__name__)

# إعداد العميل لخدمة Groq API
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def get_logo_base64():
    """تحويل صورة الشعار إلى Base64 للعرض المباشر"""
    for fname in ["logo.png", "logo.jpg", "logo.jpeg"]:
        if os.path.exists(fname):
            try:
                with open(fname, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    ext = fname.split('.')[-1]
                    return f"data:image/{ext};base64,{encoded}"
            except Exception:
                pass
    return "logo.png"

def normalize_arabic(text):
    """توحيد وتنظيف النصوص العربية للبحث"""
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'[إأآآ]', 'ا', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def clean_llm_response(text):
    """تنظيف وتنسيق إجابة النموذج"""
    if not text:
        return ""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    if "Here's" in text or "Analyze User Input" in text:
        match = re.search(r'[\u0600-\u06FF].*', text, re.DOTALL)
        if match:
            text = match.group(0)
    lines = [line for line in text.split('\n') if not re.match(r'^\s*:[A-Za-z\s]+\d*', line)]
    unique_lines = []
    for line in lines:
        if not unique_lines or line.strip() != unique_lines[-1].strip():
            unique_lines.append(line)
    return "\n".join(unique_lines).strip()

@lru_cache(maxsize=1)
def read_all_chunks():
    """قراءة وتحميل جميع النصوص من الملف الثابت والمستندات المحلية"""
    chunks = list(HARDCODED_DATA)
    
    for file in os.listdir("."):
        if not os.path.isfile(os.path.join(".", file)):
            continue
        low = file.lower()
        if file.startswith(".") or low in ["app.py", "requirements.txt", "knowledge_base.py"] or "venv" in low:
            continue
            
        try:
            if low.endswith(".pdf"):
                doc = pymupdf.open(file)
                for i, page in enumerate(doc):
                    try:
                        text = page.get_text("text")
                        if text and len(text.strip()) > 20:
                            chunks.append({"source": f"{file} (ص {i+1})", "text": text[:3000]})
                    except:
                        continue
                doc.close()
            elif low.endswith(".docx"):
                doc = Document(file)
                txt = "\n".join([p.text for p in doc.paragraphs if p.text.strip()][:150])
                if txt:
                    chunks.append({"source": file, "text": txt[:3000]})
            elif low.endswith((".xlsx", ".xls")):
                excel_file = pd.ExcelFile(file)
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(file, sheet_name=sheet, nrows=500).dropna(how='all')
                    lines = []
                    for _, row in df.iterrows():
                        row_str = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                        if row_str.strip():
                            lines.append(row_str[:300])
                    if lines:
                        chunks.append({"source": f"{file} ({sheet})", "text": "\n".join(lines)})
            elif low.endswith(".txt"):
                with open(file, 'r', encoding='utf-8') as f:
                    txt = f.read()
                    if txt and len(txt.strip()) > 20:
                        chunks.append({"source": file, "text": txt[:3000]})
        except Exception as file_err:
            print(f"Error reading file {file}: {file_err}")
            continue
                
    return chunks

def get_relevant_context(query, chunks, max_chars=30000):
    """استخراج أفضل النصوص المرجعية المرتبطة بسؤال الطالب (تم زيادة الحجم بشكل كبير)"""
    norm_query = normalize_arabic(query)
    stop_words = ["ما", "هي", "من", "في", "على", "عن", "التي", "الذي", "ماهي", "اين", "اللجان", "الوحدات"]
    query_words = [w for w in norm_query.split() if len(w) > 2 and w not in stop_words]
    
    scored = []
    for item in chunks:
        score = 0
        norm_text = normalize_arabic(item["text"])
        for w in query_words:
            if w in norm_text:
                score += 5 # زيادة وزن الكلمة المطابقة
        if norm_query in norm_text:
            score += 30 # زيادة وزن التطابق الدقيق
        # إذا كان السؤال يحتوي على اسم علم (كلمة تبدأ بـ "د." أو "أ." أو اسم شخص)
        if any(name_part in query for name_part in ["د.", "أ.", "الدكتور", "الأستاذ", "دكتور", "استاذ"]):
            # البحث عن مطابقة دقيقة لأسماء الأشخاص في النص
            name_matches = re.findall(r'(?:د\.|أ\.)\s*[\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+)*', query)
            for match in name_matches:
                if match in item["text"]:
                    score += 50 # إعطاء أولوية قصوى لأسماء الأشخاص
        if score > 0:
            scored.append((score, item))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    
    selected = ""
    # زيادة عدد الأجزاء المستخرجة لضمان شمولية المعلومات
    for _, item in scored[:20]:
        entry = f"المصدر [{item['source']}]:\n{item['text']}\n\n"
        if len(selected) + len(entry) <= max_chars:
            selected += entry
            
    if not selected and chunks:
        selected = "\n".join([c["text"][:1000] for c in chunks[:5]])
        
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
.header img { max-height: 110px; width: auto; margin-bottom: 15px; display: inline-block; }
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
.disclaimer-box { 
    background-color: #f4f4f6; 
    color: #222; 
    padding: 15px; 
    border-radius: 10px; 
    margin-top: 30px; 
    font-size: 12px; 
    line-height: 1.6; 
    text-align: right;
    border-right: 5px solid #8C7355;
}
.disclaimer-title {
    font-size: 16px;
    font-weight: bold;
    color: #8C7355;
    margin-bottom: 8px;
    display: block;
}
.disclaimer-box a { 
    color: #8C7355; 
    text-decoration: underline; 
    font-weight: bold; 
}
.disclaimer-box a:hover { 
    color: #6e5a42; 
    text-decoration: none; 
}
</style>
</head>
<body>
<div class="container">
<div class="header">
<img src="{{ logo_src }}" alt="شعار كليات الرؤية">
<h1>كليات الرؤية - Vision Colleges</h1>
<h2>الاستفسار الآلي - وحدة شؤون الطلبة</h2>
<p>مرحباً بكم في كلية الرؤية بالرياض، نرحب باستفساراتكم حول لوائح وأنظمة الكلية والأنشطة الطلابية.</p>
</div>

<div class="search-box">
<input type="text" id="q" placeholder="اكتب استفسارك هنا..." onkeypress="if(event.key==='Enter') ask()">
<button id="btn" onclick="ask()">للرد على استفسارك اضغط هنا</button>
<div class="loader" id="loader">جاري البحث في اللوائح والقرارات...</div>
<div id="answer"></div>
</div>

<div class="disclaimer-box">
    <span class="disclaimer-title">تنويه</span>
    <p style="margin: 0 0 8px 0;">هذا المساعد برنامج آلي يهدف إلى تقديم معلومات وإرشادات للطلاب، وقد لا تكون جميع إجاباته دقيقة أو محدثة بشكل كامل. لذلك، لا تُعد إجابات المساعد الآلي مرجعًا رسميًا أو ملزمًا للكلية.</p>
    <p style="margin: 0 0 8px 0;">ويُعد المرجع الرسمي والمعتمد لجميع اللوائح والأنظمة والتعليمات الأكاديمية هو ما يتم نشره عبر الرابط الرسمي للكلية أدناه:</p>
    <p style="margin: 0 0 8px 0;"><a href="https://elearning.vision.edu.sa/course/view.php?id=188" target="_blank">https://elearning.vision.edu.sa/course/view.php?id=188</a></p>
    <p style="margin: 0;">وفي حال وجود أي تعارض بين إجابة المساعد وما هو منشور في الرابط الرسمي، يُعتد بما ورد في الرابط الرسمي للكلية.</p>
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
    logo_src = get_logo_base64()
    return render_template_string(HTML_TEMPLATE, logo_src=logo_src)

@app.route("/<path:filename>")
def serve_static(filename):
    if filename in ["logo.png", "logo.jpg", "logo.jpeg"]:
        return send_from_directory(".", filename)
    return "Not Found", 404

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        q = data.get("question", "").strip()
        if not q:
            return jsonify({"error": "يرجى كتابة السؤال"})
        if not client:
            return jsonify({"error": "GROQ_API_KEY غير موجود في إعدادات البيئة"})
            
        chunks = read_all_chunks()
        context = get_relevant_context(q, chunks, max_chars=30000) # زيادة حجم السياق
        
        models_to_try = [
            "llama-3.3-70b-versatile",
            "allam-2-7b",
            "llama3-70b-8192"
        ]
        
        prompt = f"""أنت مساعد آلي رسمي لوحدة شؤون الطلبة في كليات الرؤية بالرياض.

التعليمات الهامة جداً للإجابة:
1. أجب باللغة العربية المباشرة والواضحة فقط، وبإيجاز.
2. اعتمد كلياً على النصوص والقرارات المرفقة في السياق المرجعي.
3. عند الاستفسار عن اسم شخص (مثل: "د. أحمد مرسي" أو "أ. ملاذ") أو عن لجانه أو وحداته:
   - يجب عليك البحث عن هذا الاسم في **كافة أجزاء السياق المرجعي** المرفق.
   - ثم قم بجمع **كل** اللجان أو الوحدات التي ورد فيها هذا الاسم (مثل: لجنة الأعذار، وحدة البحث العلمي، لجنة الاختبارات، إلخ) واذكرها في قائمة واضحة.
   - لا تكتفِ بذكر لجنة واحدة فقط، بل اذكر جميع اللجان التي تم العثور عليها.
4. عند الاستفسار عن الأنشطة الطلابية لشهر معين، يجب تجميع كافة الأنشطة من جميع اللجان. ويمنع منعاً باتاً ذكر أي ميزانيات أو مبالغ مالية.
5. لا تكرر إجابتك، واكتبها مرة واحدة فقط في نهاية الرد.
6. إذا لم تجد الإجابة في النص المرجعي، أجب بـ: "عذراً، لا توجد معلومات صريحة في المصادر المرفقة. يُرجى مراجعة وحدة شؤون الطلبة."

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
                        {"role": "system", "content": "أنت مساعد دقيق يجيب باللغة العربية المباشرة. لا تكرر الإجابة. ابحث عن الأسماء في كل النص."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1500
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
