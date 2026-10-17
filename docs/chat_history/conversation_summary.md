# Project & Conversation Summary

This document captures the historical context, core principles, architecture, and evolution of the **NSE Trading Market Analyzer** developed across the agent session.

---

## 📌 Critical System Rules & Preferences

1. **Strict Fetch Interval Rule**:
   * Order book fetching interval is strictly **30 seconds** (`FETCH_INTERVAL_SECONDS = 30`).
   * Never decrease to lower values (e.g. 3 seconds) to prevent NSE exchange IP blocks and protect live operation.

2. **Custom Watchlist Settings**:
   * Configured in `config.py` under `WATCHLIST_TEST` / `WATCHLIST_SET_1` / `WATCHLIST_SET_2`.
   * Includes high-interest tickers such as `BOSCHLTD`, `MCX`, `M&M`, `SONACOMS`, `AZAD`, `WABAG`, `AVALON`, `INDOMIM`, `GAJA`, `LALITHAA`.
   * Custom Watchlist displays the `ALIGN` score alongside market metrics.

3. **Strict Database Separation**:
   * Unit tests (`test_csv_run.py`) must never touch or write to the live production database (`preopen_data.db`).
   * Active live database is `preopen_data.db` in project root.

4. **Strategy & Filter Validations**:
   * Rejects new IPO listings on day 1 (`ListingDayIPO`).
   * Rejects flat openings (0.0% gap).
   * Directional filters: For LONG setups, reject negative gap or negative order book imbalance. For SHORT setups, reject positive gap or positive order book imbalance.

---

## 🏗️ Core Architecture & Execution Flow

### Dual-Phase Finalization
* **Phase 1: Equity Finalization (09:00 AM – 09:12 AM)**
  * Polling pre-open order book snapshots every 30 seconds.
  * Captures IEP (Indicative Equilibrium Price), Indicative Equilibrium Quantity, and Limit Order Imbalance.
  * Ranks Top 10 High-Opening Potential (LONG) and Top 10 Selling Pressure (SHORT).
  * Writes daily snapshot reports to `preopen_analyzer/output/top10_YYYY-MM-DD.csv`.

* **Phase 2: Live F&O OI Confirmation (09:16 AM)**
  * Triggered at 9:16 AM immediately after the 9:15 AM normal market open.
  * Queries derivative quote endpoints via `jugaad_data` for individual derivative quotes (bypassing the NSE bulk Top 20 limitation and option chain cookie blocks).
  * Computes:
    1. **Futures Buildup:** `LONG_BUILDUP`, `SHORT_COVERING`, `SHORT_BUILDUP`, `LONG_UNWINDING`.
    2. **Options PCR (Put-Call Ratio):** Calculated on liquid near-expiry option strikes.
    3. **Trapped Writers:** Evaluates if IEP breached max Call/Put open interest strikes.
  * Produces combined score (`0.65 * PreOpen + 0.35 * F&O_OI`).
  * Writes confirmed output to `preopen_analyzer/output/fno_top10_YYYY-MM-DD.csv`.

---

## 🖥️ Streamlit Dashboard
* **Entry point:** `dashboard.py`
* Default port is `8501` (or `8502` if `8501` is occupied).
* Displays:
  1. Top 10 High-Opening Potential Stocks (Equity)
  2. Top 10 Low-Opening / High Selling Pressure Stocks (Short)
  3. Top 10 F&O OI-Confirmed Stocks
  4. Custom Watchlist Table
  5. Live Market Breadth & Advance/Decline ratios
