with open('quant_engine/models.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_exec = '''@dataclass
class ExecutionFilter:
    tradeability: str  # OK, CAUTION, BLOCKED
    block_reasons: List[str] = field(default_factory=list)'''

new_exec = '''@dataclass
class ExecutionFilter:
    tradeability: str  # OK, CAUTION, BLOCKED
    block_reasons: List[str] = field(default_factory=list)
    direct_participation_safe: bool = False
    max_safe_limit_price: float = 0.0'''

code = code.replace(old_exec, new_exec)
with open('quant_engine/models.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated models.py')
