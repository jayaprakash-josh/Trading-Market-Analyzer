import sys
import os
import pandas as pd
import numpy as np

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.position_sizer import calculate_trade_levels, calculate_position_size
from core.opening_range import detect_opening_range

def test_trade_levels():
    print("Testing Trade Levels (LONG)...")
    levels = calculate_trade_levels(entry=100.0, or_high=99.0, or_low=95.0, vwap=96.0, atr=4.0, direction="LONG")
    # buffer = 0.25 * 4 = 1.0
    # max(or_low, vwap) = 96.0
    # sl = 96.0 - 1.0 = 95.0
    assert levels['stop_loss'] == 95.0
    # risk = 100 - 95 = 5
    # T1 = 100 + 1.5*5 = 107.5
    assert levels['target_1'] == 107.5
    # T2 = 100 + 2.5*5 = 112.5
    assert levels['target_2'] == 112.5
    print("  -> Passed.")
    
    print("Testing Trade Levels (SHORT)...")
    levels = calculate_trade_levels(entry=90.0, or_high=95.0, or_low=91.0, vwap=94.0, atr=4.0, direction="SHORT")
    # buffer = 1.0
    # min(or_high, vwap) = 94.0
    # sl = 94.0 + 1.0 = 95.0
    assert levels['stop_loss'] == 95.0
    # risk = 95 - 90 = 5
    # T1 = 90 - 1.5*5 = 82.5
    assert levels['target_1'] == 82.5
    # T2 = 90 - 2.5*5 = 77.5
    assert levels['target_2'] == 77.5
    print("  -> Passed.")

def test_position_size():
    print("Testing Position Size (Normal)...")
    res = calculate_position_size(entry=100, stop_loss=90, capital=100000, risk_pct=1.0, max_position_pct=20)
    # risk_budget = 1000, stop_dist = 10
    # qty = 100
    # pos_val = 10000 (10% of cap, allowed)
    assert res['quantity'] == 100
    assert res['capped'] == False
    print("  -> Passed.")
    
    print("Testing Position Size (Capped)...")
    res = calculate_position_size(entry=100, stop_loss=99.5, capital=100000, risk_pct=1.0, max_position_pct=20)
    # risk_budget = 1000, stop_dist = 0.5
    # raw_qty = 2000
    # pos_val would be 200,000 > cap of 20,000
    # max_qty = 20,000 / 100 = 200
    assert res['quantity'] == 200
    assert res['capped'] == True
    print("  -> Passed.")

if __name__ == "__main__":
    test_trade_levels()
    test_position_size()
    print("ALL TESTS PASSED!")
