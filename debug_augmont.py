import os
import json
from datetime import datetime
from preopen_analyzer.data_store import SnapshotStore
from preopen_analyzer.main import PreOpenAnalyzer
from preopen_analyzer import config
from preopen_analyzer.scoring import calculate_scores
from preopen_analyzer.filters import apply_hard_filters

analyzer = PreOpenAnalyzer()
store = SnapshotStore()
today = datetime.now().date()
snapshots = store.get_all_symbols_latest(today)

print(f"Total snapshots loaded: {len(snapshots)}")

# Let's extract AUGMONT
aug = next((s for s in snapshots if s.symbol == 'AUGMONT'), None)
if aug:
    print(f"Found AUGMONT in raw snapshots: IEP={aug.iep} PREV={aug.prev_close} IEQ={aug.ieq} EQ_IMB={aug.eq_imbalance_qty} MO_IMB={aug.mo_imbalance_qty}")
else:
    print("AUGMONT not found in raw database!")

# Let's run build_candidates
cands = analyzer._build_candidates(snapshots, "LONG")
aug_cand = next((c for c in cands if c.symbol == 'AUGMONT'), None)
if aug_cand:
    print(f"After build_candidates, AUGMONT final score: {aug_cand.opening_strength_score}")
    print(f"Rejected? {aug_cand.is_rejected} - Reason: {aug_cand.rejection_reason}")
    print(f"Metrics: IEQ_Pct={aug_cand.metrics.get('ieq_pct')}, EQ_Imb_Pct={aug_cand.metrics.get('eq_imb_pct')}, Align={aug_cand.alignment_score}")
else:
    print("AUGMONT not in candidates list!")

cands.sort(key=lambda x: x.opening_strength_score, reverse=True)
rank = next((i+1 for i, c in enumerate(cands) if c.symbol == 'AUGMONT'), -1)
print(f"AUGMONT Rank in universe: {rank} out of {len([c for c in cands if not c.is_rejected])}")

