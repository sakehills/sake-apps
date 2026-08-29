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

# クローリングで取得した説明文系のノイズテキストを削除
cur.execute("""
    DELETE FROM products
    WHERE (
        spec_name LIKE '%を求めて%' OR
        spec_name LIKE '%として、%' OR
        spec_name LIKE '%特徴的な%' OR
        spec_name LIKE '%育てました%' OR
        spec_name LIKE '%磨き上げた%' OR
        spec_name LIKE '%素早くビン詰め%' OR
        spec_name LIKE '%本物の純生原酒%' OR
        spec_name LIKE '%そのまま練りひいた%'
    ) AND confidence = 1.0 AND evidence LIKE '%Official Web Crawler%'
""")

cleaned = cur.rowcount
print(f"🧹 ノイズ除去件数: {cleaned} 件")

# 東洋美人 一天の正式登録
cur.execute("""
    SELECT id FROM products WHERE spec_name = '東洋美人 純米大吟醸 一天' AND brewery_name LIKE '%澄川酒造場%'
""")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO products (
            brand_name, spec_name, category, polish_ratio, rice_variety,
            alcohol, brewery_name, prefecture, confidence, evidence, status
        ) VALUES (
            '東洋美人', '東洋美人 純米大吟醸 一天', '純米大吟醸酒', '40%', '山田錦',
            16.0, '株式会社澄川酒造場', '山口県', 1.0, 'Official Verified (https://toyobijin.jp/)', 'active'
        )
    """)
    print("✨ [正式登録] 東洋美人 純米大吟醸 一天 (JALファーストクラス提供酒)")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"🍶 最終製品総数: {total_prods} 件")

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
