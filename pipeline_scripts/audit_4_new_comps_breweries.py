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

# 今回の4大コンペ（SAKE COMPETITION, フェミナリーズ, OSA, ロンドン）の全対象酒蔵
cur.execute("""
    SELECT DISTINCT b.id, b.name, b.prefecture, b.website
    FROM breweries b
    JOIN awards a ON a.brewery_id = b.id
    WHERE a.competition_id IN (10037, 10044, 10045, 10046, 10047)
    ORDER BY b.id
""")
new_comp_breweries = cur.fetchall()

print(f"=== 🏆 新規4大コンペ 受賞酒蔵の全数監査 (対象: {len(new_comp_breweries)} 蔵) ===")

missing_websites = []
brewery_product_counts = []

for b in new_comp_breweries:
    bid = b['id']
    bname = b['name']
    burl = b['website']
    clean_name = bname.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").strip()

    if not burl or not burl.startswith("http"):
        missing_websites.append((bid, bname))

    cur.execute("""
        SELECT COUNT(*) FROM products
        WHERE brewery_name LIKE ? OR brewery_name LIKE ?
    """, (f"%{bname}%", f"%{clean_name}%"))
    cnt = cur.fetchone()[0]
    brewery_product_counts.append((bid, bname, b['prefecture'], cnt, burl))

print(f"・公式サイトURL 未設定の蔵: {len(missing_websites)} 件")
if missing_websites:
    for mw in missing_websites:
        print(f"  ⚠️ URL未設定: ID {mw[0]} - {mw[1]}")

print(f"\n【各酒蔵の登録製品数一覧】")
for r in sorted(brewery_product_counts, key=lambda x: x[3], reverse=True):
    print(f"・ID {r[0]:5d}: {r[1]} ({r[2]}) -> {r[3]} 件 [公式: {r[4]}]")

conn.close()
