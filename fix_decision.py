import re

# Update orchestrator.py
with open('quant_engine/orchestrator.py', 'r', encoding='utf-8') as f:
    orch = f.read()
orch = orch.replace("decision = generate_final_decision(symbol, regime, context, trigger, execution)", "decision = generate_final_decision(symbol, regime, context, trigger, execution, technicals)")
with open('quant_engine/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(orch)

# Update decision.py
new_decision = '''from .models import FinalDecision, MarketRegime, StockContext, TriggerSetup, ExecutionFilter

def generate_final_decision(symbol: str, regime: MarketRegime, context: StockContext, trigger: TriggerSetup, execution: ExecutionFilter, technicals: dict) -> FinalDecision:
    # 1. Bias
    if context.trend_alignment == "BULLISH" and trigger.catalyst_direction != "BEARISH":
        bias = "LONG"
    elif context.trend_alignment == "BEARISH" and trigger.catalyst_direction != "BULLISH":
        bias = "SHORT"
    else:
        bias = "NEUTRAL"
        
    # 2. Setup State
    if execution.tradeability == "BLOCKED":
        setup = "BLOCKED"
    elif trigger.catalyst_strength in ["STRONG", "MODERATE"]:
        setup = "READY"
    else:
        setup = "WAIT_FOR_CONFIRMATION"
        
    # 3. Dynamic Execution conditions
    pdh = technicals.get('Previous_High', 0)
    pdl = technicals.get('Previous_Low', 0)
    ema20 = technicals.get('EMA_20', 0)
    
    if bias == "LONG":
        entry = f"Break above PDH (?{pdh:.1f})" if pdh > 0 else "Break above 5-min High"
        inval = f"Close below 20-EMA (?{ema20:.1f})" if ema20 > 0 else "Close below Day Low"
    elif bias == "SHORT":
        entry = f"Break below PDL (?{pdl:.1f})" if pdl > 0 else "Break below 5-min Low"
        inval = f"Close above 20-EMA (?{ema20:.1f})" if ema20 > 0 else "Close above Day High"
    else:
        entry = "WAIT (No directional bias)"
        inval = "N/A"
        
    return FinalDecision(
        symbol=symbol,
        directional_bias=bias,
        setup_state=setup,
        confidence=75,
        tradeability=execution.tradeability,
        entry_condition=entry,
        invalidation=inval,
        regime=regime,
        context=context,
        trigger=trigger,
        execution=execution
    )'''
with open('quant_engine/decision.py', 'w', encoding='utf-8') as f:
    f.write(new_decision)
print('Fixed dynamic execution conditions.')
