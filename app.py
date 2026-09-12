import os
import re
from flask import Flask, request, render_template_string, jsonify
from functools import lru_cache
import pymupdf
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
                doc = pymupdf.open(file)
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
        elif low.endswith((".
