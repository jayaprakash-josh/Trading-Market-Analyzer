import json
import logging
import os
import requests
from config import LLM_PROVIDER
import time

logger = logging.getLogger(__name__)

def _build_analyst_prompt(symbol: str, technicals: dict, sector_data: dict, news: list, quant_bias: dict) -> str:
    """Builds a rigorous SEBI-compliant Catalyst Engine prompt."""
    import json
    sector_context = sector_data.get('sector_name', 'Unknown')
    rvol = technicals.get('RVOL', 'N/A')
    close = technicals.get('Close', 'N/A')
    
    prompt = f"""Modify the Watchlist Analysis application to replace the existing News Catalyst logic with a structured, evidence-based Catalyst Engine.

OBJECTIVE
---------
The goal is NOT to generate bullish/bearish sentiment from news articles. The goal is to identify whether there is a CURRENT, MATERIAL, FRESH, PRICE-RELEVANT catalyst for {symbol} ({sector_context}) that can plausibly affect the stock during the next trading session.

The catalyst engine must be conservative:
- Ignore generic positive/negative articles.
- Do not treat media sentiment as a catalyst by itself.
- Do not manufacture a catalyst when evidence is weak.
- Prefer 'NO MATERIAL CATALYST' over a weak or speculative catalyst.
- Catalyst direction must be independent from technical price direction.

DATA PRIORITY
-------------
Use evidence in this order:
1. NSE/BSE official corporate announcements and filings
2. Company exchange filings / investor relations disclosures
3. Official regulatory announcements
4. Company press releases
5. Reputable financial news
6. Other news/media sources
7. Social media/forums only as secondary context

LATEST DATA:
{json.dumps(news, indent=2)}

TECHNICAL CONFIRMATION CONTEXT (For your reference):
Stock Close: {close}
Relative Volume (RVOL): {rvol}

CATALYST LOOKBACK WINDOWS
--------------------------
Classify catalysts by age based on the article timestamps:
0-4 hours = VERY FRESH
4-24 hours = FRESH
1-3 days = RECENT
3-7 days = AGING
>7 days = OLD

NOVELTY / PRICED-IN TEST
------------------------
This is critical. Do NOT call something a strong catalyst merely because it is positive. Determine whether:
- the event is genuinely new
- the market has already reacted
- today's article merely repeats an old announcement

CATALYST SCORE
--------------
Create a deterministic score from 0 to 100.
Recency (20) + Materiality (25) + Source quality (15) + Novelty (15) + Expected business impact (25) = 100
Interpretation:
80-100 = STRONG
60-79 = MODERATE
40-59 = WEAK
0-39 = NONE
Do not force a catalyst when score <40.

OUTPUT FORMAT
-------------
You MUST output ONLY a valid JSON object matching the exact schema below. No markdown wrapping.
{{
  "catalyst_strength": "STRONG" | "MODERATE" | "WEAK" | "NONE",
  "direction": "BULLISH" | "BEARISH" | "MIXED" | "NEUTRAL",
  "score": <number between 0 and 100>,
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "freshness": "VERY FRESH" | "FRESH" | "RECENT" | "AGING" | "OLD",
  "confirmation": "CONFIRMED" | "PARTIAL" | "UNCONFIRMED",
  "catalyst_event": "One sentence describing the actual event",
  "why_it_matters": "One sentence explaining the economic/business relevance",
  "primary_source": "Source name + timestamp",
  "secondary_sources": ["list", "of", "sources"],
  "risk_caveat": "One short sentence",
  "catalyst_conflict": "If news is bullish but RVOL is < 0.8, write 'Positive news but lacks volume confirmation.' Or leave empty string"
}}
"""
    return prompt

def get_ai_analysis(symbol: str, technicals: dict, nse_data: dict, sentiment_data: dict, global_cues: dict, sector_data: dict, risk_warnings: list = None, quant_bias: dict = None) -> dict:
    """
    Calls the LLM strictly as a JSON classifier for news/catalysts.
    """
    news = sentiment_data.get('latest_news', [])
    
    prompt = _build_analyst_prompt(symbol, technicals, sector_data, news, quant_bias or {})
    
    provider = LLM_PROVIDER.lower()
    
    if provider == "groq":
        return _call_groq(prompt)
    elif provider == "google":
        return _call_google(prompt)
    else:
        logger.error(f"Unsupported LLM Provider: {provider}")
        return {"error": "Unsupported provider"}

def _call_google(prompt: str) -> dict:
    """Calls Google Gemini API using REST to avoid SDK version conflicts."""
    import requests
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable not set."}
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "You are a JSON-only API. You output raw JSON without markdown code blocks.\n" + prompt}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        data = response.json()
        
        if 'candidates' in data and len(data['candidates']) > 0:
            text = data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text)
        return {"error": "No candidates in response"}
    except Exception as e:
        return {"error": f"Gemini REST Error: {str(e)}"}

def _make_groq_request(prompt: str, api_key: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": "You are a JSON-only API. You output raw JSON and nothing else."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    if isinstance(parsed, list):
        return parsed[0] if parsed and isinstance(parsed[0], dict) else {}
    return parsed if isinstance(parsed, dict) else {}


def _call_groq(prompt: str) -> dict:
    """Calls Groq API using requests, with fallback, expecting JSON."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_api_key_1 = os.getenv("GROQ_API_KEY_1")
    
    if not groq_api_key:
        return {"error": "GROQ_API_KEY environment variable not set."}
        
    try:
        return _make_groq_request(prompt, groq_api_key)
    except Exception as e:
        if "429" in str(e) and groq_api_key_1:
            try:
                time.sleep(2)
                return _make_groq_request(prompt, groq_api_key_1)
            except Exception as fallback_e:
                return {"error": f"Groq fallback failed: {str(fallback_e)}"}
        return {"error": str(e)}
def get_macro_analysis(news: list) -> dict:
    prompt = f"""Act as a global macro analyst for the Indian Stock Market (NSE).
    Determine how the following global news will affect the Indian market today.
    
    NEWS:
    {json.dumps(news, indent=2)}
    
    OUTPUT FORMAT (Valid JSON only):
    {{
      "bias": "BULLISH",
      "reasoning": "Concise explanation of how this global news impacts India today"
    }}
    """
    try:
        import os
        import requests
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"error": "GROQ_API_KEY not found in environment."}
        
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": "You are a JSON-only API. Output raw valid JSON and nothing else."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return json.loads(content)
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}
