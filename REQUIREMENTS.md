# NSE Pre-Market Analyzer - Requirements Document

## 1. Project Overview
A fully automated Python-based stock market analyzer that runs every morning before the NSE opens. It fetches historical data, global macros, NSE derivatives, and news, computes technical indicators, and leverages an LLM (Groq) to score and identify high-probability intraday setups.

## 2. Core Features (Migrated from JS)
- **Watchlist Processing**: Analyze a predefined list of NSE stocks (e.g., M&M, BOSCHLTD).
- **Market Context**: Fetch NIFTY 50, BANK NIFTY, India VIX, and global indices (S&P 500, NASDAQ, Crude, Gold).
- **Daily OHLCV Data**: Fetch daily historical data (up to 3 months) to establish recent structures.
- **Technical Indicator Derivations**:
  - Previous Day High, Low, Close (PDH, PDL, PDC).
  - Central Pivot Range (CPR: Pivot, BC, TC).
  - 20-Day Average Volume.
  - Previous Week High/Low.
  - Fibonacci Retracement Levels.
  - Fair Value Gaps (Bullish/Bearish FVG).
- **Options & Futures (Derivatives)**:
  - Nearest Future LTP, OI, and OI Change.
  - Total Call/Put OI, PCR (Put-Call Ratio), and Max OI Strikes.
- **Sentiment / Catalysts**:
  - Latest Corporate Announcements from NSE.
  - Google News RSS feed for each stock.
- **LLM Integration (Groq)**: 18-point scoring system using a specialized prompt for intraday traders.
- **Delivery**: Format results as an HTML Email and send via SMTP.

## 3. Identified Gaps & Python Improvements
- **Robust Data Fetching**: Using `yfinance` for OHLCV data instead of manual Yahoo API parsing.
- **Advanced Technicals**: Utilizing `pandas` and `pandas_ta` to calculate FVGs, CPR, and adding standard indicators (RSI, EMA, ATR for risk-reward calculations) which were too complex to write manually in JS.
- **NSE API Reliability**: NSE India actively blocks raw requests. Python allows us to implement retry logic, session management, user-agent rotation, or library integrations (`nsepython`/`jugaad-trader`) to ensure reliable data.
- **Structured LLM Output**: Instead of asking the LLM to output raw markdown tables (which can break), we can use `Pydantic` and `Instructor` to force Groq to return guaranteed JSON objects, which we then safely render into HTML.

## 4. Architectural Decisions
- **Timing:** 09:10 AM execution (captures true NSE opening gaps, opening volume, and validates setups against actual open prices).
- **Indicators:** Enhanced to include ATR (for dynamic Stop-Loss/Targets), EMA crossovers, RSI, along with CPR and FVG.
- **Data Sourcing Strategy (The Hybrid Architecture):** 
  - **OHLCV, Macros, VIX & Technicals:** `yfinance` + `pandas_ta` (Fast, reliable historical data).
  - **Pre-Open IEP & Derivatives (F&O):** Zerodha Kite API / MCP (Provides flawless exact opening gaps, Level 2 depth, Options OI, PCR, and Futures data).
  - **Institutional Flow & News:** Python `requests` web scraper for Moneycontrol/NSE (FII/DII cash flow) and Google News RSS (Corporate announcements).
- **Watchlist:** Managed inside `config.py` to keep logic and configuration separate.
- **Notification:** Skipped for now. Outputs will be generated locally (HTML/Markdown) for review.
