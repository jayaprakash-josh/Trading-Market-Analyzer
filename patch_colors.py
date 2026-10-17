import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract the color functions
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.strip() == 'def color_signal(val):':
        start_idx = i
    if start_idx != -1 and line.strip() == "df = pd.read_csv(csv_path)":
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    color_funcs = lines[start_idx:end_idx]
    
    # Remove from old position
    del lines[start_idx:end_idx]
    
    # Clean up indentation (unindent them since they will go to the top level)
    # The original indentation is 12 spaces.
    unindented_funcs = []
    for line in color_funcs:
        if line.startswith('            '):
            unindented_funcs.append(line[12:])
        elif line.strip() == '':
            unindented_funcs.append(line)
        else:
            unindented_funcs.append(line)

    # Insert after import statements at the top
    insert_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('st.set_page_config'):
            insert_idx = i + 1
            break
            
    if insert_idx != -1:
        lines = lines[:insert_idx] + ['\n'] + unindented_funcs + ['\n'] + lines[insert_idx:]
        
        with open('dashboard.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Successfully moved color functions to top level.")
    else:
        print("Could not find insertion point.")
else:
    print("Could not find color functions block.")
