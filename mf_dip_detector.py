"""
MF Dip Detector v2 — 7-Factor Quantitative Mutual Fund Buying Signal.
No LLM. No opinions. Pure math. Runs in under 5 seconds.

Usage:
    .\\venv\\Scripts\\python mf_dip_detector.py
"""
import sys
import json
import datetime
import os

sys.stdout.reconfigure(encoding='utf-8')

from core.mf_signals import (
    fetch_india_vix, score_india_vix,
    fetch_index_data, fetch_52w_high, score_nifty_drawdown,
    fetch_nifty_pe, score_nifty_pe,
    score_fii_dii,
    score_broader_market_drawdown,
    fetch_usdinr_weekly_change, score_usdinr_weekly,
    score_us_market,
    calculate_composite_score, get_verdict,
)
from core.sentiment import fetch_fii_dii_data
from core.mf_report import generate_mf_html_report


# =========================================================================
# Data Collection — fetch all 7 factors in one pass
# =========================================================================
def collect_all_signals():
    """Fetches live data for all 7 factors and returns a structured dict."""
    print("  [1/7] Fetching India VIX...")
    vix = fetch_india_vix()

    print("  [2/7] Fetching Nifty 50 (price + 52W high)...")
    nifty_price, _, nifty_1d_chg = fetch_index_data("^NSEI", period="5d")
    nifty_52w_high = fetch_52w_high("^NSEI")

    print("  [3/7] Fetching Nifty PE Ratio...")
    nifty_pe = fetch_nifty_pe()

    print("  [4/7] Fetching FII/DII Cash Flows...")
    fii_dii = fetch_fii_dii_data()

    print("  [5/7] Fetching Midcap & Smallcap Index Drawdowns...")
    midcap_data = _fetch_index_drawdown("NIFTYMIDCAP150.NS")
    smallcap_data = _fetch_index_drawdown("NIFTYSMLCAP250.NS")

    print("  [6/7] Fetching USD/INR Weekly Change...")
    usdinr_weekly = fetch_usdinr_weekly_change()

    print("  [7/7] Fetching S&P 500 Overnight Signal...")
    _, _, sp500_chg = fetch_index_data("^GSPC", period="5d")

    return {
        "vix": vix,
        "nifty_price": nifty_price,
        "nifty_52w_high": nifty_52w_high,
        "nifty_pe": nifty_pe,
        "fii_dii": fii_dii,
        "midcap_drawdown": midcap_data,
        "smallcap_drawdown": smallcap_data,
        "usdinr_weekly": usdinr_weekly,
        "sp500_chg": sp500_chg,
    }


def _fetch_index_drawdown(ticker_symbol):
    """Returns drawdown % from 52-week high for a given index ticker."""
    try:
        price, _, _ = fetch_index_data(ticker_symbol, period="5d")
        high_52w = fetch_52w_high(ticker_symbol)
        if price and high_52w and high_52w > 0:
            return round(((price - high_52w) / high_52w) * 100, 2)
    except Exception:
        pass
    return 0.0


# =========================================================================
# Scoring — score all 7 factors and compute composite
# =========================================================================
def score_all_factors(data):
    """Takes raw data dict and returns scored results for all 7 factors."""
    factors = []

    # Factor 1: India VIX
    f1_score, f1_label = score_india_vix(data["vix"])
    factors.append(build_factor_row("India VIX", format_value(data["vix"]), f1_score, f1_label))

    # Factor 2: Nifty 50 Drawdown
    f2_score, f2_label, drawdown_pct = score_nifty_drawdown(data["nifty_price"], data["nifty_52w_high"])
    dd_display = f"{drawdown_pct:+.1f}% from {format_value(data['nifty_52w_high'])}"
    factors.append(build_factor_row("Nifty Drawdown", dd_display, f2_score, f2_label))

    # Factor 3: Nifty PE
    f3_score, f3_label = score_nifty_pe(data["nifty_pe"])
    factors.append(build_factor_row("Nifty PE Ratio", format_value(data["nifty_pe"]), f3_score, f3_label))

    # Factor 4: FII/DII
    fii_net = extract_fii_net(data["fii_dii"])
    dii_net = extract_dii_net(data["fii_dii"])
    f4_score, f4_label = score_fii_dii(fii_net, dii_net)
    fii_display = format_flow(fii_net)
    factors.append(build_factor_row("FII Flow (Today)", fii_display, f4_score, f4_label))

    # Factor 5: Broader Market
    midcap_dd = data["midcap_drawdown"] or 0.0
    smallcap_dd = data["smallcap_drawdown"] or 0.0
    f5_score, f5_label = score_broader_market_drawdown(midcap_dd, smallcap_dd)
    broader_display = f"Mid:{midcap_dd:+.1f}% / Sml:{smallcap_dd:+.1f}%"
    factors.append(build_factor_row("Broader Mkt DD", broader_display, f5_score, f5_label))

    # Factor 6: USD/INR
    f6_score, f6_label = score_usdinr_weekly(data["usdinr_weekly"])
    usdinr_display = f"{data['usdinr_weekly']:+.2f}% weekly" if data["usdinr_weekly"] is not None else "N/A"
    factors.append(build_factor_row("USD/INR (Weekly)", usdinr_display, f6_score, f6_label))

    # Factor 7: US Market
    f7_score, f7_label = score_us_market(data["sp500_chg"])
    sp_display = f"{data['sp500_chg']:+.2f}%" if data["sp500_chg"] is not None else "N/A"
    factors.append(build_factor_row("US Mkt (O/Night)", sp_display, f7_score, f7_label))

    # Build scores dict for composite
    scores = {
        "india_vix": f1_score,
        "nifty_drawdown": f2_score,
        "nifty_pe": f3_score,
        "fii_dii": f4_score,
        "broader_market": f5_score,
        "usdinr": f6_score,
        "us_market": f7_score,
    }

    return factors, scores


