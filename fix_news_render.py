with open('dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = '''            else:
                c1.write("**NO MATERIAL CATALYST**")'''

new_block = '''            else:
                c1.write("**NO MATERIAL CATALYST**")
                
            sentiment = res.get('sentiment_data', {})
            raw_news = sentiment.get('latest_news', [])
            if raw_news:
                c1.markdown("---")
                c1.caption("Recent News Flow:")
                for idx, n in enumerate(raw_news[:5]):
                    c1.markdown(f"{idx+1}. [{n['title']}]({n['link']})")'''

code = code.replace(old_block, new_block)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Fixed news rendering in dashboard.')
