import os

# --- WATCHLIST CONFIGURATION ---
# Change ACTIVE_SET to "SET_2" to run the new batch of stocks. Do not run both at the same time.
ACTIVE_SET = "SET_2" 

# Aliases for tickers that differ between internal symbols and official NSE/Yahoo listings
SYMBOL_ALIASES = {
    "INDUSIND": "INDUSINDBK",
    "NATCOFORM": "NATCOPHARM"
}

WATCHLIST_SET_1 = [
    "M&M",
    "RELIANCE"
]

WATCHLIST_SET_2 = [
    "ARSSBL",
    "AVALON",
    "AZAD",
    "BSE",
    "GMMPFAUDLR",
    "GMRAIRPORT",
    "HDBFS",
    "HINDCOPPER",
    "IGIL",
    "INDOMIM",
    "INDUSIND",
    "KAYNES",
    "KFINTECH",
    "LALITHAA",
    "MCX",
    "MOMSBELIEF",
    "M&M",
    "NATCOFORM",
    "NSDL",
    "WAAREEENER",
    "WIPRO",
    "SONACOMS",
    "WABAG"
]

WATCHLIST = WATCHLIST_SET_1 if ACTIVE_SET == "SET_1" else WATCHLIST_SET_2

SECTORS = {
    "WAAREEENER": "Renewable energy / Solar / Manufacturing",
    "SONACOMS": "Auto components / Automotive",
    "GMMPFAUDLR": "Industrial / Engineering / Specialty manufacturing",
    "MCX": "Exchange / Commodities / Financial markets",
    "BOSCHLTD": "Auto components / Industrial / Automotive",
    "M&M": "Automobile / Tractors / Auto",
    "GMRAIRPORT": "Airport infrastructure / Aviation",
    "WABAG": "Water infrastructure / EPC",
    "AZAD": "Aerospace / Defence / Engineering",
    "ARSSBL": "Auto components / Automotive",
    "AVALON": "IT / Technology",
    "BSE": "Exchange / Financial markets",
    "GMMFAUDLR": "Industrial / Engineering / Specialty manufacturing",
    "HDBFS": "NBFC / Financial services",
    "HINDCOPPER": "Mining / Metals / Copper",
    "IGIL": "Industrial / Gas / Infrastructure",
    "INDOMIM": "Precision Engineering / Manufacturing",
    "INDUSIND": "Private Banking / Financial services",
    "KAYNES": "Electronics / EMS / Technology",
    "KFINTECH": "Financial Technology / Registrar",
    "LALITHAA": "Retail / Jewellery",
    "MOMSBELIEF": "Healthcare / Social Enterprise",
    "NATCOFORM": "Pharmaceuticals / Formulations",
    "NSDL": "Depository / Financial Infrastructure",
    "WIPRO": "IT Services / Technology",
}

# Stock Tier Classification (for strategy decisions in the HTML report)
TIERS = {
    "M&M": 1,           # Tier 1: Avg Down OK
    "MCX": 1,           # Tier 1: Avg Down OK
    "SONACOMS": 2,      # Tier 2: Cautious
    "WAAREEENER": 3,    # Tier 3: Stop-Loss Only
    "AZAD": 3,          # Tier 3: Stop-Loss Only
    "WABAG": 3,         # Tier 3: Stop-Loss Only
    "BOSCHLTD": 3,      # Tier 3: Stop-Loss Only (Capital intensive)
    "GMRAIRPORT": 3,    # Tier 3: Stop-Loss Only (Debt heavy)
    "GMMPFAUDLR": 3,    # Tier 3: Stop-Loss Only (Cyclical)
}

# Indices to track
INDICES = {
    "NIFTY_50": "^NSEI",
    "BANK_NIFTY": "^NSEBANK",
    "INDIA_VIX": "^INDIAVIX"
}

# Global Macro Proxies
MACROS = {
    "S&P_500": "^GSPC",
    "NASDAQ": "^IXIC",
    "CRUDE_OIL": "CL=F",
    "GOLD": "GC=F",
    "GIFT_NIFTY": "NIFTY_FUT.NS",  # GIFT Nifty for pre-open proxy
}

# --- RISK MANAGEMENT SETTINGS ---
TRADING_CAPITAL = 500000          # Total trading capital in INR
RISK_PER_TRADE_PERCENT = 0.5     # Max risk per trade as % of capital (0.5% = ₹2,500 on 5L)
MIN_RISK_REWARD = 1.5            # Minimum R:R to allow a trade (hard veto below this)
MIN_TRADED_VALUE_LAKHS = 10      # Minimum avg daily traded value in lakhs for liquidity gate

# --- APPLICATION SETTINGS ---
TIMEZONE = "Asia/Kolkata"

# Set to False during development/testing to skip Groq API calls and run fast
ENABLE_LLM = True

# AI Config
LLM_PROVIDER = "groq"
LLM_MODEL = "openai/gpt-oss-120b"
LLM_TEMPERATURE = 0.2
LLM_MODEL_GEMINI = "gemini-3.5-flash-lite"

# --- PHASE 2: LIVE CONFIRMATION SETTINGS ---
OR_MINUTES = 15                   # Opening Range window: 5 or 15 minutes
CANDLE_INTERVAL = "5m"            # yfinance interval for intraday candles
BREAKOUT_VOLUME_MULTIPLIER = 1.3  # Min volume on breakout candle vs avg
MAX_POSITION_PCT = 20             # Max % of capital in a single stock
PHASE2_CUTOFF_TIME = "09:45"      # Stop scanning for new entries after this time
