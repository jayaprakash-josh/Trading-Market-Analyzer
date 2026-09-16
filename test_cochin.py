import sys
import os
import json
from core.technicals import fetch_and_calculate_technicals
from core.nse_data import get_nse_data
from core.sentiment import fetch_stock_news, fetch_fii_dii_data
from core.macros import fetch_global_cues
from core.llm import generate_premarket_analysis

# Just analyze Cochin Shipyard
symbol = "COCHINSHIP"
sector = "Defence / Shipbuilding / Government PSU"

print(f"Gathering data for {symbol}...")
fii_dii = fetch_fii_dii_data()
global_cues = fetch_global_cues()
technicals = fetch_and_calculate_technicals(f"{symbol}.NS")
nse_data = get_nse_data(symbol)
news = fetch_stock_news(symbol, limit=3)
sentiment_data = {"fii_dii_flow": fii_dii, "latest_news": news}

print(f"Calling Groq LLM...")
analysis = generate_premarket_analysis(symbol, sector, technicals, nse_data, sentiment_data, global_cues)

print("\n--- EXACT AI OUTPUT ---")
print(json.dumps(analysis, indent=2))
