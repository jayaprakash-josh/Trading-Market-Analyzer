from test_csv_run import run
import logging
logging.getLogger().setLevel(logging.CRITICAL) # Suppress log output so we can see stdout cleanly

import sys
from io import StringIO
from preopen_analyzer.main import PreOpenAnalyzer

class MockAnalyzer(PreOpenAnalyzer):
    def _produce_final_decision(self):
        decision = super()._produce_final_decision()
        for c in decision.top_10 + decision.rejected:
            if c.symbol == 'HEROMOTORS':
                print(f"FOUND HEROMOTORS!")
                print(f"REJECTED: {c.is_rejected} - {c.reason}")
                print(f"RANK: {c.rank}")
                print(f"SCORE: {c.opening_strength_score}")
                print(f"GAP_PCT: {c.gap_pct}, STRETCH: {c.stretch_risk.name}")
        return decision

import preopen_analyzer.test_csv_run as tcr
# Hook into it
original_analyzer = tcr.PreOpenAnalyzer
tcr.PreOpenAnalyzer = MockAnalyzer
tcr.run()
