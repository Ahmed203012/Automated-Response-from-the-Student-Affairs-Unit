def generate_direct_answer(query, db):
    if not GEMINI_API_KEY:
        return "⚠️ لم يتم العثور على `GEMINI_API_KEY` في Streamlit Secrets."

    relevant_context = get_relevant_context(query, db)
    
    if not relevant_context:
        return "لم أجد نصاً صريحاً يتعلق باستفسارك في اللوائح المرفقة."

    prompt = f"""
    أنت مساعد أكاديمي ذكي. أجب على سؤال الطالب بناءً على النص المقتطع التالي فقط.

    النص المقتطع من اللائحة:
    \"\"\"
    {relevant_context}
    \"\"\"

    سؤال الطالب: "{query}"

    التعليمات:
    1. أجب بأسلوب مباشر ومقتضب جداً (في سطر أو سطرين فقط).
    2. اذكر المهل والشروط والأرقام فوراً.
    3. لا تطبع النص الكامل للائحة.
    """

    # الرابط الجديد المباشر عبر الإصدار v1 المعتمد
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_json = response.json()
        
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            err_msg = res_json.get('error', {}).get('message', str(res_json))
            return f"❌ خطأ من الخادم ({response.status_code}):\n\n`{err_msg}`"
    except Exception as e:
        return f"❌ خطأ في الاتصال الشبكي: `{str(e)}`"
