with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_exec = '''            exec_f = v2.get('execution', {})
            c4.markdown("#### ??? Execution Filter", help="Layer 4: Final hard gates. Blocks trades with insufficient liquidity or dangerous Reward/Risk profiles.")
            c4.markdown(f"**Condition:** {v2.get('entry_condition')}")
            c4.markdown(f"**Invalidation:** {v2.get('invalidation')}")
            if exec_f.get('block_reasons'):
                for b in exec_f.get('block_reasons'):
                    c4.error(b)'''

new_exec = '''            exec_f = v2.get('execution', {})
            c4.markdown("#### ??? Execution Filter", help="Layer 4: Final hard gates. Blocks trades with insufficient liquidity or dangerous Reward/Risk profiles.")
            c4.markdown(f"**Condition:** {v2.get('entry_condition')}")
            c4.markdown(f"**Invalidation:** {v2.get('invalidation')}")
            if exec_f.get('block_reasons'):
                for b in exec_f.get('block_reasons'):
                    c4.error(b)
                    
            # Direct Participation Strategy UI
            if exec_f.get('direct_participation_safe'):
                c4.markdown("---")
                c4.success("?? **DIRECT PARTICIPATION SAFE**")
                c4.markdown(f"**Max Safe Limit:** ?{exec_f.get('max_safe_limit_price')}")
                c4.caption("LIMIT ORDERS ONLY. Massive Catalyst & High Liquidity detected.")
            else:
                c4.markdown("---")
                c4.info("?? **Direct Pre-Market Unsafe** (Wait for 9:15 AM)")'''

code = code.replace(old_exec, new_exec)
with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated dashboard with Direct Participation.')
