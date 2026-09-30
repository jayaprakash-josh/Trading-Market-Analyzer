import json
import os
import pandas as pd
import logging
from datetime import datetime

from .models import FinalDecision
from . import config

logger = logging.getLogger(__name__)

def generate_report(decision: FinalDecision, output_dir: str = "."):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    today_str = decision.timestamp.strftime("%Y-%m-%d")
    
    csv_path = os.path.join(output_dir, f"top10_{today_str}.csv")
    csv_path_short = os.path.join(output_dir, f"top10_short_{today_str}.csv")
    
    _write_csv(decision.top_10, csv_path)
    if decision.top_10_short:
        _write_csv(decision.top_10_short, csv_path_short)

    # Write F&O OI-confirmed CSV
    fno_csv_path = os.path.join(output_dir, f"fno_top10_{today_str}.csv")
    if decision.top_10_fno:
        _write_fno_csv(decision.top_10_fno, fno_csv_path)

    
    wl_csv_path = os.path.join(output_dir, f"watchlist_{today_str}.csv")
    
    # Write meta file
    meta_path = os.path.join(output_dir, f"meta_{today_str}.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump({"last_updated": decision.timestamp.isoformat()}, f)

    if getattr(config, 'CUSTOM_WATCHLIST', None) and decision.all_long and decision.all_short:
        wl_symbols = set(config.CUSTOM_WATCHLIST)
        wl_rows = []
        # Find them in long
        for c_long in decision.all_long:
            if c_long.symbol in wl_symbols:
                # Find matching in short
                c_short = next((x for x in decision.all_short if x.symbol == c_long.symbol), None)
                short_score = c_short.opening_strength_score if c_short else 0.0
                wl_rows.append({
                    'SYMBOL': c_long.symbol,
                    'BUY_SCORE': c_long.opening_strength_score,
                    'SELL_SCORE': short_score,
                    'IEP': c_long.latest_iep,
                    'PREV_CLOSE': c_long.prev_close,
                    'GAP_PCT': c_long.gap_pct,
                    'IEQ': c_long.latest_ieq,
                    'EQ_IMBALANCE': c_long.eq_imbalance_qty,
                    'MO_IMBALANCE': c_long.mo_imbalance_qty,
                    'EV_CR': c_long.executable_value_cr
                })
        if wl_rows:
            import pandas as pd
            pd.DataFrame(wl_rows).to_csv(wl_csv_path, index=False)


    logger.info("=" * 60)
    logger.info(f"PRE-OPEN MARKET ANALYZER FINAL REPORT ({decision.timestamp.strftime('%H:%M')})")
    logger.info("=" * 60)
    
    if decision.top_10:
        logger.info("\n[TOP 10 HIGH-OPENING POTENTIAL STOCKS]")
        _print_table(decision.top_10)
    
    if decision.top_10_short:
        logger.info("\n[TOP 5 LOW-OPENING POTENTIAL STOCKS (HIGH SELLING PRESSURE)]")
        _print_table(decision.top_10_short)
        
    if decision.rejected:
        logger.info("\n[REJECTIONS]")
        for c in decision.rejected[:10]:
            logger.info(f"{c.symbol}: REJECTED - {c.reason}")

def _print_table(candidates):
    logger.info(f"{'RANK':<4} {'SYMBOL':<10} {'FINAL_SCORE':<11} {'IEP':<8} {'PREV':<8} {'GAP%':<7} {'IEQ':<9} {'EQ_IMB':<10} {'MO_IMB':<10} {'EV_CR':<8} {'ALIGN':<5}")
    logger.info("-" * 110)
    for c in candidates[:config.TOP_N_DISPLAY]:
        score = f"{c.opening_strength_score:.6f}"
        iep = f"{c.latest_iep:.2f}"
        prev = f"{c.prev_close:.2f}"
        gap = f"{c.gap_pct:.2f}"
        ev = f"{c.executable_value_cr:.6f}"
        align = f"{c.alignment_score:.1f}"
        
        logger.info(f"{c.rank:<4} {c.symbol:<10} {score:<11} {iep:<8} {prev:<8} {gap:<7} {c.latest_ieq:<9} {c.eq_imbalance_qty:<10} {c.mo_imbalance_qty:<10} {ev:<8} {align:<5}")

def _write_csv(candidates, path):
    rows = []
    for c in candidates[:config.TOP_N_DISPLAY]:
        rows.append({
            'RANK': c.rank,
            'SYMBOL': c.symbol,
            'FINAL_SCORE': c.opening_strength_score,
            'IEP': c.latest_iep,
            'PREV_CLOSE': c.prev_close,
            'GAP_PCT': c.gap_pct,
            'IEQ': c.latest_ieq,
            'EQ_IMBALANCE': c.eq_imbalance_qty,
            'MO_IMBALANCE': c.mo_imbalance_qty,
            'EXECUTABLE_VALUE_CR': c.executable_value_cr,
            'IEQ_PERCENTILE': c.ieq_percentile,
            'EQ_IMBALANCE_PERCENTILE': c.eq_imb_percentile,
            'MO_POSITIVE_PERCENTILE': c.mo_imb_percentile,
            'EXECUTABLE_VALUE_PERCENTILE': c.ev_percentile,
            'ALIGNMENT_SCORE': c.alignment_score
        })
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)

def _write_fno_csv(candidates, path):
    rows = []
    for c in candidates[:10]:
        rows.append({
            'RANK': c.rank,
            'SYMBOL': c.symbol,
            'FNO_SCORE': round(c.fno_combined_score, 2),
            'PRE_OPEN_SCORE': round(c.opening_strength_score, 2),
            'OI_SCORE': round(c.fno_oi_score * 100, 2),
            'BUILDUP': c.fno_buildup,
            'PCR': round(c.fno_pcr, 3),
            'ALIGN': c.alignment_score,
            'IEP': c.latest_iep,
            'PREV_CLOSE': c.prev_close,
            'GAP_PCT': round(c.gap_pct, 2),
            'EQ_IMBALANCE': c.eq_imbalance_qty,
            'MO_IMBALANCE': c.mo_imbalance_qty,
        })
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
