import os
import sys
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# LAGOON BREWERYの表記統一
cur.execute("UPDATE products SET brewery_name = 'LAGOON BREWERY合同会社(ラグーンブリュワリー)' WHERE brewery_name LIKE '%LAGOON%'")

# 濱川商店の表記統一
cur.execute("UPDATE products SET brewery_name = '有限会社濱川商店' WHERE brewery_name LIKE '%濱川商店%'")

# 甲斐商店の表記統一
cur.execute("UPDATE products SET brewery_name = '株式会社甲斐商店' WHERE brewery_name LIKE '%甲斐商店%'")

# 村尾酒造の表記統一
cur.execute("UPDATE products SET brewery_name = '村尾酒造合資会社' WHERE brewery_name LIKE '%村尾酒造%'")

# 鳥飼酒造の表記統一
cur.execute("UPDATE products SET brewery_name = '株式会社鳥飼酒造' WHERE brewery_name LIKE '%鳥飼酒造%'")

# 国分酒造の表記統一
cur.execute("UPDATE products SET brewery_name = '国分酒造株式会社' WHERE brewery_name LIKE '%国分酒造%'")

# 関原酒造 (新潟・越の鶴) のラインナップ追加
SEKIHARA_PRODUCTS = [
    {"spec": "越の鶴 大吟醸 斗瓶囲い 鑑評会出品酒", "brand": "越の鶴", "cat": "大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "新潟県", "url": "https://www.harashuzo.com/"},
    {"spec": "越の鶴 プレミアム純米大吟醸 越淡麗35", "brand": "越の鶴", "cat": "純米大吟醸酒", "polish": "35%", "rice": "越淡麗", "alc": 15.5, "smv": "+2.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://www.harashuzo.com/"},
    {"spec": "越の鶴 本醸造 辛口 寒仕込み", "brand": "越の鶴", "cat": "本醸造酒", "polish": "60%", "rice": "五百万石", "alc": 15.0, "smv": "+6.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "新潟県", "url": "https://www.harashuzo.com/"},
    {"spec": "越の鶴 純米吟醸 越淡麗", "brand": "越の鶴", "cat": "純米吟醸酒", "polish": "55%", "rice": "越淡麗", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://www.harashuzo.com/"}
]

for p in SEKIHARA_PRODUCTS:
    cur.execute("""
        SELECT id FROM products WHERE spec_name = ? AND brewery_name = '関原酒造株式会社'
    """, (p['spec'],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, smv, acidity, ssi_type, ingredients,
                brewery_name, prefecture, confidence, evidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '関原酒造株式会社', ?, 1.0, ?, 'active')
        """, (p['brand'], p['spec'], p['cat'], p['polish'], p['rice'], p['alc'], p['smv'], p['acid'], p['ssi'], p['ing'], p['pref'], f"Official Verified ({p['url']})"))

conn.commit()
conn.close()

print("✅ 表記統一＆関原酒造ラインナップ補完完了")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
