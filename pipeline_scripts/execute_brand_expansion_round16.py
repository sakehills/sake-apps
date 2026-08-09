import os
import sqlite3
import sys
import importlib.util

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
SAKELIA_DB = os.path.join(ROOT_DIR, "Claudeから移行", "sakelia-pipeline", "db", "sakelia.db")
ARCHIVE_DIR = os.path.join(ROOT_DIR, "Claudeから移行", "sakelia-pipeline", "data", "staged", "archive")

# 1. Dynamically import norm_name from 03_normalize.py per handoff rules
NORM_PATH = os.path.join(ROOT_DIR, "Claudeから移行", "sakelia-pipeline", "pipeline", "03_normalize.py")
if os.path.exists(NORM_PATH):
    spec = importlib.util.spec_from_file_location("normalize03", NORM_PATH)
    normalize03 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normalize03)
    norm_name = normalize03.norm_name
    print(" Successfully imported norm_name() from pipeline/03_normalize.py!")
else:
    import re
    def norm_name(name):
        return re.sub(r'\s+', '', name).strip().lower()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get existing brand_norms for deduplication
cur.execute("SELECT brewery_id, name FROM brands WHERE status != 'rejected'")
existing_brands = set()
for row in cur.fetchall():
    b_id, b_name = row
    if b_name:
        existing_brands.add((b_id, norm_name(b_name)))

print(f"Loaded {len(existing_brands)} existing brand-brewery pairs for deduplication.")

# Find brands in products table that are not yet in brands table
cur.execute("""
    SELECT DISTINCT p.brewery_name, p.brand_name
    FROM products p
    WHERE p.brand_name IS NOT NULL AND p.brand_name != ''
""")
product_brands = cur.fetchall()

# Map brewery_name to brewery_id
cur.execute("SELECT id, name, name_norm, kura_name FROM breweries WHERE status != 'rejected'")
brewery_rows = cur.fetchall()
brewery_map = {}
for b in brewery_rows:
    b_id, name, name_norm, kura_name = b
    if name: brewery_map[norm_name(name)] = b_id
    if kura_name: brewery_map[norm_name(kura_name)] = b_id

new_brand_records = []
added_pairs = set()

for b_name_raw, brand_raw in product_brands:
    if not b_name_raw or not brand_raw: continue
    bn_norm = norm_name(b_name_raw)
    brand_norm = norm_name(brand_raw)
    
    b_id = brewery_map.get(bn_norm)
    if not b_id:
        # Partial match
        for k, vid in brewery_map.items():
            if k in bn_norm or bn_norm in k:
                b_id = vid
                break
                
    if b_id:
        pair = (b_id, brand_norm)
        if pair not in existing_brands and pair not in added_pairs:
            added_pairs.add(pair)
            new_brand_records.append((b_id, brand_raw.strip(), 'active', 1.0, 'product_mining', 'extracted_from_products'))

print(f"\n🔍 Found {len(new_brand_records)} new brand entries to insert into brands table!")

if new_brand_records:
    cur.executemany("""
        INSERT OR IGNORE INTO brands (brewery_id, name, status, confidence, source_id, evidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, new_brand_records)
    conn.commit()
    print(f" ✅ Inserted {len(new_brand_records)} new brands into database/sake_database.db!")

    # Also sync into sakelia.db
    if os.path.exists(SAKELIA_DB):
        conn_sak = sqlite3.connect(SAKELIA_DB)
        cur_sak = conn_sak.cursor()
        cur_sak.executemany("""
            INSERT OR IGNORE INTO brands (brewery_id, name, status, confidence, source_id, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, new_brand_records)
        conn_sak.commit()
        conn_sak.close()
        print(f" ✅ Synchronized new brands into sakelia.db!")

# Display current total counts
cur.execute("SELECT COUNT(*) FROM brands WHERE status != 'rejected'")
total_brands = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM breweries WHERE status != 'rejected'")
total_breweries = cur.fetchone()[0]

print("\n==========================================")
print(f"📊 最新DBステータス:")
print(f" - 総酒蔵数 (breweries): {total_breweries} 件")
print(f" - 総銘柄数 (brands)   : {total_brands} 件")
print("==========================================")

conn.close()
