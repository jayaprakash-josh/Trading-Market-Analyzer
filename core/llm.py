import json
import logging
import os
import requests
from config import LLM_PROVIDER
import time

logger = logging.getLogger(__name__)

def _build_analyst_prompt(symbol: str, sector_context: str, news: list, quant_bias: dict) -> str:
    """
    Builds a prompt that forces the LLM to classify news and return structured JSON.
    """
    bias_direction = quant_bias.get('direction', 'UNKNOWN')
    bias_strength = quant_bias.get('bias_strength', 0)
    
    prompt = f"""You are a strict financial news classifier for the NSE stock market.
The Python Quant Engine has already analyzed all technicals, options, and volume data for {symbol} ({sector_context}) and locked in the following score:
BIAS STRENGTH: {bias_strength} ({bias_direction})

Your ONLY job is to read the latest news headlines below and classify if they conflict with the Quant Engine's bias.

NEWS HEADLINES:
{json.dumps(news, indent=2)}

RULES:
1. ONLY use facts explicitly present in the supplied text. Do not invent numbers.
2. If the news is highly negative (e.g. fraud, major earnings miss) but the Quant Bias is BULLISH, set "conflicts_with_bias" to true.
3. You must output ONLY a valid JSON object matching the exact schema below. No markdown formatting, no backticks, no conversational text.

SCHEMA:
{{
  "direction": "positive|negative|neutral",
  "severity": "none|low|medium|high|critical",
  "catalyst_type": "earnings|order|regulatory|management|corporate_action|other",
  "conflicts_with_bias": true|false,
  "source_quality": "primary|high|medium|low",
  "comment": "Brief 2-sentence explanation of the news impact."
}}
"""
    return prompt

def get_ai_analysis(symbol: str, technicals: dict, nse_data: dict, sentiment_data: dict, global_cues: dict, sector_data: dict, risk_warnings: list = None, quant_bias: dict = None) -> dict:
    """
    Calls the LLM strictly as a JSON classifier for news/catalysts.
    """
    news = sentiment_data.get('latest_news', [])
    sector_context = sector_data.get('sector_name', 'Unknown')
    
    prompt = _build_analyst_prompt(symbol, sector_context, news, quant_bias or {})
    
    provider = LLM_PROVIDER.lower()
    
    if provider == "groq":
        return _call_groq(prompt)
    else:
        logger.error(f"Unsupported LLM Provider: {provider}")
        return {"error": "Unsupported provider"}

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
