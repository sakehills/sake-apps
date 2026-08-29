import os
import sys
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    DELETE FROM products
    WHERE spec_name LIKE '>%'
       OR spec_name LIKE '%定義に準じます%'
       OR spec_name LIKE '%寄附いたしました%'
       OR spec_name LIKE '%せいろ蒸し%'
       OR spec_name LIKE '%商品一覧%'
""")

cleaned = cur.rowcount
print(f"🧹 ノイズ除外件数: {cleaned} 件")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"🍶 最終製品総数: {total_prods} 件")

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
