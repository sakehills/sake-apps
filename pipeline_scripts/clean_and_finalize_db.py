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

# クローリングで取得した不要なナビゲーションテキストや長文ゴミデータをクリーニング
cur.execute("""
    DELETE FROM products
    WHERE (
        spec_name LIKE '%公式サイト%' OR
        spec_name LIKE '%について%' OR
        spec_name LIKE '%全て見る%' OR
        spec_name LIKE '%一覧%' OR
        spec_name LIKE '%創業%' OR
        spec_name LIKE '%私たちの%' OR
        spec_name LIKE '%メーカーです%' OR
        spec_name LIKE '%オンラインショップ%' OR
        spec_name LIKE '%カート%' OR
        spec_name LIKE '%購入%' OR
        spec_name LIKE '%ログイン%' OR
        spec_name LIKE '%プライバシーポリシー%' OR
        LENGTH(spec_name) > 40
    ) AND confidence = 1.0 AND evidence LIKE '%Official Web Crawler%'
""")

cleaned_deleted = cur.rowcount
print(f"🧹 ノイズデータ クリーニング削除数: {cleaned_deleted} 件")

# 有効な製品数を取得
cur.execute("SELECT COUNT(*) FROM products")
total_products = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
total_breweries = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"🍶 最終クリーン後 製品総数: {total_products} 件")
print(f"🏭 紐付け酒蔵総数: {total_breweries} 蔵")

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
