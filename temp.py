import json
def get_macro_analysis(news: list) -> dict:
    prompt = f\"\"\"Act as a global macro analyst for the Indian Stock Market (NSE).
    Determine how the following global news will affect the Indian market today.
    
    NEWS:
    {json.dumps(news, indent=2)}
    
    OUTPUT FORMAT (Valid JSON only):
    {{
      "bias": "BULLISH" | "BEARISH" | "NEUTRAL",
      "reasoning": "Concise explanation of how this global news impacts India today"
    }}
    \"\"\"
    try:
        from config import GROQ_API_KEY
        import requests
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return json.loads(content)
        else:
            return {"error": f"API Error {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
