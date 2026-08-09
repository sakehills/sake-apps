import os
import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
SAKELIA_DB = os.path.join(ROOT_DIR, "Claudeから移行", "sakelia-pipeline", "db", "sakelia.db")

print(f"=== 🍾 Executing Product Spec Mining & Automatic Enrichment ===")
print(f"DB Path: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check missing specs count
cur.execute("SELECT COUNT(*) FROM products WHERE (smv IS NULL OR smv = '') AND (acidity IS NULL OR acidity = '')")
missing_count = cur.fetchone()[0]
print(f"Products missing SMV/acidity specs: {missing_count} out of 7,513")

# Auto-infer specs based on product names / category / spec_name keywords
cur.execute("SELECT id, brand_name, spec_name, category, polish_ratio, rice_variety, alcohol, smv, acidity FROM products")
products = cur.fetchall()

updated_count = 0

for p in products:
    pid, brand, spec, cat, polish, rice, alc, smv, acidity = p
    
    new_polish = polish
    new_rice = rice
    new_cat = cat
    
    text = f"{brand or ''} {spec or ''}"
    
    # 1. Infer category if missing
    if not new_cat or new_cat.strip() == '':
        if '純米大吟醸' in text: new_cat = '純米大吟醸酒'
        elif '大吟醸' in text: new_cat = '大吟醸酒'
        elif '純米吟醸' in text: new_cat = '純米吟醸酒'
        elif '吟醸' in text: new_cat = '吟醸酒'
        elif '特別純米' in text: new_cat = '特別純米酒'
        elif '純米' in text: new_cat = '純米酒'
        elif '特別本醸造' in text: new_cat = '特別本醸造酒'
        elif '本醸造' in text: new_cat = '本醸造酒'
        elif '普通酒' in text or '清酒' in text: new_cat = '普通酒'

    # 2. Infer Rice Variety if missing
    if not new_rice or new_rice.strip() == '':
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

    # 3. Infer Polish Ratio if missing (e.g. 磨き二割三分 -> 23%, 50%, 60%)
    if not new_polish or new_polish.strip() == '':
        m = re.search(r'(\d{2})%', text)
        if m:
            new_polish = f"{m.group(1)}%"
        elif '二割三分' in text or '23' in text: new_polish = '23%'
        elif '三割九分' in text or '39' in text: new_polish = '39%'
        elif '四割五分' in text or '45' in text: new_polish = '45%'
        elif '50' in text or '半がえし' in text: new_polish = '50%'
        elif '60' in text: new_polish = '60%'

    if new_cat != cat or new_rice != rice or new_polish != polish:
        cur.execute("""
            UPDATE products
            SET category = COALESCE(?, category),
                rice_variety = COALESCE(?, rice_variety),
                polish_ratio = COALESCE(?, polish_ratio)
            WHERE id = ?
        """, (new_cat, new_rice, new_polish, pid))
        updated_count += 1

conn.commit()
print(f" ✅ Enriched and updated specs for {updated_count} products!")

conn.close()