# =========================================================================
# Display Helpers
# =========================================================================
def build_factor_row(name, value, score, label):
    """Creates a structured row dict for terminal display."""
    return {"name": name, "value": value, "score": score, "label": label}


def format_value(val):
    """Formats a numeric value for display."""
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:,.2f}"
    return str(val)


def format_flow(val):
    """Formats FII/DII flow value for display."""
    if val is None:
        return "N/A"
    return f"₹{val:,.0f} Cr"


def extract_fii_net(fii_dii_data):
    """Extracts FII net value from the fii_dii dict."""
    if not fii_dii_data or "error" in fii_dii_data:
        return None
    raw = fii_dii_data.get("FII_Net")
    if raw is None:
        return None
    try:
        return float(str(raw).replace(",", ""))
    except (ValueError, TypeError):
        return None


def extract_dii_net(fii_dii_data):
    """Extracts DII net value from the fii_dii dict."""
    if not fii_dii_data or "error" in fii_dii_data:
        return None
    raw = fii_dii_data.get("DII_Net")
    if raw is None:
        return None
    try:
        return float(str(raw).replace(",", ""))
    except (ValueError, TypeError):
        return None


# =========================================================================
# Terminal Report Printer
# =========================================================================
def print_terminal_report(factors, composite_score, verdict, action, deploy_pct, data):
    """Prints the clean terminal dashboard."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n{'=' * 62}")
    print(f"   MF DIP DETECTOR v2 | {now}")
    print(f"{'=' * 62}")

    nifty_display = format_value(data.get("nifty_price"))
    print(f"\n   Nifty 50: {nifty_display}")
    print(f"\n {'Factor':<22} | {'Value':<28} | {'Score':>5} | {'Signal'}")
    print(f" {'-' * 22}-+-{'-' * 28}-+-{'-' * 5}-+-{'-' * 20}")

    for f in factors:
        print(f" {f['name']:<22} | {f['value']:<28} | {f['score']}/3   | {f['label']}")

    print(f"\n   COMPOSITE SCORE: {composite_score:.2f} / 3.00")
    print(f"\n{'=' * 62}")
    print(f"   {verdict}")
    print(f"{'=' * 62}")

    if deploy_pct > 0:
        print(f"\n   [ACTION PLAN]")
        print(f"   1. Open Zerodha Coin / Groww NOW.")
        print(f"   2. {action}")
        print(f"   3. Pay via UPI before 2:00 PM to lock today's NAV!")
    else:
        print(f"\n   {action}")

    print(f"\n{'=' * 62}\n")


# =========================================================================
# History Logger — track past scores for future review
# =========================================================================
def log_to_history(composite_score, verdict, data, factors):
    """Appends today's result to a JSON log file."""
    history_path = os.path.join(os.path.dirname(__file__), "docs", "mf_dip_history.json")

    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "composite_score": composite_score,
        "verdict": verdict,
        "india_vix": data.get("vix"),
        "nifty_price": data.get("nifty_price"),
        "nifty_pe": data.get("nifty_pe"),
        "factor_scores": {f["name"]: f["score"] for f in factors},
    }
    history.append(entry)

    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# =========================================================================
# Main Entry Point
# =========================================================================
def run_mf_dip_detector():
    """Main orchestrator: collect → score → display → log."""
    print(f"\n{'=' * 62}")
    print(f"   MF DIP DETECTOR v2 — Collecting Live Data...")
    print(f"{'=' * 62}\n")

    data = collect_all_signals()
    factors, scores = score_all_factors(data)
    composite = calculate_composite_score(scores)
    verdict, action, deploy_pct = get_verdict(composite)

    print_terminal_report(factors, composite, verdict, action, deploy_pct, data)
    log_to_history(composite, verdict, data, factors)
    
    html_path = generate_mf_html_report(factors, composite, verdict, action, deploy_pct, data)

    print(f"   History logged to docs/mf_dip_history.json")
    print(f"   Beautiful HTML Report saved to: {html_path}\n")


if __name__ == "__main__":
    run_mf_dip_detector()
