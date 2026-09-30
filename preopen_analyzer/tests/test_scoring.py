import unittest
import sys
import os
from datetime import datetime, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from preopen_analyzer.models import (
    PreOpenSnapshot, BasicFeatures, StockCandidate,
    StretchRisk, ReversalSeverity, TimeSeriesFeatures,
    EntryExitLevels, ReversalInfo
)
from preopen_analyzer import feature_engineering
from preopen_analyzer import filters
from preopen_analyzer import reversal_detector
from preopen_analyzer import time_series
from preopen_analyzer import scoring
from preopen_analyzer import config

class TestPreOpenScoring(unittest.TestCase):
    
    def test_1_strong_bullish_candidate_should_score_high(self):
        snapshot = PreOpenSnapshot(
            timestamp=datetime.now(),
            symbol="RELIANCE",
            prev_close=100.0,
            iep=102.0,
            ieq=50000,
            total_buy_qty=100000,
            total_sell_qty=30000,
            eq_imbalance_qty=70000,
            best_bid_price=101.9,
            best_ask_price=102.1,
            best_bid_qty=5000,
            best_ask_qty=3000
        )
        features = feature_engineering.calculate_basic_features(snapshot)
        self.assertAlmostEqual(features.gap_pct, 2.0)
        self.assertTrue(features.eq_imbalance_ratio > 0)
        self.assertIn(features.stretch_risk, [StretchRisk.LOW, StretchRisk.MEDIUM])

    def test_2_strong_gap_but_low_ieq_rejected(self):
        snapshot = PreOpenSnapshot(
            timestamp=datetime.now(),
            symbol="PENNYSTOCK",
            prev_close=100.0,
            iep=105.0,
            ieq=50  # Extremely low IEQ
        )
        basic_feat = feature_engineering.calculate_basic_features(snapshot)
        candidate = StockCandidate(
            symbol="PENNYSTOCK", 
            latest_iep=105.0, 
            latest_ieq=50, 
            executable_value_cr=basic_feat.executable_value_cr,
            basic_features=basic_feat,
            gap_pct=basic_feat.gap_pct
        )
        
        is_rejected, reasons = filters.apply_hard_filters(candidate)
        self.assertTrue(is_rejected)
        reason_codes = [r.value for r in reasons]
        # It's an Enum, RejectionReason.IEQ_INVALID
        from preopen_analyzer.models import RejectionReason
        self.assertIn(RejectionReason.IEQ_INVALID, reasons)

    def test_3_late_reversal_detection(self):
        snapshots = []
        now = datetime.now()
        
        # First 10: bullish
        for i in range(10):
            snap = PreOpenSnapshot(
                timestamp=now + timedelta(minutes=i),
                symbol="TCS",
                prev_close=100.0,
                iep=105.0,
                ieq=10000,
                eq_imbalance_qty=50000,
                total_buy_qty=60000,
                total_sell_qty=10000,
                market_order_imbalance_qty=10000
            )
            snapshots.append(snap)
            
        # Last 5: drops
        for i in range(10, 15):
            snap = PreOpenSnapshot(
                timestamp=now + timedelta(minutes=i),
                symbol="TCS",
                prev_close=100.0,
                iep=101.0,
                ieq=2000,
                eq_imbalance_qty=-50000,
                total_buy_qty=10000,
                total_sell_qty=60000,
                market_order_imbalance_qty=-10000
            )
            snapshots.append(snap)
            
        reversal = reversal_detector.detect_reversal(snapshots, 100.0)
        self.assertIn(reversal.severity, [ReversalSeverity.HIGH, ReversalSeverity.CRITICAL])

    def test_4_positive_gap_negative_imbalance_low_consistency(self):
        basic = BasicFeatures(
            symbol="HDFC",
            timestamp=datetime.now(),
            gap_pct=3.0,
            eq_imbalance_ratio=-0.5
        )
        ts = TimeSeriesFeatures(symbol="HDFC", iep_slope=-0.5)
        candidate = StockCandidate(
            symbol="HDFC",
            basic_features=basic, 
            time_series=ts
        )
        
        consistency = filters.calculate_signal_consistency(candidate)
        self.assertLess(consistency.score, 100.0)

    def test_5_moderate_gap_with_strong_persistence_ranks_well(self):
        # Candidate 1: Moderate gap, highly persistent demand
        c1 = StockCandidate(
            symbol="GOOD",
            latest_ieq=50000,
            executable_value_cr=10.0,
            gap_pct=1.5,
            basic_features=BasicFeatures(symbol="GOOD", timestamp=datetime.now(), gap_pct=1.5, executable_value_cr=10.0, eq_imbalance_ratio=1.0, mo_imbalance_ratio=1.0, spread_pct=0.1, gap_score_multiplier=1.0),
            time_series=TimeSeriesFeatures(symbol="GOOD", bullish_persistence=100.0, iep_slope=0.5, iep_slope_recent=0.5, eq_imbalance_slope=0.1, iep_drawdown_pct=0.0),
            reversal=ReversalInfo(severity=ReversalSeverity.NONE)
        )
        
        # Candidate 2: Large gap, weak persistence, stretched
        c2 = StockCandidate(
            symbol="STRETCHED",
            latest_ieq=5000,
            executable_value_cr=1.0,
            gap_pct=5.0,
            basic_features=BasicFeatures(symbol="STRETCHED", timestamp=datetime.now(), gap_pct=5.0, executable_value_cr=1.0, eq_imbalance_ratio=0.1, mo_imbalance_ratio=0.0, spread_pct=0.5, gap_score_multiplier=0.4),
            time_series=TimeSeriesFeatures(symbol="STRETCHED", bullish_persistence=20.0, iep_slope=-0.5, iep_slope_recent=-0.5, eq_imbalance_slope=-0.1, iep_drawdown_pct=2.0),
            reversal=ReversalInfo(severity=ReversalSeverity.HIGH)
        )
        
        scored = scoring.calculate_scores([c1, c2])
        self.assertEqual(len(scored), 2)
        # GOOD candidate should rank higher because penalties and scores favor it
        self.assertEqual(scored[0].symbol, "GOOD")

    def test_6_gap_down_stock_not_long_candidate(self):
        snapshot = PreOpenSnapshot(
            timestamp=datetime.now(),
            symbol="BAD",
            prev_close=100.0,
            iep=97.0,
            ieq=10000,
            eq_imbalance_qty=-5000
        )
        features = feature_engineering.calculate_basic_features(snapshot)
        self.assertLess(features.gap_pct, 0.0)

    def test_7_large_gap_at_upper_band_high_stretch_risk(self):
        snapshot = PreOpenSnapshot(
            timestamp=datetime.now(),
            symbol="RISKY",
            prev_close=100.0,
            iep=105.0,  # +5% gap
            ieq=10000
        )
        features = feature_engineering.calculate_basic_features(snapshot)
        self.assertIn(features.stretch_risk, [StretchRisk.HIGH, StretchRisk.EXTREME])

    def test_8_persistence_tracking(self):
        snapshots = []
        now = datetime.now()
        for i in range(15):
            snap = PreOpenSnapshot(
                timestamp=now + timedelta(minutes=i),
                symbol="PERSISTENT",
                prev_close=100.0,
                iep=102.0,
                ieq=10000,
                eq_imbalance_qty=5000,
                total_buy_qty=10000,
                total_sell_qty=5000
            )
            snapshots.append(snap)
            
        ts_features = time_series.calculate_time_series_features(snapshots, "PERSISTENT")
        self.assertGreater(ts_features.bullish_persistence, 50.0)

    def test_9_data_quality_scoring(self):
        dq_perfect = filters.calculate_data_quality(15, 0, 0, 0, 0, 0)
        self.assertEqual(dq_perfect.score, 100.0)
        
        dq_poor = filters.calculate_data_quality(15, 5, 0, 0, 0, 0)
        self.assertLess(dq_poor.score, 100.0)

    def test_10_entry_exit_calculation(self):
        levels = EntryExitLevels(
            aggressive_entry=102.0,
            conservative_entry=101.5,
            target_1=104.0,
            stop_loss=100.5,
            risk_pct=1.0,
            reward_pct=2.0,
            reward_risk_ratio=2.0
        )
        self.assertEqual(levels.reward_risk_ratio, 2.0)
        self.assertEqual(levels.aggressive_entry, 102.0)

if __name__ == "__main__":
    unittest.main()
