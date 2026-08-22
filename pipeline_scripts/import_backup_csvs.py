import sqlite3
import os
import csv
import shutil
from datetime import datetime

import sys
import io

# UTF-8 stdout wrapper for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
BACKUP_DIR = r"C:\Users\hitos\Antigravity-Playground\japanese-sake-db\database-backup"

# 1. 既存DBのバックアップ
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
db_backup_path = os.path.join(BASE_DIR, "database", f"sake_database_pre_import_{timestamp}.db.bak")
print(f"[*] 既存データベースをバックアップ中: {db_backup_path}")
shutil.copy2(DB_PATH, db_backup_path)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# SQLite PRAGMA 最適化
cursor.execute("PRAGMA synchronous = OFF")
cursor.execute("PRAGMA journal_mode = MEMORY")

csv_files = [f for f in sorted(os.listdir(BACKUP_DIR)) if f.endswith(".csv")]

total_inserted_or_updated = {}

for f in csv_files:
    table_name = os.path.splitext(f)[0]
    csv_path = os.path.join(BACKUP_DIR, f)
    
    print(f"\n[*] テーブル '{table_name}' のインポート処理を開始...")
    
    with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, None)
        if not headers:
            print(f"  [!] 空のCSVです: {f}")
            continue
        
        # カラム名のクリーニング
        headers = [h.strip() for h in headers]
        
        # 既存テーブルのカラム確認
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols_info = cursor.fetchall()
        
        if not existing_cols_info:
            pk_col = headers[0]
            col_defs = [f'"{h}" TEXT' for h in headers]
            if pk_col == 'id':
                col_defs[0] = '"id" INTEGER PRIMARY KEY'
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"
            cursor.execute(create_stmt)
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_cols_info = cursor.fetchall()
            print(f"  [+] テーブル '{table_name}' を新規作成しました。")
        
        existing_cols = [c[1] for c in existing_cols_info]
        
        # 不足しているカラムを ALTER TABLE で追加
        for h in headers:
            if h not in existing_cols:
                print(f"  [+] 新規カラムを追加: {table_name}.{h}")
                cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{h}" TEXT')
                existing_cols.append(h)
        
        cols_str = ', '.join([f'"{h}"' for h in headers])
        placeholders = ', '.join(['?'] * len(headers))
        sql = f'INSERT OR REPLACE INTO {table_name} ({cols_str}) VALUES ({placeholders})'
        
        batch_data = []
        count = 0
        for row in reader:
            if len(row) < len(headers):
                row = row + [None] * (len(headers) - len(row))
            elif len(row) > len(headers):
                row = row[:len(headers)]
            
            processed_row = []
            for h, val in zip(headers, row):
                # products の NOT NULL 制約対策
                if table_name == 'products' and h == 'spec_name' and (val == '' or val is None):
                    # brand_name のインデックスを探して代用
                    brand_idx = headers.index('brand_name') if 'brand_name' in headers else -1
                    val = row[brand_idx] if (brand_idx != -1 and row[brand_idx]) else '特別品'
                
                if val == '' or val is None:
                    processed_row.append(None)
                else:
                    processed_row.append(val)
            
            batch_data.append(processed_row)
            count += 1
            
            if len(batch_data) >= 2000:
                cursor.executemany(sql, batch_data)
                batch_data = []
        
        if batch_data:
            cursor.executemany(sql, batch_data)
        
        total_inserted_or_updated[table_name] = count
        print(f"  [OK] {table_name}: {count} 件のデータをインポート/更新しました。")

conn.commit()

print("\n[*] データベースを最適化中 (ANALYZE)...")
cursor.execute("ANALYZE")
conn.commit()

print("\n==================== インポート結果サマリー ====================")
for t, count in total_inserted_or_updated.items():
    cursor.execute(f"SELECT count(*) FROM {t}")
    total_in_db = cursor.fetchone()[0]
    print(f" テーブル: {t:22} | CSV行数: {count:6} | DB現在行数: {total_in_db:6}")

conn.close()
print("\n[OK] すべてのCSVインポートおよび更新が正常に完了しました！")
