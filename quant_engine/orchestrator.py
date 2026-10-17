import json
import dataclasses
from .market_regime import evaluate_market_regime
from .stock_context import evaluate_stock_context
from .trigger import evaluate_trigger
from .execution import evaluate_execution
from .decision import generate_final_decision

import numpy as np

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.bool_):
            return bool(o)
        return super().default(o)

def run_v2_engine(symbol: str, global_data: dict, nse_data: dict, technicals: dict, sector_data: dict, llm_analysis: dict) -> dict:
    """
    Main entry point for V2.0 Quant Engine.
    Passes data through the 4-Layer hierarchical gating system.
    """
    regime = evaluate_market_regime(global_data, nse_data)
    context = evaluate_stock_context(technicals, sector_data)
    trigger = evaluate_trigger(technicals, nse_data, llm_analysis)
    execution = evaluate_execution(trigger, context, technicals, llm_analysis, nse_data)
    
    decision = generate_final_decision(symbol, regime, context, trigger, execution, technicals)
    
    # Convert dataclass to dict using our custom encoder so it's JSON serializable
    return json.loads(json.dumps(decision, cls=EnhancedJSONEncoder))
