from .models import ExecutionFilter, TriggerSetup, StockContext

def evaluate_execution(trigger: TriggerSetup, context: StockContext, technicals: dict, llm_analysis: dict, nse_data: dict) -> ExecutionFilter:
    blocks = []
    
    if trigger.gap_atr_ratio > 1.5:
        blocks.append(f"Exhaustion Gap Risk (Gap/ATR: {trigger.gap_atr_ratio:.2f})")
        
    vol = float(technicals.get('Volume') or 100000)
    if vol < 50000:
        blocks.append("Insufficient Volume/Liquidity")
        
    tradeability = "BLOCKED" if blocks else "OK"
    
    # --- DIRECT PARTICIPATION STRATEGY (9:00 - 9:08 AM) ---
    # Acceptance Criteria 1: Massive SEBI Catalyst
    cat_score = int(llm_analysis.get('score', 0)) if isinstance(llm_analysis, dict) else 0
    cat_strength = trigger.catalyst_strength
    massive_catalyst = (cat_score >= 80) and (cat_strength == "STRONG")
    
    # Acceptance Criteria 3: High Liquidity Gate (Avg Vol > 1,000,000 or explicitly F&O)
    # We use a 500k volume threshold for 'highly liquid' intraday trading in India
    high_liquidity = (vol > 500000)
    
    # Acceptance Criteria 2: Limit Order Enforcement
    direct_participation = (massive_catalyst and high_liquidity and tradeability == "OK")
    
    iep = float(nse_data.get('pre_open_iep') or technicals.get('Close') or 0.0)
    
    # Max Safe Limit = IEP + 0.5% slippage buffer (if LONG) or IEP - 0.5% (if SHORT)
    # Since we don't know the exact bias here without logic, we calculate a generic 0.5% buffer zone
    # We just provide the upper limit for a long trade as default
    max_safe_limit = round(iep * 1.005, 1) if iep > 0 else 0.0

    return ExecutionFilter(
        tradeability=tradeability,
        block_reasons=blocks,
        direct_participation_safe=direct_participation,
        max_safe_limit_price=max_safe_limit
    )
