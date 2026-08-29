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

# クローリングで取得した説明文系や食品・セット系ノイズテキストを削除
cur.execute("""
    DELETE FROM products
    WHERE (
        spec_name LIKE '%を求めて%' OR
        spec_name LIKE '%として、%' OR
        spec_name LIKE '%特徴的な%' OR
        spec_name LIKE '%チョコ%' OR
        spec_name LIKE '%セット%' OR
        spec_name LIKE '%搭載されました%' OR
        spec_name LIKE '%受賞いたしました%' OR
        spec_name LIKE '%選出されました%' OR
        spec_name LIKE '%登場！%' OR
        spec_name = '純米大吟醸' OR
        spec_name = '純米吟醸' OR
        spec_name = '純米酒' OR
        spec_name = '大吟醸' OR
        spec_name = 'リキュール' OR
        spec_name = 'スパークリング'
    ) AND confidence = 1.0 AND evidence LIKE '%Official Web Crawler%'
""")

cleaned = cur.rowcount
print(f"🧹 ノイズ除去件数: {cleaned} 件")

# 千代むすびの正式規格名への正規化
cur.execute("""
    UPDATE products
    SET spec_name = REPLACE(REPLACE(REPLACE(spec_name, ' 720ml(桐箱入り) | 千代むすび酒造オンラインストア', ''), ' 720ml', ''), ' 1.8L', '')
    WHERE brewery_name LIKE '%千代むすび%'
""")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"🍶 最終製品総数: {total_prods} 件")

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
