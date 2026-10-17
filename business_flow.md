# NSE Pre-Open Quant Engine: Business Flow

This document outlines the complete end-to-end business flow of the Pre-Open Engine.

## High-Level Architecture
The engine consists of two completely decoupled components:
1. **The Python Orchestrator (`main.py`)**: Runs invisibly in the terminal to hunt for data, calculate scores, and dump CSVs.
2. **The Streamlit Dashboard (`dashboard.py`)**: A visual UI that does absolutely no heavy lifting. It simply reads the CSVs dumped by the Orchestrator and displays them nicely.

---

## The Execution Flow (Step-by-Step)

### Phase 1: Wake Up & Wait (Before 9:00 AM)
- You run `python -m preopen_analyzer.main` in your terminal anytime in the morning.
- The Orchestrator wakes up, checks the time, and goes to sleep if it is before 9:00 AM.
- It will automatically wake up the exact second the clock strikes `09:00:00`.

### Phase 2: Live Data Polling (9:00 AM - 9:12 AM)
- Between 9:00 AM and 9:12 AM, the Orchestrator enters an infinite loop, executing one "Cycle" every 30 seconds.
- **In each cycle:**
  1. **Fetch**: It calls the live NSE API to download the pre-open data for thousands of stocks.
  2. **Filter**: It filters out any stocks not in the F&O segment and adds the 9 specific stocks from your custom Watchlist.
  3. **Snapshot**: It saves exactly what the equilibrium price (IEP) and equilibrium quantity (IEQ) are at that exact second to an in-memory SQLite database.
  4. **Sleep**: It sleeps for exactly 30 seconds and repeats.

### Phase 3: Final Decision Engine (Exactly at 9:12 AM)
At exactly 9:12 AM, the Orchestrator stops collecting data and runs the entire historical timeline of the morning through the scoring pipeline.

#### A. Hard Filters (Rejections)
Any stock that fails *any* of the following conditions is immediately rejected:
- **Missing Data**: The stock didn't have at least 5 successful data snapshots.
- **Liquidity Check**: The total executable value (IEP * IEQ) is less than 1 Crore INR.
- **Minimum Quantity**: The IEQ is less than 1,000 shares.
- **Gap Direction (Longs)**: The stock is opening with a negative gap (opening lower than yesterday).
- **Gap Direction (Shorts)**: The stock is opening with a positive gap (opening higher than yesterday).

#### B. The 50-Parameter Scoring (0 to 100)
For the stocks that survive the hard filters, the engine calculates a final score based on a weighted blend of features. The exact same mathematical pipeline is run twice (once for Longs, once for Shorts), but the inputs are mathematically inverted for Shorts.
- **Price Momentum**: Did the IEP drift in our favor across the snapshots, or did it fake out? 
- **Order Imbalance**: Is the underlying order book heavily skewed toward Buy Orders (Long) or Sell Orders (Short)?
- **Gap Rank**: It cross-sectionally ranks the percentage gap against all other stocks in the market to find relative strength/weakness.

#### C. Entry & Exit Calculations
The engine automatically calculates limit order triggers. 
- **Longs**: Calculates a limit entry *below* the IEP (buying the dip), and places the Stop Loss below and Target above based on fixed R:R ratios.
- **Shorts**: Calculates a limit entry *above* the IEP (shorting the spike), and places the Stop Loss above and Target below.
- **Position Sizing**: Dynamically calculates exactly how many shares to buy/short so that if your Stop Loss hits, you lose exactly your fixed max risk (5,000 INR).

### Phase 4: Output & UI Rendering (9:12:05 AM)
- The Orchestrator dumps everything into three output files: `top10_YYYY-MM-DD.csv`, `top10_short_YYYY-MM-DD.csv`, and `watchlist_YYYY-MM-DD.csv`.
- The Orchestrator safely exits.
- You refresh your Streamlit dashboard. The dashboard reads the new CSVs and renders the Top 10 Longs, Top 10 Shorts, and your Watchlist in color-coded tables.
