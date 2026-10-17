import re

with open('quant_engine/orchestrator.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_encoder = '''import numpy as np

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
        return super().default(o)'''

pattern = re.compile(r'class EnhancedJSONEncoder\(json\.JSONEncoder\):.*?return super\(\)\.default\(o\)', re.DOTALL)
code = pattern.sub(new_encoder, code)

with open('quant_engine/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed JSON Encoder.')
