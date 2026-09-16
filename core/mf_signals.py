"""
MF Signals Module: 7-Factor Quantitative Dip Detection Engine.
No LLM. No opinions. Pure math.
"""
import yfinance as yf
import datetime


# ---------------------------------------------------------------------------
# Factor 1: India VIX (Weight 25%)
# ---------------------------------------------------------------------------
def score_india_vix(vix_value):
    """Scores India VIX from 0 (calm) to 3 (extreme fear)."""
    if vix_value is None:
        return 0, "DATA ERROR"
    if vix_value > 22:
        return 3, "🔴 EXTREME FEAR"
    if vix_value > 16:
        return 2, "🟠 FEAR BUILDING"
    if vix_value > 13:
        return 1, "🟡 SLIGHTLY NERVOUS"
    return 0, "⚪ DEAD CALM"


# ---------------------------------------------------------------------------
# Factor 2: Nifty 50 Drawdown from 52-Week High (Weight 20%)
# ---------------------------------------------------------------------------
def score_nifty_drawdown(current_price, high_52w):
    """Scores drawdown from 52-week high, 0 (normal) to 3 (crash)."""
    if current_price is None or high_52w is None or high_52w == 0:
        return 0, "DATA ERROR", 0.0
    drawdown_pct = ((current_price - high_52w) / high_52w) * 100
    drawdown_pct = round(drawdown_pct, 2)

    if drawdown_pct <= -10:
        return 3, "🔴 CRASH", drawdown_pct
    if drawdown_pct <= -5:
        return 2, "🟠 CORRECTION", drawdown_pct
    if drawdown_pct <= -3:
        return 1, "🟡 PULLBACK", drawdown_pct
    return 0, "⚪ NORMAL", drawdown_pct


# ---------------------------------------------------------------------------
# Factor 3: Nifty PE Ratio (Weight 15%)
# ---------------------------------------------------------------------------
def score_nifty_pe(pe_value):
    """Scores Nifty PE ratio, 0 (overvalued) to 3 (deep value)."""
    if pe_value is None:
        return 0, "DATA ERROR"
    if pe_value < 19:
        return 3, "🔴 DEEP VALUE"
    if pe_value < 22:
        return 2, "🟠 UNDERVALUED"
    if pe_value < 24:
        return 1, "🟡 FAIR VALUE"
    return 0, "⚪ OVERVALUED"


# ---------------------------------------------------------------------------
# Factor 4: FII/DII Net Cash Flow (Weight 15%)
# ---------------------------------------------------------------------------
def score_fii_dii(fii_net, dii_net):
    """Scores FII/DII flow pattern, 0 (no distress) to 3 (smart money transfer)."""
    if fii_net is None:
        return 0, "DATA ERROR"

    fii_val = _parse_flow_value(fii_net)
    dii_val = _parse_flow_value(dii_net)

    if fii_val >= 0:
        return 0, "⚪ FII BUYING"
    if fii_val > -1500:
        return 1, "🟡 MILD FII SELLING"
    if fii_val <= -3000 and dii_val >= 1000:
        return 3, "🔴 SMART MONEY TRANSFER"
    if fii_val <= -1500:
        return 2, "🟠 HEAVY FII SELLING"
    return 1, "🟡 MILD FII SELLING"


