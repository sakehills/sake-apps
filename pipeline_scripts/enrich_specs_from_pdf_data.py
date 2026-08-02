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

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ensure prefecture column exists
cursor.execute("PRAGMA table_info(products)")
cols = [c[1] for c in cursor.fetchall()]
if 'prefecture' not in cols:
    cursor.execute("ALTER TABLE products ADD COLUMN prefecture TEXT")
    conn.commit()

cursor.execute("SELECT id, brand_name, spec_name, brewery_name, prefecture FROM products")
products = cursor.fetchall()

print(f"Loaded {len(products)} products from DB.")

# Mine PDF Maps
pdf_sake_info = []

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
        
        pref = None
        for p in PREFECTURES:
            if p in fname or p.replace('県','').replace('府','').replace('都','') in fname:
                pref = p
                break
                
        try:
            reader = pypdf.PdfReader(fpath)
            for page in reader.pages[:2]:
                text = page.extract_text() or ''
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                for line in lines:
                    if len(line) > 3 and any(k in line for k in ['酒', '蔵', '吟醸', '純米', '大吟醸', '本醸造']):
                        pdf_sake_info.append((pref, fname, line))
        except Exception:
            pass

print(f"Extracted {len(pdf_sake_info)} raw PDF text entries.")

updated_breweries = 0
updated_prefs = 0

for pref, fname, text_line in pdf_sake_info:
    # Match against brand_name in DB
    for p_id, brand, spec, brewery, existing_pref in products:
        if brand and len(brand) >= 2 and brand in text_line:
            # Update prefecture if missing
            if pref and not existing_pref:
                cursor.execute("UPDATE products SET prefecture = ? WHERE id = ?", (pref, p_id))
                updated_prefs += cursor.rowcount
                
            # Update brewery_name if missing/unknown
            if not brewery or brewery == '不明':
                # Extract potential brewery name from text_line
                b_match = re.search(r'([一-龥あ-んア-ンa-zA-Z]+(?:酒造|醸造|酒造場|酒造店|本店|商店))', text_line)
                if b_match:
                    new_b = b_match.group(1)
                    cursor.execute("UPDATE products SET brewery_name = ? WHERE id = ?", (new_b, p_id))
                    updated_breweries += cursor.rowcount

conn.commit()

print(f"\n==========================================")
print(f"🎉 PDFデータによる銘柄情報補正・ブラッシュアップ結果")
print(f"==========================================")
print(f" 🏭 酒蔵名の新規補填・更新: {updated_breweries} 件")
print(f" 🗾 都道府県情報の新規補填・設定: {updated_prefs} 件")
print(f"==========================================")

conn.close()
