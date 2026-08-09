import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🧹 戦略 3: 名寄せAI ＆ データ品質クレンジング パイプライン開始 ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def normalize_text(text):
    if not text: return ""
    t = str(text).strip()
    # Fullwidth alphanumeric to halfwidth
    t = t.translate(str.maketrans(
        '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ',
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    ))
    # Replace fullwidth space
    t = t.replace('　', ' ')
    # Remove extra spaces
    t = re.sub(r'\s+', ' ', t)
    return t

# 1. Brewery Data Cleaning
cur.execute("SELECT id, name, prefecture, address, corporate_no FROM breweries")
breweries = cur.fetchall()

b_updated = 0
for b in breweries:
    bid = b['id']
    old_name = b['name']
    old_pref = b['prefecture']
    old_addr = b['address']
    
    new_name = normalize_text(old_name)
    # Fix company name variations
    new_name = new_name.replace('(株)', '株式会社').replace('(有)', '有限会社').replace('(名)', '合名会社').replace('(資)', '合資会社')
    new_name = new_name.replace('（株）', '株式会社').replace('（有）', '有限会社').replace('（名）', '合名会社').replace('（資）', '合資会社')
    
    new_pref = normalize_text(old_pref)
    new_addr = normalize_text(old_addr)
    
    if new_name != old_name or new_pref != old_pref or new_addr != old_addr:
        cur.execute("UPDATE breweries SET name = ?, prefecture = ?, address = ? WHERE id = ?", (new_name, new_pref, new_addr, bid))
        b_updated += 1

conn.commit()
print(f"✅ 酒蔵マスタ (breweries) クレンジング完了: {b_updated} 件クレンジング実施")

# 2. Brands Data Cleaning & Deduplication
cur.execute("SELECT id, name, brewery_id FROM brands")
brands = cur.fetchall()

br_updated = 0
seen_brands = set()
duplicates_found = 0

for br in brands:
    brid = br['id']
    old_bname = br['name']
    brew_id = br['brewery_id']
    
    new_bname = normalize_text(old_bname)
    
    key = (new_bname.lower(), brew_id)
    if key in seen_brands:
        duplicates_found += 1
    else:
        seen_brands.add(key)
        
    if new_bname != old_bname:
        cur.execute("UPDATE brands SET name = ? WHERE id = ?", (new_bname, brid))
        br_updated += 1

conn.commit()
print(f"✅ 銘柄マスタ (brands) クレンジング完了: {br_updated} 件クレンジング実施 (重複検出: {duplicates_found} 件)")

# 3. Products Data Cleaning
cur.execute("SELECT id, brand_name, brewery_name, spec_name, category FROM products")
products = cur.fetchall()

p_updated = 0
for p in products:
    pid = p['id']
    old_bn = p['brand_name']
    old_bw = p['brewery_name']
    old_sp = p['spec_name']
    old_cat = p['category']
    
    new_bn = normalize_text(old_bn)
    new_bw = normalize_text(old_bw)
    new_sp = normalize_text(old_sp)
    new_cat = normalize_text(old_cat)
    
    if new_bn != old_bn or new_bw != old_bw or new_sp != old_sp or new_cat != old_cat:
        cur.execute("UPDATE products SET brand_name = ?, brewery_name = ?, spec_name = ?, category = ? WHERE id = ?", (new_bn, new_bw, new_sp, new_cat, pid))
        p_updated += 1

conn.commit()
print(f"✅ 製品スペック (products) クレンジング完了: {p_updated} 件クレンジング実施")

print("==========================================")
print("✨ 戦略 3 名寄せAI ＆ クレンジングパイプライン 完了！")
print("==========================================")

conn.close()
