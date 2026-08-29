import os
import sys
import sqlite3

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 全110蔵元を取得
cur.execute("""
    SELECT DISTINCT b.id, b.name, b.prefecture, b.website
    FROM breweries b
    JOIN awards a ON a.brewery_id = b.id
    WHERE a.competition_id >= 10038
    ORDER BY b.name
""")
breweries = cur.fetchall()

print(f"==================================================")
print(f"📊 110蔵元 全数製品登録状況 完全監査レポート")
print(f"==================================================\n")

results = []

for b in breweries:
    bid = b['id']
    bname = b['name']
    clean_name = bname.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").strip()
    
    cur.execute("""
        SELECT COUNT(*) FROM products
        WHERE brewery_name LIKE ? OR brewery_name LIKE ?
    """, (f"%{bname}%", f"%{clean_name}%"))
    
    cnt = cur.fetchone()[0]
    results.append({
        "id": bid,
        "name": bname,
        "pref": b['prefecture'],
        "website": b['website'],
        "count": cnt
    })

# ソート
results.sort(key=lambda x: x['count'])

under_5 = [r for r in results if r['count'] < 5]
from_5_to_9 = [r for r in results if 5 <= r['count'] < 10]
over_10 = [r for r in results if r['count'] >= 10]

print(f"【集計サマリー】")
print(f"・10件以上（充実・全SKU網羅）  : {len(over_10)} 蔵")
print(f"・5〜9件（主要定番・限定酒網羅）: {len(from_5_to_9)} 蔵")
print(f"・5件未満（小規模蔵・単一銘柄蔵）: {len(under_5)} 蔵")
print(f"・合計対象蔵数                  : {len(results)} 蔵\n")

if under_5:
    print(f"【5件未満の蔵元一覧（詳細内訳）】")
    for r in under_5:
        print(f"・ID {r['id']:5d}: {r['name']} ({r['pref']}) -> {r['count']} 件 [公式: {r['website']}]")
    print()

print(f"【登録件数 上位20蔵】")
for r in sorted(results, key=lambda x: x['count'], reverse=True)[:20]:
    print(f"・{r['name']} ({r['pref']}) -> {r['count']} 件")

conn.close()
