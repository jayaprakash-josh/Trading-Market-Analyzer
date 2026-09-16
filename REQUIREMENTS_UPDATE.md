# Parameter Availability & Source Matrix

This document outlines exactly what parameters we are tracking for the 09:10 AM Pre-Market Analyzer, the source of truth, and a direct comparison between using the **Kite MCP (Manual)** vs **NSE Free APIs (Automated)**.

## 1. Parameters We ARE Getting (09:10 AM Execution)

| Parameter | Source of Truth (NSE Free API - Path 2) | Source of Truth (Kite MCP - Path 1) | Winner for 09:10 AM |
| :--- | :--- | :--- | :--- |
| **Historical Technicals** (CPR, PDH, PDL, EMA, RSI) | `yfinance` & `ta` libraries | `yfinance` & `ta` libraries | **Tie** (Independent of broker) |
| **Pre-Open IEP** (Gap Up/Down Price) | `jugaad-data` (`stock_quote` IEP field) | Kite `get_quotes` (`last_price`) | **Tie** |
| **Pre-Open Matched Volume** | `jugaad-data` (`preOpenMarket` volume array) | Kite `get_quotes` (`volume`) | **Tie** |
| **FII / DII Net Cash Flow** | NSE Direct HTTPS API (`sentiment.py`) | NSE Direct HTTPS API | **Tie** (Independent of broker) |
| **Corporate News / Sentiment** | Google News RSS Scraper (`sentiment.py`) | Google News RSS Scraper | **Tie** (Independent of broker) |
| **Live Order Book Depth** (Top 5 Bids/Asks) | `jugaad-data` (`orderBook` array) | Kite `get_quotes` (`depth` array) | **Tie** |
| **Futures Open Interest** (Long/Short Buildup) | `jugaad-data` (Derivatives quote) | Kite `get_quotes` (Requires exact `NFO:` contract symbol) | **NSE Free** (Easier to fetch dynamically) |
| **Options PCR** (Put-Call Ratio) | `jugaad-data` (`equities_option_chain`) fetches all 50+ strikes in one second. | **Extremely difficult.** You would have to manually guess and query 50 exact Kite contract strings simultaneously. | **NSE Free** (Massive advantage) |
| **Max Call & Put OI Strikes** (Options Resistance/Support) | `jugaad-data` (Automatically sorts the fetched Options Chain) | **Extremely difficult.** Same reason as above. | **NSE Free** (Massive advantage) |
| **Automation & Execution** | **100% Hands-Free.** Cron job runs silently while you sleep. | **Requires Daily Manual Action.** Fails if you don't click the link at 09:09 AM. | **NSE Free** (Massive advantage) |


