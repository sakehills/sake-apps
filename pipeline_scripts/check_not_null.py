import sqlite3
import os
import csv
import io
import sys

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
BACKUP_DIR = r"C:\Users\hitos\Antigravity-Playground\japanese-sake-db\database-backup"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

csv_files = [f for f in sorted(os.listdir(BACKUP_DIR)) if f.endswith(".csv")]

for f in csv_files:
    table_name = os.path.splitext(f)[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols_info = cursor.fetchall()
    not_null_cols = [c[1] for c in cols_info if c[3] == 1]
    
    csv_path = os.path.join(BACKUP_DIR, f)
    with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as cf:
        reader = csv.DictReader(cf)
        null_counts = {c: 0 for c in not_null_cols}
        total_rows = 0
        for r in reader:
            total_rows += 1
            for c in not_null_cols:
                if c in r and (r[c] is None or r[c] == ''):
                    null_counts[c] += 1
        
        has_issue = any(cnt > 0 for cnt in null_counts.values())
        if has_issue:
            print(f"[!] Table: {table_name} has empty values in NOT NULL columns: {null_counts}")
        else:
            print(f"[OK] Table: {table_name} ({total_rows} rows) - NOT NULL check passed.")
