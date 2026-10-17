import re
with open('preopen_analyzer/models.py', 'r') as f:
    text = f.read()

text = text.replace('class StretchRisk(str, Enum):', 'class ReversalRisk(str, Enum):\n    NONE = "NONE"\n    LOW = "LOW"\n    MEDIUM = "MEDIUM"\n    HIGH = "HIGH"\n    CRITICAL = "CRITICAL"\n\nclass StretchRisk(str, Enum):')

text = text.replace('    # Status\n    order_flow_alignment', '    # Trend\n    max_iep: float = 0.0\n    iep_drawdown_pct: float = 0.0\n    max_ieq: int = 0\n    ieq_drawdown_pct: float = 0.0\n\n    # Status\n    order_flow_alignment')

text = text.replace('    stretch_risk: StretchRisk = StretchRisk.LOW\n', '    stretch_risk: StretchRisk = StretchRisk.LOW\n    reversal_risk: ReversalRisk = ReversalRisk.NONE\n')

with open('preopen_analyzer/models.py', 'w') as f:
    f.write(text)
