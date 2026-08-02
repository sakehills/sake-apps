import os
import sys
import sqlite3
import json
import re
import time
from datetime import datetime

# Set stdout encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from import_sakelia_data import main as run_sakelia_import
from server import search_web_snippets, extract_specs_with_gemini

DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database", os.path.join("..", "database", "sake_database.db"))

def parse_numeric(val):
    if not val or str(val).strip() in ["非公開", "不明", "None"]:
        return None
    matches = re.findall(r'[-+]?\d+(?:\.\d+)?', str(val))
    if not matches:
        return None
    floats = [float(m) for m in matches]
    return sum(floats) / len(floats)

def run_step1_db_sync():
    print("\n==========================================")
    print("STEP 1: Importing & Syncing Sakelia DB")
    print("==========================================")
    run_sakelia_import()

def run_step2_cleansing():
    print("\n==========================================")
    print("STEP 2: Data Cleansing & Normalization")
    print("==========================================")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT id, category, alcohol, polish_ratio, smv, acidity, amino_acidity FROM products")
    rows = cur.fetchall()
    
    updated = 0
    for r in rows:
        pid = r['id']
        category = r['category']
        
        # Category normalization
        new_cat = category
        if category:
            if "純米大吟醸" in category:
                new_cat = "純米大吟醸"
            elif "大吟醸" in category:
                new_cat = "大吟醸"
            elif "純米吟醸" in category:
                new_cat = "純米吟醸"
            elif "吟醸" in category:
                new_cat = "吟醸"
            elif "特別純米" in category:
                new_cat = "特別純米"
            elif "純米" in category:
                new_cat = "純米"
            elif "特別本醸造" in category:
                new_cat = "特別本醸造"
            elif "本醸造" in category:
                new_cat = "本醸造"
            elif "普通酒" in category:
                new_cat = "普通酒"
        
        # Polish ratio normalization
        polish = r['polish_ratio']
        if polish and polish not in ["非公開", "不明"]:
            p_val = parse_numeric(polish)
            new_polish = f"{int(p_val)}%" if p_val else polish
        else:
            new_polish = polish
            
        cur.execute("""
            UPDATE products SET
                category = ?,
                polish_ratio = ?
            WHERE id = ?
        """, (new_cat, new_polish, pid))
        updated += 1
        
    conn.commit()
    conn.close()
    print(f"Cleansing completed. {updated} records normalized.")

def run_step3_image_placeholders():
    print("\n==========================================")
    print("STEP 3: Assigning Default Image Assets")
    print("==========================================")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Assign category-based placeholder images if front image is NULL
    cur.execute("SELECT id, category FROM products WHERE cropped_image_path_front IS NULL OR cropped_image_path_front = '' OR cropped_image_path_front = '0'")
    rows = cur.fetchall()
    
    assigned = 0
    for pid, cat in rows:
        img = "cropped_images/placeholder_noimage.jpg"
        if cat and ("大吟醸" in cat):
            img = "cropped_images/placeholder_daiginjo.jpg"
        elif cat and ("リキュール" in cat or "果汁" in cat):
            img = "cropped_images/placeholder_liqueur.jpg"
        elif cat and ("にごr" in cat or "濁り" in cat or "にごり" in cat):
            img = "cropped_images/placeholder_nigori.jpg"
            
        cur.execute("UPDATE products SET cropped_image_path_front = ? WHERE id = ?", (img, pid))
        assigned += 1
        
    conn.commit()
    conn.close()
    print(f"Image placeholder assignment completed. {assigned} records updated.")

def run_step4_batch_ai_spec_mining(max_items=50, delay=1.5):
    print("\n==========================================")
    print("STEP 4: AI & Web Search Spec Mining")
    print("==========================================")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Find targets missing heating_type or alcohol or polish_ratio
    cur.execute("""
        SELECT id, brand_name, spec_name, brewery_name 
        FROM products 
        WHERE (heating_type IS NULL OR alcohol IS NULL OR alcohol = 0.0 OR polish_ratio IS NULL OR polish_ratio = '不明')
          AND brewery_name IS NOT NULL AND brewery_name != ''
        LIMIT ?
    """, (max_items,))
    
    targets = cur.fetchall()
    print(f"Found {len(targets)} candidate records for AI spec mining (limit: {max_items}).")
    
    extracted_count = 0
    for idx, r in enumerate(targets):
        pid = r['id']
        brand = r['brand_name']
        spec = r['spec_name'] or ''
        brewery = r['brewery_name']
        
        full_name = f"{brand} {spec}".strip()
        query = f"{brewery} {full_name} 特定名称 アルコール度数 精米歩合 火入れ 原酒 温度帯"
        print(f"[{idx+1}/{len(targets)}] Processing ID {pid}: {full_name} ({brewery})")
        
        try:
            snippets = search_web_snippets(query)
            if snippets:
                extracted = extract_specs_with_gemini(brand, brewery, snippets)
                if extracted and any(v is not None for v in extracted.values()):
                    cur.execute("""
                        UPDATE products SET
                            category = COALESCE(?, category),
                            alcohol = COALESCE(?, alcohol),
                            polish_ratio = COALESCE(?, polish_ratio),
                            ingredients = COALESCE(?, ingredients),
                            rice_variety = COALESCE(?, rice_variety),
                            yeast = COALESCE(?, yeast),
                            smv = COALESCE(?, smv),
                            acidity = COALESCE(?, acidity),
                            amino_acidity = COALESCE(?, amino_acidity),
                            heating_type = COALESCE(?, heating_type),
                            is_genshu = COALESCE(?, is_genshu),
                            brewing_method = COALESCE(?, brewing_method),
                            serving_temperature = COALESCE(?, serving_temperature)
                        WHERE id = ?
                    """, (
                        extracted.get('category'),
                        extracted.get('alcohol'),
                        extracted.get('polish_ratio'),
                        extracted.get('ingredients'),
                        extracted.get('rice_variety'),
                        extracted.get('yeast'),
                        str(extracted.get('smv')) if extracted.get('smv') is not None else None,
                        str(extracted.get('acidity')) if extracted.get('acidity') is not None else None,
                        str(extracted.get('amino_acidity')) if extracted.get('amino_acidity') is not None else None,
                        extracted.get('heating_type'),
                        extracted.get('is_genshu'),
                        extracted.get('brewing_method'),
                        extracted.get('serving_temperature'),
                        pid
                    ))
                    conn.commit()
                    extracted_count += 1
                    print(f"  --> Updated specs for ID {pid}")
        except Exception as e:
            print(f"  [Warning] Failed to mine specs for ID {pid}: {e}")
            
        time.sleep(delay)
        
    conn.close()
    print(f"AI Spec Mining step completed. {extracted_count}/{len(targets)} records enriched.")

