import re
with open('preopen_analyzer/scoring.py', 'r') as f:
    text = f.read()

text = text.replace('OrderFlowAlignment, StretchRisk, Signal', 'OrderFlowAlignment, StretchRisk, Signal, ReversalRisk')

reversal_logic = '''        # 9. Reversal Risk (EARLY STRONG + LATE WEAK)
        if direction == "LONG":
            if c.iep_drawdown_pct > 2.0 or c.ieq_drawdown_pct > 20.0 or c.iep_slope < 0:
                c.reversal_risk = ReversalRisk.CRITICAL
            elif c.iep_drawdown_pct > 1.0 or c.ieq_drawdown_pct > 10.0:
                c.reversal_risk = ReversalRisk.HIGH
            elif c.iep_drawdown_pct > 0.5 or c.ieq_drawdown_pct > 5.0:
                c.reversal_risk = ReversalRisk.MEDIUM
            elif c.iep_drawdown_pct > 0.0 or c.ieq_drawdown_pct > 0.0:
                c.reversal_risk = ReversalRisk.LOW
        else: # SHORT
            if c.iep_slope > 0:
                c.reversal_risk = ReversalRisk.CRITICAL
            elif c.ieq_drawdown_pct > 20.0:
                c.reversal_risk = ReversalRisk.HIGH
                
        base_score = gap_pts + eq_pts + mo_pts + ieq_pts + ev_pts + align_pts + liq_pts
        
        # Penalties
        penalties = 0.0
        if c.stretch_risk == StretchRisk.VERY_HIGH:
            penalties += 10.0
        elif c.stretch_risk == StretchRisk.EXTREME:
            penalties += 20.0
            
        if c.order_flow_alignment == OrderFlowAlignment.CONTRADICTORY:
            penalties += 15.0
            
        if c.reversal_risk == ReversalRisk.CRITICAL:
            penalties += 30.0
        elif c.reversal_risk == ReversalRisk.HIGH:
            penalties += 15.0
'''

text = text.replace('''        base_score = gap_pts + eq_pts + mo_pts + ieq_pts + ev_pts + align_pts + liq_pts
        
        # Penalties
        penalties = 0.0
        if c.stretch_risk == StretchRisk.VERY_HIGH:
            penalties += 10.0
        elif c.stretch_risk == StretchRisk.EXTREME:
            penalties += 20.0
            
        if c.order_flow_alignment == OrderFlowAlignment.CONTRADICTORY:
            penalties += 15.0''', reversal_logic)

with open('preopen_analyzer/scoring.py', 'w') as f:
    f.write(text)
