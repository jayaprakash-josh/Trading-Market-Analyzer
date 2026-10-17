import re

with open('core/llm.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_func = '''def _build_analyst_prompt(symbol: str, technicals: dict, sector_data: dict, news: list, quant_bias: dict) -> str:
    \"\"\"Builds a rigorous SEBI-compliant Catalyst Engine prompt.\"\"\"
    import json
    sector_context = sector_data.get('sector_name', 'Unknown')
    rvol = technicals.get('RVOL', 'N/A')
    close = technicals.get('Close', 'N/A')
    
    prompt = f\"\"\"Modify the Watchlist Analysis application to replace the existing News Catalyst logic with a structured, evidence-based Catalyst Engine.

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
\"\"\"
    return prompt
'''

pattern = re.compile(r'def _build_analyst_prompt.*?return prompt\n', re.DOTALL)
new_code = pattern.sub(new_func, code)

with open('core/llm.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print('Replaced _build_analyst_prompt successfully.')
