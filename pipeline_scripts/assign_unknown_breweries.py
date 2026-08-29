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
    SELECT p.id, p.brand_name, p.spec_name, b.name as target_brewery, b.prefecture as target_pref
    FROM products p
    JOIN brands br ON br.name = p.brand_name
    JOIN breweries b ON b.id = br.brewery_id
    WHERE p.brewery_name = '不明'
""")
unassigned = cur.fetchall()

merged = 0
assigned = 0

for r in unassigned:
    p_id = r['id']
    spec = r['spec_name']
    target_b = r['target_brewery']
    target_pref = r['target_pref']

    cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name = ?", (spec, target_b))
    dup = cur.fetchone()

    if dup:
        cur.execute("UPDATE awards SET product_id = ? WHERE product_id = ?", (dup['id'], p_id))
        cur.execute("UPDATE user_flavor_ratings SET product_id = ? WHERE product_id = ?", (dup['id'], p_id))
        cur.execute("DELETE FROM products WHERE id = ?", (p_id,))
        merged += 1
    else:
        cur.execute("UPDATE products SET brewery_name = ?, prefecture = ? WHERE id = ?", (target_b, target_pref, p_id))
        assigned += 1

conn.commit()
print(f"✅ 酒蔵名「不明」の処理完了: {assigned} 件を正規酒蔵へ更新、{merged} 件を既存正規レコードへ統合")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.close()

print(f"🍶 最終製品総数: {total_prods} 件")

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
