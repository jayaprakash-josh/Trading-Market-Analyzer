from .models import MarketBias
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def calculate_market_bias(market_data: Optional[Dict] = None) -> MarketBias:
    if not market_data:
        return MarketBias.NEUTRAL

    bias_score = 0
    nifty_change_pct = market_data.get('nifty_change_pct')
    gift_nifty_change_pct = market_data.get('gift_nifty_change_pct')
    india_vix = market_data.get('india_vix')
    india_vix_change_pct = market_data.get('india_vix_change_pct')
    fii_net_cr = market_data.get('fii_net_cr')

    if nifty_change_pct is not None:
        if nifty_change_pct > 1.0:
            bias_score += 3
        elif nifty_change_pct > 0.5:
            bias_score += 2
        elif nifty_change_pct < -1.0:
            bias_score -= 3
        elif nifty_change_pct < -0.5:
            bias_score -= 2

    if gift_nifty_change_pct is not None:
        if gift_nifty_change_pct > 0.5:
            bias_score += 1
        elif gift_nifty_change_pct < -0.5:
            bias_score -= 1

    if india_vix is not None:
        if india_vix > 20 and india_vix_change_pct is not None and india_vix_change_pct > 0:
            bias_score -= 1
        elif india_vix < 15:
            bias_score += 1

    if fii_net_cr is not None:
        if fii_net_cr > 1000:
            bias_score += 1
        elif fii_net_cr < -1000:
            bias_score -= 1

    if bias_score >= 3:
        return MarketBias.BULLISH
    elif bias_score <= -3:
        return MarketBias.BEARISH
    else:
        return MarketBias.NEUTRAL

def format_market_context(market_data: Optional[Dict], bias: MarketBias) -> str:
    if not market_data:
        return f"Market Bias: {bias.name} (No context provided)"
    
    parts = []
    if 'nifty_change_pct' in market_data:
        parts.append(f"NIFTY: {market_data['nifty_change_pct']}%")
    if 'banknifty_change_pct' in market_data:
        parts.append(f"BANKNIFTY: {market_data['banknifty_change_pct']}%")
    if 'gift_nifty_change_pct' in market_data:
        parts.append(f"GIFT NIFTY: {market_data['gift_nifty_change_pct']}%")
    if 'india_vix' in market_data:
        parts.append(f"VIX: {market_data['india_vix']}")
    
    return f"Market Bias: {bias.name} ({', '.join(parts)})"
