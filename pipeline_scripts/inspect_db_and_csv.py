import sqlite3
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
BACKUP_DIR = r"C:\Users\hitos\Antigravity-Playground\japanese-sake-db\database-backup"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

print("=== DB Tables & Row Counts ===")
for t in tables:
    cursor.execute(f"SELECT count(*) FROM {t}")
    cnt = cursor.fetchone()[0]
    cursor.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cursor.fetchall()]
    pk_cols = [c[1] for c in cursor.fetchall() if c[5] > 0]
    print(f"Table: {t:25} | Rows: {cnt:6} | Cols: {len(cols)}")

print("\n=== Backup CSV Files & Headers ===")
if os.path.exists(BACKUP_DIR):
    for f in sorted(os.listdir(BACKUP_DIR)):
        if f.endswith(".csv"):
            csv_path = os.path.join(BACKUP_DIR, f)
            with open(csv_path, mode='r', encoding='utf-8', errors='replace') as csv_file:
                reader = csv.reader(csv_file)
                headers = next(reader, None)
                row_count = sum(1 for _ in reader)
                print(f"CSV: {f:25} | Rows: {row_count:6} | Cols: {len(headers) if headers else 0}")
