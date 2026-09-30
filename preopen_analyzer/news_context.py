from .models import CatalystType
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_catalyst(symbol: str, news_data: Optional[Dict] = None) -> CatalystType:
    if not news_data:
        return CatalystType.UNKNOWN
    
    cat_str = news_data.get(symbol, "UNKNOWN")
    try:
        return CatalystType[cat_str]
    except KeyError:
        return CatalystType.UNKNOWN

def catalyst_score_modifier(catalyst: CatalystType) -> float:
    modifiers = {
        CatalystType.FRESH_POSITIVE: 3.0,
        CatalystType.POSITIVE_BACKGROUND: 1.0,
        CatalystType.NO_CLEAR_CATALYST: 0.0,
        CatalystType.UNKNOWN: 0.0,
        CatalystType.FRESH_NEGATIVE: -5.0
    }
    return modifiers.get(catalyst, 0.0)
