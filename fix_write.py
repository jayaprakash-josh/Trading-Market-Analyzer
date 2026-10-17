with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace .write with .markdown for lines containing help=
import re
def replacer(match):
    return match.group(0).replace('.write(', '.markdown(')

pattern = re.compile(r'c\d\.write\(.*?, help=".*?"\)')
code = pattern.sub(replacer, code)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed write() to markdown() for help kwargs.')
