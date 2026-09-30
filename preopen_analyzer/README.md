# NSE Pre-Open Market Analyzer

A production-quality Python application that collects NSE pre-open market data every 30 seconds from 9:00 AM to 9:07 AM IST and identifies the strongest candidates for a pre-market long trade.

## Purpose

Systematically identify stocks where:
- Pre-open demand is strong and persistent
- IEP (Indicative Equilibrium Price) is stable or improving
- IEQ (Indicative Equilibrium Quantity) is sufficiently large
- Equilibrium and market-order imbalance confirm demand
- The potential reward justifies the risk

The system is **deterministic, explainable, configurable, and backtestable**.

## Quick Start

### Phase 0: Data Verification (First-Time Only)

Run during the live pre-open session (9:00–9:08 AM IST) to capture raw API data and verify field availability:

```bash
python -m preopen_analyzer.capture_raw
```

This saves raw JSON snapshots to `preopen_analyzer/data/raw_captures/`.

### Production Run

```bash
# Run the full analyzer (default: F&O stocks, 30-second interval)
python -m preopen_analyzer.main

# Customize category and interval
python -m preopen_analyzer.main --category NIFTY --interval 30

# Test mode (single snapshot, ignores time window)
python -m preopen_analyzer.main --test
```

### Run Tests

```bash
python -m pytest preopen_analyzer/tests/ -v
# or
python -m unittest discover preopen_analyzer/tests/ -v
```

## Architecture

```
preopen_analyzer/
├── config.py              # All configurable parameters (weights, thresholds)
├── models.py              # Data models (PreOpenSnapshot, StockCandidate, etc.)
├── nse_client.py          # NSE API wrapper with retry logic
├── normalizer.py          # Column name mapping (NSE → internal)
├── data_store.py          # SQLite snapshot persistence
├── feature_engineering.py # Basic features (gap, IEQ, imbalance, spread)
├── time_series.py         # Time-series analysis (slopes, persistence, stability)
├── reversal_detector.py   # Late reversal detection
├── scoring.py             # Cross-sectional scoring (0-100) with penalties
├── filters.py             # Hard rejection rules & contradiction detection
├── entry_exit.py          # Entry zones, targets, stop-loss, R:R, GTT levels
├── market_context.py      # Optional NIFTY/VIX/FII-DII context
├── news_context.py        # Optional catalyst/news input
├── report.py              # Console output & CSV/JSON reports
├── capture_raw.py         # Phase 0 data capture script
├── main.py                # Main 30-second polling orchestrator
├── data/                  # SQLite database & raw captures
├── output/                # Generated reports (CSV, JSON)
└── tests/
    └── test_scoring.py    # Unit tests (8 required test cases + extras)
```

## Scoring System

The PREMARKET_SCORE (0-100) is computed from these weighted components:

| Component               | Weight | Signal |
|--------------------------|--------|--------|
| IEP Gap Quality          | 15%    | Size and quality of the opening gap |
| IEQ / Executable Value   | 15%    | Liquidity and tradeable volume |
| Equilibrium Imbalance    | 20%    | Buy vs sell demand at IEP |
| Market-Order Imbalance   | 10%    | Market order pressure |
| IEP Trend / Momentum     | 10%    | Is IEP strengthening or weakening? |
| IEP Stability            | 10%    | Drawdown from max IEP |
| Imbalance Persistence    | 8%     | How consistently bullish across snapshots |
| Imbalance Trend          | 5%     | Is demand growing or shrinking? |
| Liquidity / Spread       | 4%     | Bid-ask tightness |
| Market Context           | 3%     | NIFTY/VIX/FII backdrop |

After the base score, **penalties** (up to -20 each) are applied for late reversals, low IEQ, wide spreads, contradictory signals, etc.

## Key Design Principles

1. **No AI black-box** — All scoring is deterministic and explainable
2. **No fake probabilities** — Signal confidence, not win probability
3. **No look-ahead bias** — Only 09:00-09:07 data used for decisions
4. **Fewer high-quality signals > many weak signals** — PRIMARY=NONE if nothing qualifies
5. **Persistent order flow matters most** — Not just the latest snapshot

## Data Source

Uses the NSE public API via `jugaad-data`:
- `pre_open_market("FO")` — Single API call returns all F&O stocks
- Polling every 30 seconds = 2 requests/minute (safe for rate limits)

## Output

At 09:07, the system produces:
- **PRIMARY CANDIDATE** with entry zone, target, stop-loss, R:R
- **SECONDARY CANDIDATE**
- **WATCH CANDIDATE**
- **TOP 10 ranked table**
- **AVOID LIST** with rejection explanations
- CSV and JSON report files in `output/`

## Configuration

All parameters are in `config.py` — change weights, thresholds, and targets without editing core logic.
