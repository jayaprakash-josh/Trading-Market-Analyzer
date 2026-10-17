with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("c4.markdown(f\\"**Max Safe Limit:** ?{exec_f.get('max_safe_limit_price')}\\")", "c4.markdown(f\\"**Max Safe Limit:** Rs. {exec_f.get('max_safe_limit_price')}\\")")
code = code.replace("* **Target Zone:** ?{res.get('target_zone')}", "* **Target Zone:** Rs. {res.get('target_zone')}")

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
    
print('Replaced Rupee symbol with Rs. in dashboard.')
