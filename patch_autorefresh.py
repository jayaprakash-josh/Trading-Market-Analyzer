import sys
with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'auto_refresh = st.sidebar.toggle("\U0001f504 Auto-Refresh Pre-Open (15s)")\n    if auto_refresh:\n        import time\n        with st.spinner("Auto-fetching live pre-open data... Next refresh in 15s"):\n            subprocess.run(["python", "preopen_v2.py"], shell=True)\n        time.sleep(15)\n        st.rerun()',
    'auto_refresh = st.sidebar.toggle("\U0001f504 Auto-Refresh UI (30s)")\n    if auto_refresh:\n        import time\n        time.sleep(30)\n        st.rerun()'
)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
