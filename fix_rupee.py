with open('live_920_scanner.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the target zone formatting to just pass numbers, UI handles the Rupee sign
code = code.replace('target = f"?{last_price * 1.01:.1f} - ?{last_price * 1.015:.1f}"', 'target = f"{last_price * 1.01:.1f} - {last_price * 1.015:.1f}"')
with open('live_920_scanner.py', 'w', encoding='utf-8') as f:
    f.write(code)

with open('dashboard.py', 'r', encoding='utf-8') as f:
    dash = f.read()
    
dash = dash.replace('* **Target Zone:** {res.get(\'target_zone\')}', '* **Target Zone:** ?{res.get(\'target_zone\')}')
with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(dash)
    
print('Fixed Rupee symbol encoding issue.')
