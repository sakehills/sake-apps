import sqlite3
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
BACKUP_DIR = r"C:\Users\hitos\Antigravity-Playground\japanese-sake-db\database-backup"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

csv_files = [f for f in sorted(os.listdir(BACKUP_DIR)) if f.endswith(".csv")]

for f in csv_files:
    table_name = os.path.splitext(f)[0]
    csv_path = os.path.join(BACKUP_DIR, f)
    
    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as csv_file:
        reader = csv.reader(csv_file)
        csv_cols = next(reader, [])
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    db_info = cursor.fetchall()
    db_cols = [c[1] for c in db_info]
    pk_cols = [c[1] for c in db_info if c[5] > 0]
    
    print(f"\n==================== {table_name} ====================")
    print(f"Primary Key in DB: {pk_cols}")
    
    missing_in_db = [c for c in csv_cols if c not in db_cols]
    missing_in_csv = [c for c in db_cols if c not in csv_cols]
    
    if missing_in_db:
        print(f"  [+] Columns in CSV but missing in DB: {missing_in_db}")
    if missing_in_csv:
        print(f"  [-] Columns in DB but missing in CSV: {missing_in_csv}")
    if not missing_in_db and not missing_in_csv:
        print("  [=] Column lists match completely.")
