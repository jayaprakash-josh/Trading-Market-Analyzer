import sys
with open('preopen_analyzer/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("rejected: List[StockCandidate] = field(default_factory=list)", "rejected: List[StockCandidate] = field(default_factory=list)\n    all_long: List[StockCandidate] = field(default_factory=list)\n    all_short: List[StockCandidate] = field(default_factory=list)")

with open('preopen_analyzer/models.py', 'w', encoding='utf-8') as f:
    f.write(text)
