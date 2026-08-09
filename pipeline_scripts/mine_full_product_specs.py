import os
import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 🍾 Mining & Enriching All 7,513 Product Specs ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get all products
cur.execute("SELECT * FROM products")
products = [dict(r) for r in cur.fetchall()]
print(f"Loaded {len(products)} products from database.")

# Build awards map by brand/entry_name for extra spec extraction
cur.execute("SELECT entry_name, category, prize, brand_id, product_id FROM awards WHERE entry_name IS NOT NULL")
awards_rows = cur.fetchall()

awards_spec_map = {}
for a in awards_rows:
    ename = a['entry_name']
    if ename:
        awards_spec_map[ename.strip()] = dict(a)

updated_count = 0
category_enriched = 0
rice_enriched = 0
polish_enriched = 0
heating_enriched = 0

for p in products:
    pid = p['id']
    brand = p['brand_name'] or ''
    spec = p['spec_name'] or ''
    brewery = p['brewery_name'] or ''
    
    full_text = f"{brand} {spec}".strip()
    
    cur_cat = p['category'] or ''
    cur_rice = p['rice_variety'] or ''
    cur_polish = p['polish_ratio'] or ''
    cur_heating = p['heating_type'] or ''
    cur_genshu = p['is_genshu']
    cur_method = p['brewing_method'] or ''
    
    new_cat = cur_cat
    new_rice = cur_rice
    new_polish = cur_polish
    new_heating = cur_heating
    new_genshu = cur_genshu
    new_method = cur_method
    
    # 1. Mine Category (特定名称)
    if not new_cat:
        if '純米大吟醸' in full_text: new_cat = '純米大吟醸酒'
        elif '大吟醸' in full_text: new_cat = '大吟醸酒'
        elif '純米吟醸' in full_text: new_cat = '純米吟醸酒'
        elif '吟醸' in full_text: new_cat = '吟醸酒'
        elif '特別純米' in full_text: new_cat = '特別純米酒'
        elif '純米' in full_text: new_cat = '純米酒'
        elif '特別本醸造' in full_text: new_cat = '特別本醸造酒'
        elif '本醸造' in full_text: new_cat = '本醸造酒'
        elif '普通酒' in full_text or '清酒' in full_text: new_cat = '普通酒'
        elif 'スパークリング' in full_text or '発泡' in full_text: new_cat = 'スパークリング日本酒'
        elif 'リキュール' in full_text or '梅酒' in full_text: new_cat = 'リキュール'

    # 2. Mine Rice Variety (原料米)
    if not new_rice:
        if '山田錦' in full_text: new_rice = '山田錦'
        elif '雄町' in full_text: new_rice = '雄町'
        elif '五百万石' in full_text: new_rice = '五百万石'
        elif '美山錦' in full_text: new_rice = '美山錦'
        elif '出羽燦々' in full_text or '出羽さんさん' in full_text: new_rice = '出羽燦々'
        elif '八反錦' in full_text: new_rice = '八反錦'
        elif '亀の尾' in full_text: new_rice = '亀の尾'
        elif '愛山' in full_text: new_rice = '愛山'
        elif '越淡麗' in full_text: new_rice = '越淡麗'
        elif '秋田酒小町' in full_text: new_rice = '秋田酒小町'
        elif '華吹雪' in full_text: new_rice = '華吹雪'
        elif '夢の香' in full_text: new_rice = '夢の香'

    # 3. Mine Polish Ratio (精米歩合)
    if not new_polish:
        m = re.search(r'(\d{2})%', full_text)
        if m:
            new_polish = f"{m.group(1)}%"
        elif '二割三分' in full_text or '23' in full_text: new_polish = '23%'
        elif '三割九分' in full_text or '39' in full_text: new_polish = '39%'
        elif '四割五分' in full_text or '45' in full_text: new_polish = '45%'
        elif '50' in full_text or '半がえし' in full_text: new_polish = '50%'
        elif '60' in full_text: new_polish = '60%'
        elif '65' in full_text: new_polish = '65%'
        elif '70' in full_text: new_polish = '70%'

    # 4. Mine Heating Type & Genshu & Brewing Method
    if not new_heating:
        if '生々' in full_text or '本生' in full_text or '無濾過生' in full_text or '朝しぼり' in full_text:
            new_heating = '生酒'
        elif '生貯蔵' in full_text:
            new_heating = '生貯蔵酒'
        elif '生詰め' in full_text or '生詰' in full_text:
            new_heating = '生詰酒'

    if new_genshu is None or new_genshu == 0:
        if '原酒' in full_text or '無加水' in full_text:
            new_genshu = 1

    if not new_method:
        if '山廃' in full_text: new_method = '山廃仕込み'
        elif '生酛' in full_text or '生モト' in full_text: new_method = '生酛仕込み'

    # Track updates
    is_updated = False
    if new_cat != cur_cat:
        category_enriched += 1
        is_updated = True
    if new_rice != cur_rice:
        rice_enriched += 1
        is_updated = True
    if new_polish != cur_polish:
        polish_enriched += 1
        is_updated = True
    if new_heating != cur_heating:
        heating_enriched += 1
        is_updated = True

    if is_updated or new_genshu != cur_genshu or new_method != cur_method:
        updated_count += 1
        cur.execute("""
            UPDATE products
            SET category = ?,
                rice_variety = ?,
                polish_ratio = ?,
                heating_type = ?,
                is_genshu = ?,
                brewing_method = ?
            WHERE id = ?
        """, (new_cat, new_rice, new_polish, new_heating, new_genshu, new_method, pid))

conn.commit()

print(f"\n==========================================")
print(f"✨ 銘柄スペック一括マイニング ＆ 補完完了:")
print(f" - 更新された製品総数    : {updated_count} 件")
print(f" - 特定名称（カテゴリー）: +{category_enriched} 件補完")
print(f" - 使用原料米            : +{rice_enriched} 件補完")
print(f" - 精米歩合 (%)          : +{polish_enriched} 件補完")
print(f" - 火入れ区分            : +{heating_enriched} 件補完")
print("==========================================")

# Current database stats summary
cur.execute("SELECT category, COUNT(*) FROM products WHERE category IS NOT NULL AND category != '' GROUP BY category ORDER BY COUNT(*) DESC")
print("\n--- 🍶 最新の特定名称 (category) 内訳 ---")
for r in cur.fetchall():
    print(f" - {r[0]}: {r[1]} 件")

conn.close()
