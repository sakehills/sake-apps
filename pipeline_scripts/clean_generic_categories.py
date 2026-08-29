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

# 単体カテゴリ名や完売・0件テキストの除外
cur.execute("""
    DELETE FROM products
    WHERE spec_name IN (
        '大吟醸', '純米大吟醸', '純米吟醸', '特別純米', '特別純米酒', '純米酒',
        '吟醸', '吟醸酒', '本醸造', '本醸造酒', '特別本醸造', '特別本醸造酒',
        '普通酒', 'リキュール', '本格焼酎', '泡盛', 'スパークリング', 'にごり酒',
        'しぼりたて', 'ひやおろし', '生酒', '原酒', '生原酒', '無濾過生原酒',
        '大吟醸酒', '純米大吟醸酒', '純米吟醸酒', 'クラフトサケ', 'どぶろく'
    )
    OR spec_name LIKE '%完売%'
    OR spec_name LIKE '%(0件)%'
    OR spec_name LIKE '%(純米%'
    OR spec_name LIKE '%(大吟醸%'
    OR spec_name LIKE '%大吟醸・吟醸%'
""")

deleted = cur.rowcount
print(f"🧹 単体カテゴリ・無効テキスト除外数: {deleted} 件")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"🍶 最終クリーン後 登録製品総数: {total_prods} 件")

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