def _parse_flow_value(val):
    """Converts FII/DII net value string to float."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    try:
        cleaned = str(val).replace(",", "").replace("₹", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# Factor 5: Midcap / Smallcap Index Drawdown (Weight 10%)
# ---------------------------------------------------------------------------
def score_broader_market_drawdown(midcap_drawdown, smallcap_drawdown):
    """Scores the worse of midcap/smallcap drawdown, 0 to 3."""
    worst = min(midcap_drawdown or 0, smallcap_drawdown or 0)
    if worst <= -15:
        return 3, "🔴 BROADER CRASH"
    if worst <= -10:
        return 2, "🟠 BROADER CORRECTION"
    if worst <= -5:
        return 1, "🟡 BROADER PULLBACK"
    return 0, "⚪ NORMAL"


# ---------------------------------------------------------------------------
# Factor 6: USD/INR Weekly Change (Weight 10%)
# ---------------------------------------------------------------------------
def score_usdinr_weekly(weekly_pct_change):
    """Scores Rupee weakness, 0 (stable) to 3 (currency crisis)."""
    if weekly_pct_change is None:
        return 0, "DATA ERROR"
    if weekly_pct_change > 2.0:
        return 3, "🔴 CURRENCY CRISIS"
    if weekly_pct_change > 1.0:
        return 2, "🟠 SIGNIFICANT OUTFLOW"
    if weekly_pct_change > 0.5:
        return 1, "🟡 MILD OUTFLOW"
    return 0, "⚪ STABLE"


# ---------------------------------------------------------------------------
# Factor 7: US Market Overnight Signal (Weight 5%)
# ---------------------------------------------------------------------------
def score_us_market(sp500_pct_change):
    """Scores overnight S&P 500 move, 0 (calm) to 3 (global crash)."""
    if sp500_pct_change is None:
        return 0, "DATA ERROR"
    if sp500_pct_change <= -3.0:
        return 3, "🔴 GLOBAL CRASH"
    if sp500_pct_change <= -2.0:
        return 2, "🟠 GLOBAL SELLOFF"
    if sp500_pct_change <= -1.0:
        return 1, "🟡 RISK-OFF"
    return 0, "⚪ CALM"


# ---------------------------------------------------------------------------
# Composite Score Calculator
# ---------------------------------------------------------------------------
WEIGHTS = {
    "india_vix":        0.25,
    "nifty_drawdown":   0.20,
    "nifty_pe":         0.15,
    "fii_dii":          0.15,
    "broader_market":   0.10,
    "usdinr":           0.10,
    "us_market":        0.05,
}


def calculate_composite_score(scores_dict):
    """
    Takes a dict of {factor_name: raw_score (0-3)} and returns weighted composite.
    """
    total = 0.0
    for factor, weight in WEIGHTS.items():
        raw = scores_dict.get(factor, 0)
        total += raw * weight
    return round(total, 2)


def get_verdict(composite_score):
    """Returns verdict string and deployment percentage based on composite score."""
    if composite_score >= 2.50:
        return "🔥 GENERATIONAL BUY", "Deploy 100% of war-chest. This happens once every 5-8 years.", 100
    if composite_score >= 1.75:
        return "🔴 STRONG BUY", "Deploy 50% of war-chest into Mid-Cap + Small-Cap.", 50
    if composite_score >= 1.00:
        return "🟠 REAL CORRECTION", "Deploy 25% of war-chest into Flexi-Cap + Mid-Cap.", 25
    if composite_score >= 0.50:
        return "🟡 MILD DIP", "Deploy 10% of war-chest into Flexi-Cap only.", 10
    return "⚪ NO OPPORTUNITY", "Do nothing. Keep cash in Liquid Fund.", 0


# ---------------------------------------------------------------------------
# Data Fetchers (using yfinance)
# ---------------------------------------------------------------------------
def fetch_index_data(ticker_symbol, period="3mo"):
    """Fetches price history and returns (current_price, 52_week_high, pct_change_1d)."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return None, None, None

        current_price = float(hist['Close'].iloc[-1])
        high_52w = float(hist['High'].max())

        pct_change_1d = None
        if len(hist) >= 2:
            prev = float(hist['Close'].iloc[-2])
            pct_change_1d = round(((current_price - prev) / prev) * 100, 2)

        return current_price, high_52w, pct_change_1d
    except Exception as e:
        print(f"  [WARN] Failed to fetch {ticker_symbol}: {e}")
        return None, None, None


def fetch_52w_high(ticker_symbol):
    """Fetches 52-week high by pulling 1 year of data."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        if hist.empty:
            return None
        return float(hist['High'].max())
    except Exception:
        return None


def fetch_usdinr_weekly_change():
    """Returns the weekly percentage change in USD/INR (positive = rupee weakened)."""
    try:
        ticker = yf.Ticker("USDINR=X")
        hist = ticker.history(period="1mo")
        if len(hist) < 6:
            return None
        current = float(hist['Close'].iloc[-1])
        week_ago = float(hist['Close'].iloc[-6])
        return round(((current - week_ago) / week_ago) * 100, 2)
    except Exception:
        return None


def fetch_india_vix():
    """Returns the current India VIX value."""
    try:
        ticker = yf.Ticker("^INDIAVIX")
        hist = ticker.history(period="5d")
        if hist.empty:
            return None
        return round(float(hist['Close'].iloc[-1]), 2)
    except Exception:
        return None


def fetch_nifty_pe():
    """
    Fetches Nifty PE from NSE website.
    Falls back to a yfinance-based estimation if direct scrape fails.
    """
    try:
        import requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/"
        }
        session = requests.Session()
        session.headers.update(headers)
        session.get("https://www.nseindia.com", timeout=10)
        resp = session.get(
            "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            metadata = data.get("metadata", {})
            pe = metadata.get("pe")
            if pe:
                return round(float(pe), 2)
    except Exception:
        pass

    # Fallback: return None and let the caller handle it
    return None