def run_step1_5_award_registration_and_deduplication():
    print("\n==========================================")
    print("STEP 1.5: Award Products Sync & Deduplication")
    print("==========================================")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 1. Register missing award entry names into products table
    cur.execute("""
        SELECT DISTINCT a.entry_name, a.brand_id, a.brewery_id
        FROM awards a
        WHERE a.entry_name NOT IN (SELECT brand_name FROM products WHERE brand_name IS NOT NULL)
          AND a.entry_name NOT IN (SELECT spec_name FROM products WHERE spec_name IS NOT NULL)
    """)
    missing_awards = cur.fetchall()
    
    if missing_awards:
        brewery_map = {}
        cur.execute("SELECT id, name FROM breweries")
        for b in cur.fetchall():
            brewery_map[b['id']] = b['name']

        brand_map = {}
        cur.execute("SELECT id, brand_name, brewery_name FROM products")
        for p in cur.fetchall():
            if p['brand_name']:
                brand_map[p['brand_name']] = p['brewery_name']

        now = datetime.now().isoformat()
        inserted = 0

        for ma in missing_awards:
            entry = ma['entry_name'].strip()
            if not entry:
                continue
                
            brewery_name = brewery_map.get(ma['brewery_id'])
            if not brewery_name:
                for bname, b_brewery in brand_map.items():
                    if len(bname) >= 2 and entry.startswith(bname):
                        brewery_name = b_brewery
                        break
                        
            parts = entry.split(' ', 1)
            brand_name = parts[0] if len(parts) > 1 else entry
            
            cur.execute("""
                INSERT INTO products (
                    spec_name, brand_name, brewery_name, category, status, confidence, source_id, evidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry, brand_name, brewery_name or '不明', '日本酒', 'draft', 1.0, 'award_import', 'Imported from Competition Awards', now
            ))
            inserted += 1
        conn.commit()
        print(f"Award sync: Registered {inserted} new award-winning products.")

    # 2. Deduplication check
    cur.execute("""
        SELECT brewery_name, spec_name, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
        FROM products
        WHERE spec_name IS NOT NULL AND spec_name != ''
        GROUP BY brewery_name, spec_name
        HAVING cnt > 1
    """)
    dupes_spec = cur.fetchall()
    deleted_count = 0

    for group in dupes_spec:
        ids = [int(x) for x in group['ids'].split(',')]
        cur.execute(f"SELECT * FROM products WHERE id IN ({','.join(map(str, ids))})")
        rows = [dict(r) for r in cur.fetchall()]
        
        def score_row(r):
            score = 0
            img = r.get('cropped_image_path_front') or ''
            if img and 'placeholder' not in img:
                score += 100
            if r.get('alcohol') and r.get('alcohol') > 0:
                score += 10
            if r.get('polish_ratio') and r.get('polish_ratio') != '不明':
                score += 10
            if r.get('source_id') != 'award_import':
                score += 5
            return score
            
        rows.sort(key=score_row, reverse=True)
        delete_ids = [r['id'] for r in rows[1:]]
        cur.execute(f"DELETE FROM products WHERE id IN ({','.join(map(str, delete_ids))})")
        deleted_count += len(delete_ids)

    # 3. Create Unique Index
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_brewery_spec ON products(brewery_name, spec_name)")
    conn.commit()
    conn.close()
    print(f"Deduplication & Unique Index check completed. {deleted_count} duplicates removed.")

def main():
    print("==================================================")
    print("STARTING FULL SAKE DATA ENRICHMENT PIPELINE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================")
    
    # 1. External DB Sync
    run_step1_db_sync()

    # 1.5 Award Sync & Deduplication
    run_step1_5_award_registration_and_deduplication()
    
    # 2. Cleansing & Normalization
    run_step2_cleansing()
    
    # 3. Image Placeholders
    run_step3_image_placeholders()
    
    # 4. AI Spec Mining (Default batch of 20 for quick validation / initial run)
    max_mining_count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    run_step4_batch_ai_spec_mining(max_items=max_mining_count)
    
    print("\n==================================================")
    print("FULL PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()
