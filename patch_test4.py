import sys

with open('test_csv_run.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace analyzer instantiation to use an in-memory DB or test DB
replacement = '''
    import sqlite3
    from preopen_analyzer.data_store import SnapshotStore
    # Use an isolated test database file
    test_db = "test_run.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    test_store = SnapshotStore(test_db)
    
    analyzer = PreOpenAnalyzer()
    analyzer._store = test_store
    analyzer._snapshot_number = 5
'''

text = text.replace(
    'analyzer = PreOpenAnalyzer()\n    analyzer._snapshot_number = 5',
    replacement
)

with open('test_csv_run.py', 'w', encoding='utf-8') as f:
    f.write(text)
