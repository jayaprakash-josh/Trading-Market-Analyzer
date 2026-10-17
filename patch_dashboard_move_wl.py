import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start and end of the watchlist block
wl_start = -1
wl_end = -1
for i, line in enumerate(lines):
    if 'wl_csv_path = os.path.join(output_dir' in line:
        wl_start = i
    # The block ends after the else: st.info("Watchlist is currently empty...")
    if wl_start != -1 and 'st.info("Watchlist is currently empty or no valid data found.")' in line:
        wl_end = i + 1
        break

if wl_start != -1 and wl_end != -1:
    wl_lines = lines[wl_start:wl_end]
    del lines[wl_start:wl_end]
    
    # Now find where to insert it.
    # It should go right after the timestamp banner, before Top 10 High-Opening
    insert_idx = -1
    for i, line in enumerate(lines):
        if 'st.markdown("#### Top 10 High-Opening Potential Stocks")' in line:
            insert_idx = i
            break
            
    if insert_idx != -1:
        # Add some spacing
        wl_lines.insert(0, '            # CUSTOM WATCHLIST UI\n')
        wl_lines.append('            st.markdown("---")\n')
        lines = lines[:insert_idx] + wl_lines + lines[insert_idx:]
        
        with open('dashboard.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Success")
    else:
        print("Could not find insertion point.")
else:
    print(f"Could not find watchlist block. start={wl_start} end={wl_end}")

