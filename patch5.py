import re
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad_block = '''                    if 'REVERSAL_RISK' in df_short.columns:
                    styled_df_short = getattr(styled_df_short, 'map' if hasattr(styled_df_short, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                if 'IEP_TREND' in df_short.columns:
                    styled_df_short = getattr(styled_df_short, 'map' if hasattr(styled_df_short, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                st.dataframe(styled_df_short, use_container_width=True)
                else:
                    st.dataframe(df_short, use_container_width=True)'''

good_block = '''                    if 'REVERSAL_RISK' in df_short.columns:
                        styled_df_short = getattr(styled_df_short, 'map' if hasattr(styled_df_short, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                    if 'IEP_TREND' in df_short.columns:
                        styled_df_short = getattr(styled_df_short, 'map' if hasattr(styled_df_short, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                    st.dataframe(styled_df_short, use_container_width=True)
                else:
                    st.dataframe(df_short, use_container_width=True)'''

text = text.replace(bad_block, good_block)

bad_block2 = '''                    if 'REVERSAL_RISK' in wl_df.columns:
                    styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                if 'IEP_TREND' in wl_df.columns:
                    styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                st.dataframe(styled_wl, use_container_width=True)'''

good_block2 = '''                    if 'REVERSAL_RISK' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_reversal, subset=['REVERSAL_RISK'])
                    if 'IEP_TREND' in wl_df.columns:
                        styled_wl = getattr(styled_wl, 'map' if hasattr(styled_wl, 'map') else 'applymap')(color_trend, subset=['IEP_TREND'])
                    st.dataframe(styled_wl, use_container_width=True)'''
                    
text = text.replace(bad_block2, good_block2)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
