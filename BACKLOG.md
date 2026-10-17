# Project Backlog

## [Story] Direct Participation Strategy (High Risk Execution)
**Status**: Backlog
**Priority**: Medium

### Description
Implement a specialized execution profile for the 9:00–9:08 AM pre-market window. The engine should flag specific stocks as safe for "Direct Pre-Market Execution" ONLY if they meet extremely strict criteria.

### Acceptance Criteria
The system must generate a specialized alert/flag for Direct Pre-Market Participation if and only if ALL of the following are true:
1. **Massive SEBI Catalyst**: The LLM Catalyst Engine must score the catalyst as STRONG (>80/100) based on highly material, fresh news (e.g., blockbuster earnings, massive order win).
2. **Limit Order Enforcement**: The UI/Execution module must explicitly recommend a Limit Order and calculate the maximum safe limit price to prevent getting filled at a 10% premium due to institutional order book manipulation. Market orders must be strictly warned against.
3. **High Liquidity Gate**: The stock must be filtered by a strict liquidity gate (e.g., must belong to the F&O list or Nifty 50). Illiquid stocks must be hard-blocked from pre-market execution to prevent wild price swings.

