import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == 'wl_df = add_birth_date_and_format(wl_df)':
        # Find the previous line's indentation
        prev_line = lines[i-1]
        indent = len(prev_line) - len(prev_line.lstrip())
        lines[i] = (' ' * indent) + 'wl_df = add_birth_date_and_format(wl_df)\n'
    elif line.strip() == 'df_short = add_birth_date_and_format(df_short)':
        prev_line = lines[i-1]
        indent = len(prev_line) - len(prev_line.lstrip())
        lines[i] = (' ' * indent) + 'df_short = add_birth_date_and_format(df_short)\n'
    elif line.strip() == 'df = add_birth_date_and_format(df)':
        prev_line = lines[i-1]
        indent = len(prev_line) - len(prev_line.lstrip())
        lines[i] = (' ' * indent) + 'df = add_birth_date_and_format(df)\n'

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
