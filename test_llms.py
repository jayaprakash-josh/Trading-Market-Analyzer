import os
import json
import time
from dotenv import load_dotenv

from groq import Groq
from core.technicals import fetch_and_calculate_technicals
from core.nse_data import get_nse_data
from core.sentiment import fetch_stock_news, fetch_fii_dii_data
from core.macros import fetch_global_cues
from core.llm import NpEncoder

load_dotenv()

def test_both_llms():
    print("Fetching data for benchmarking...")
    symbol = "WABAG"
    sector = "Water infrastructure / EPC"
    
    fii_dii = fetch_fii_dii_data()
    global_cues = fetch_global_cues()
    technicals = fetch_and_calculate_technicals(f"{symbol}.NS")
    nse_data = get_nse_data(symbol)
    news = fetch_stock_news(symbol, limit=2)
    sentiment_data = {"fii_dii_flow": fii_dii, "latest_news": news}
    
    prompt = f"""
    You are an expert Indian Stock Market Quantitative Trader. 
    Analyze the following 09:10 AM Pre-Market data for {symbol} ({sector}) and generate a highly actionable intraday trading plan.
    
    # 1. Global & Market Context
    {json.dumps(global_cues, indent=2, cls=NpEncoder)}
    
    # 2. Technicals
    {json.dumps(technicals, indent=2, cls=NpEncoder)}
    
    # 3. NSE Live Data
    {json.dumps(nse_data, indent=2, cls=NpEncoder)}
    
    # 4. Macro & Sentiment
    {json.dumps(sentiment_data, indent=2, cls=NpEncoder)}
    
    SCORING MATRIX (-10 to +10):
    Evaluate the stock across 5 pillars, scoring each from -2 (Bearish) to +2 (Bullish).
    1. Trend
    2. Derivatives/OI
    3. Catalyst/News
    4. Market Regime
    5. Delivery & Pre-Open Strength
    
    VETO RULE: If the Catalyst/News is deeply negative (-2), cap total score at 0 and forbid LONG setups.
    
    You MUST respond EXCLUSIVELY with a JSON object matching this exact schema:
    {{
      "directional_score": "Integer from -10 to 10",
      "signal": "GO LONG, GO SHORT, WAIT, or NO-TRADE",
      "confidence": "High, Medium, or Low",
      "trend": "A 1-sentence summary of the prevailing trend",
      "key_levels": "Exact prices for Support and Resistance",
      "trade_plan": "Exact entry triggers, targets, and stop-loss",
      "risks": "Risks to watch out for"
    }}
    """
    
    print("\n==================================================")
    print("1. TESTING GROQ (llama-3.3-70b-versatile)")
    print("==================================================")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    start_time = time.time()
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Output exclusively in JSON format."}, {"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        groq_result = json.loads(completion.choices[0].message.content)
        groq_time = time.time() - start_time
        print(f"Time Taken: {groq_time:.2f} seconds")
        print(json.dumps(groq_result, indent=2))
    except Exception as e:
        print(f"Groq Error: {e}")

    print("\n==================================================")
    print("2. TESTING GEMINI (gemini-2.5-flash)")
    print("==================================================")
    try:
        from google import genai
        from google.genai import types
        gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        start_time = time.time()
        response = gemini_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        gemini_result = json.loads(response.text)
        gemini_time = time.time() - start_time
        print(f"Time Taken: {gemini_time:.2f} seconds")
        print(json.dumps(gemini_result, indent=2))
    except Exception as e:
        print(f"Gemini Error: {e}")

if __name__ == "__main__":
    test_both_llms()
