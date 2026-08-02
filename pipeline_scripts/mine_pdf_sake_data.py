import os
import sqlite3
import re
import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
MAPS_DIR = os.path.join(BASE_DIR, "maps")

PREFECTURES = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
    '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
    '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
    '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

print(f"Connecting to DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ensure prefecture column exists
cursor.execute("PRAGMA table_info(products)")
cols = [c[1] for c in cursor.fetchall()]
if 'prefecture' not in cols:
    print("Adding 'prefecture' column to products table...")
    cursor.execute("ALTER TABLE products ADD COLUMN prefecture TEXT")
    conn.commit()

# Get existing products
cursor.execute("SELECT id, brand_name, spec_name, brewery_name, prefecture FROM products")
products = cursor.fetchall()
print(f"Total Products in DB: {len(products)}")

mined_breweries = []
mined_sake_notes = []

# Scan PDF maps
folders = [
    os.path.join(MAPS_DIR, "日本酒銘柄・特長マップ"),
    os.path.join(MAPS_DIR, "酒蔵・アクセス位置マップ")
]

for folder in folders:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith('.pdf'):
            continue
        fpath = os.path.join(folder, fname)
        
        pref_from_name = None
        for p in PREFECTURES:
            if p in fname or p.replace('県','').replace('府','').replace('都','') in fname:
                pref_from_name = p
                break
                
        try:
            reader = pypdf.PdfReader(fpath)
            full_text = ''
            for page in reader.pages:
                full_text += page.extract_text() or ''
                
            lines = [l.strip() for l in full_text.splitlines() if l.strip()]
            for line in lines:
                # Table pattern for corporate/brewery names
                table_match = re.search(r'([一-龥]{2,4}[都道府県府])?\s*\d*\s*([一-龥あ-んア-ンa-zA-Z株式会社有限会社合名合資]+(?:酒造|酒販|醸造|酒造場|酒造店|本店|商店)[一-龥あ-んア-ンa-zA-Z]*)\s*(\d{13})?', line)
                if table_match:
                    pref = table_match.group(1) or pref_from_name
                    b_name = table_match.group(2)
                    corp_id = table_match.group(3)
                    mined_breweries.append({
                        'pref': pref,
                        'brewery_name': b_name,
                        'corp_id': corp_id
                    })
                elif any(w in line for w in ['味わい', '特徴', '香り', '甘口', '辛口', 'ペアリング']):
                    mined_sake_notes.append({
                        'pref': pref_from_name,
                        'note': line
                    })
        except Exception:
            pass

print(f"Mined Breweries Count: {len(mined_breweries)}")

# DB Updates & Refinements
updated_brewery_count = 0
updated_pref_count = 0

for item in mined_breweries:
    b_name = item['brewery_name']
    pref = item['pref']
    
    if not b_name:
        continue
        
    core_b_name = re.sub(r'^(株式会社|有限会社|合名会社|合資会社|合同会社)', '', b_name)
    core_b_name = re.sub(r'(株式会社|有限会社|合名会社|合資会社|合同会社)$', '', core_b_name)
    
    if len(core_b_name) < 2:
        continue
        
    if pref:
        cursor.execute("UPDATE products SET prefecture = ? WHERE (brewery_name LIKE ? OR brand_name LIKE ?) AND (prefecture IS NULL OR prefecture = '')", (pref, f"%{core_b_name}%", f"%{core_b_name}%"))
        updated_pref_count += cursor.rowcount
        
    cursor.execute("UPDATE products SET brewery_name = ? WHERE (brewery_name IS NULL OR brewery_name = '' OR brewery_name = '不明') AND brand_name LIKE ?", (b_name, f"%{core_b_name}%"))
    updated_brewery_count += cursor.rowcount

conn.commit()

print(f"\n==========================================")
print(f"🎉 DB銘柄情報ブラッシュアップ完了レポート")
print(f"==========================================")
print(f" 🏭 酒蔵名の補正・補填件数: {updated_brewery_count} 件")
print(f" 🗾 都道府県情報の補正件数: {updated_pref_count} 件")
print(f" 📄 マイニングした公式酒蔵リスト: {len(mined_breweries)} 件")
print(f"==========================================")

conn.close()
