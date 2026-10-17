import re
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

def_reversal = '''                
            def color_reversal(val):
                if val in ('CRITICAL', 'HIGH'): return 'color: #FF4B4B; font-weight: bold'
                if val == 'MEDIUM': return 'color: #FFA500'
                if val == 'NONE': return 'color: #00FF00'
                return ''
                
            def color_trend(val):
                try:
                    if float(val) > 0: return 'color: #00FF00'
                    if float(val) < 0: return 'color: #FF4B4B'
                except: pass
                return ''
'''

text = text.replace('''            def color_gap(val):
                try:
                    if float(val) > 3.0: return 'color: #00FF00'
                    if float(val) < 0.0: return 'color: #FF4B4B'
                except: pass
                return ''''', '''            def color_gap(val):
                try:
                    if float(val) > 3.0: return 'color: #00FF00'
                    if float(val) < 0.0: return 'color: #FF4B4B'
                except: pass
                return ''''' + def_reversal)

apply_colors = '''                if 'REVERSAL_RISK' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                if 'IEP_TREND' in df.columns:
                    styled_df = getattr(styled_df, 'map' if hasattr(styled_df, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                st.dataframe(styled_df, use_container_width=True)'''

text = text.replace('                st.dataframe(styled_df, use_container_width=True)', apply_colors, 1)

apply_colors_short = apply_colors.replace('styled_df', 'styled_df_short').replace('df.', 'df_short.')
text = text.replace('                    st.dataframe(styled_df_short, use_container_width=True)', '    ' + apply_colors_short)

apply_colors_wl = apply_colors.replace('styled_df', 'styled_wl').replace('df.', 'wl_df.')
text = text.replace('                    st.dataframe(styled_wl, use_container_width=True)', '    ' + apply_colors_wl)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
