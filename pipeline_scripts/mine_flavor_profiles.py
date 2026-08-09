import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 📊 Mining Flavor Profiles across All Products ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Aggregate user ratings by product_id
cur.execute("""
    SELECT 
        product_id,
        COUNT(*) as cnt,
        AVG(total_score) as avg_total,
        AVG(taste_score) as avg_taste,
        AVG(aroma_score) as avg_aroma,
        ssi_type,
        body_level,
        aroma_level
    FROM user_flavor_ratings
    WHERE product_id IS NOT NULL
    GROUP BY product_id
""")
rating_aggs = cur.fetchall()
print(f"Aggregated user flavor ratings for {len(rating_aggs)} rated products.")

rating_map = {}
for r in rating_aggs:
    pid = r['product_id']
    rating_map[pid] = dict(r)

# 2. Process all products
cur.execute("SELECT id, brand_name, spec_name, category, ssi_type, body_level, aroma_level FROM products")
products = [dict(row) for row in cur.fetchall()]

updated_count = 0
ssi_inferred_count = 0

for p in products:
    pid = p['id']
    brand = p['brand_name'] or ''
    spec = p['spec_name'] or ''
    cat = p['category'] or ''
    full_text = f"{brand} {spec} {cat}"
    
    cur_ssi = p['ssi_type']
    cur_body = p['body_level']
    cur_aroma = p['aroma_level']
    
    new_ssi = cur_ssi
    new_body = cur_body
    new_aroma = cur_aroma
    
    # Priority A: Check user rating aggs
    if pid in rating_map:
        rag = rating_map[pid]
        if rag.get('ssi_type'): new_ssi = rag['ssi_type']
        if rag.get('body_level'): new_body = rag['body_level']
        if rag.get('aroma_level'): new_aroma = rag['aroma_level']

    # Priority B: Infer from Category / Spec text if still missing
    if not new_ssi or new_ssi.strip() == '':
        if any(w in full_text for w in ['純米大吟醸', '大吟醸', '吟醸', 'フルーティー', '華やか', 'スパークリング']):
            new_ssi = '薫酒'
            if not new_aroma: new_aroma = '華やか'
            if not new_body: new_body = '軽快・スッキリ'
            ssi_inferred_count += 1
        elif any(w in full_text for w in ['特別純米', '純米', '山廃', '生酛', '旨口', '無濾過生原酒']):
            new_ssi = '醇酒'
            if not new_aroma: new_aroma = '穏やか'
            if not new_body: new_body = 'しっかり・濃醇'
            ssi_inferred_count += 1
        elif any(w in full_text for w in ['生酒', '本醸造', '普通酒', '淡麗', '辛口', '夏酒']):
            new_ssi = '爽酒'
            if not new_aroma: new_aroma = '軽快'
            if not new_body: new_body = 'スッキリ'
            ssi_inferred_count += 1
        elif any(w in full_text for w in ['古酒', '熟成', '秘蔵酒', '長期']):
            new_ssi = '熟酒'
            if not new_aroma: new_aroma = '熟成香'
            if not new_body: new_body = '極濃醇'
            ssi_inferred_count += 1

    if new_ssi != cur_ssi or new_body != cur_body or new_aroma != cur_aroma:
        cur.execute("""
            UPDATE products
            SET ssi_type = ?,
                body_level = ?,
                aroma_level = ?
            WHERE id = ?
        """, (new_ssi, new_body, new_aroma, pid))
        updated_count += 1

conn.commit()

print(f"\n==========================================")
print(f"✨ フレーバープロファイル統計マイニング完了:")
print(f" - 更新された製品総数       : {updated_count} 件")
print(f" - 推論・補完された SSI タイプ: +{ssi_inferred_count} 件")
print("==========================================")

# Breakdown of SSI Types
cur.execute("SELECT ssi_type, COUNT(*) FROM products WHERE ssi_type IS NOT NULL AND ssi_type != '' GROUP BY ssi_type ORDER BY COUNT(*) DESC")
print("\n--- 🍶 フレーバー (SSI 4分類) 内訳 ---")
for r in cur.fetchall():
    print(f" - {r[0]}: {r[1]} 件")

conn.close()
