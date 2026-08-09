import os
import sqlite3
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 🍶 Batch Sake Specification Enrichment Script ===")
print(f"DB Path: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM products")
products = cur.fetchall()

updated_count = 0

for p in products:
    pid = p['id']
    brand = p['brand_name'] or ''
    spec = p['spec_name'] or ''
    cat = p['category'] or ''
    polish = p['polish_ratio'] or ''
    rice = p['rice_variety'] or ''
    alc = p['alcohol']
    smv = p['smv'] or ''
    acidity = p['acidity'] or ''
    ingredients = p['ingredients'] or ''
    ssi = p['ssi_type'] or ''
    
    text = f"{brand} {spec} {cat}"
    
    new_cat = cat
    new_polish = polish
    new_rice = rice
    new_alc = alc
    new_smv = smv
    new_acidity = acidity
    new_ingredients = ingredients
    new_ssi = ssi

    # 1. Category Inference
    if not new_cat or new_cat.strip() == '' or new_cat == '特定名称不明':
        if '純米大吟醸' in text: new_cat = '純米大吟醸酒'
        elif '大吟醸' in text: new_cat = '大吟醸酒'
        elif '純米吟醸' in text: new_cat = '純米吟醸酒'
        elif '吟醸' in text: new_cat = '吟醸酒'
        elif '特別純米' in text: new_cat = '特別純米酒'
        elif '純米' in text: new_cat = '純米酒'
        elif '特別本醸造' in text: new_cat = '特別本醸造酒'
        elif '本醸造' in text: new_cat = '本醸造酒'
        elif '普通酒' in text or '清酒' in text: new_cat = '普通酒'

    # 2. Rice Variety Inference
    if not new_rice or new_rice.strip() in ['', '不明']:
        if '山田錦' in text: new_rice = '山田錦'
        elif '雄町' in text: new_rice = '雄町'
        elif '五百万石' in text: new_rice = '五百万石'
        elif '美山錦' in text: new_rice = '美山錦'
        elif '出羽燦々' in text or '出羽さんさん' in text: new_rice = '出羽燦々'
        elif '八反錦' in text: new_rice = '八反錦'
        elif '亀の尾' in text: new_rice = '亀の尾'
        elif '愛山' in text: new_rice = '愛山'
        elif '越淡麗' in text: new_rice = '越淡麗'
        elif '秋田酒小町' in text: new_rice = '秋田酒小町'
        elif '夢の香' in text: new_rice = '夢の香'
        elif '華吹雪' in text: new_rice = '華吹雪'
        elif '吟風' in text: new_rice = '吟風'

    # 3. Polish Ratio Inference
    if not new_polish or new_polish.strip() in ['', '不明']:
        m = re.search(r'(\d{2})%', text)
        if m:
            new_polish = f"{m.group(1)}%"
        elif '二割三分' in text or '23' in text: new_polish = '23%'
        elif '三割九分' in text or '39' in text: new_polish = '39%'
        elif '四割五分' in text or '45' in text: new_polish = '45%'
        elif '純米大吟醸' in text or '大吟醸' in text: new_polish = '50%'
        elif '純米吟醸' in text or '吟醸' in text: new_polish = '55%'
        elif '特別純米' in text or '特別本醸造' in text: new_polish = '60%'

    # 4. Alcohol Content Inference
    if new_alc is None or new_alc == '':
        m = re.search(r'(\d{2}(?:\.\d)?)度', text)
        if m:
            try: new_alc = float(m.group(1))
            except: pass
        elif '原酒' in text:
            new_alc = 17.0
        elif 'スパークリング' in text or '低アル' in text:
            new_alc = 12.0
        else:
            new_alc = 15.0

    # 5. Ingredients Default Fill
    if not new_ingredients or new_ingredients.strip() in ['', '不明']:
        if '純米' in (new_cat or '') or '純米' in text:
            new_ingredients = '米（国産）、米麹（国産米）'
        else:
            new_ingredients = '米（国産）、米麹（国産米）、醸造アルコール'

    # 6. SSI Type Inference
    if not new_ssi or new_ssi.strip() in ['', '-']:
        if '大吟醸' in text or '吟醸' in text or 'フルーティ' in text:
            new_ssi = '薫酒'
        elif '生酒' in text or '本醸造' in text or 'すっきり' in text or '爽' in text:
            new_ssi = '爽酒'
        elif '熟成' in text or '古酒' in text or '山廃' in text or '生酛' in text:
            new_ssi = '熟酒'
        else:
            new_ssi = '醇酒'

    # 7. SMV / Acidity Defaults if non-existent
    if not new_smv or new_smv.strip() == '':
        new_smv = '非公開'
    if not new_acidity or new_acidity.strip() == '':
        new_acidity = '非公開'

    # Apply updates
    if (new_cat != cat or new_polish != polish or new_rice != rice or 
        new_alc != alc or new_smv != smv or new_acidity != acidity or 
        new_ingredients != ingredients or new_ssi != ssi):
        
        cur.execute("""
            UPDATE products SET
                category = ?,
                polish_ratio = ?,
                rice_variety = ?,
                alcohol = ?,
                smv = ?,
                acidity = ?,
                ingredients = ?,
                ssi_type = ?
            WHERE id = ?
        """, (new_cat, new_polish, new_rice, new_alc, new_smv, new_acidity, new_ingredients, new_ssi, pid))
        updated_count += 1

conn.commit()
print(f"✨ Successfully enriched details for {updated_count} products!")
conn.close()
