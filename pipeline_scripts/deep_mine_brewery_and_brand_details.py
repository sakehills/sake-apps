import os
import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 🏛️🍶 Executing Deep Precision Enrichment for Breweries & Brands ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Ensure extra columns exist in breweries and products
cur.execute("PRAGMA table_info(breweries)")
b_cols = [r['name'] for r in cur.fetchall()]

if 'founding_year' not in b_cols:
    cur.execute("ALTER TABLE breweries ADD COLUMN founding_year TEXT")
if 'visitation_allowed' not in b_cols:
    cur.execute("ALTER TABLE breweries ADD COLUMN visitation_allowed INTEGER DEFAULT 0")
if 'shop_available' not in b_cols:
    cur.execute("ALTER TABLE breweries ADD COLUMN shop_available INTEGER DEFAULT 0")

cur.execute("PRAGMA table_info(products)")
p_cols = [r['name'] for r in cur.fetchall()]

if 'yeast' not in p_cols:
    cur.execute("ALTER TABLE products ADD COLUMN yeast TEXT")
if 'water_source' not in p_cols:
    cur.execute("ALTER TABLE products ADD COLUMN water_source TEXT")
if 'serving_temperature' not in p_cols:
    cur.execute("ALTER TABLE products ADD COLUMN serving_temperature TEXT")

conn.commit()

# Famous founding years & details map for major breweries
WELL_KNOWN_BREWERIES_DETAIL = {
    "旭酒造": {"founding": "1948年 (昭和23年)", "shop": 1, "visit": 1, "web": "https://www.dassai.co.jp/"},
    "八海醸造": {"founding": "1922年 (大正11年)", "shop": 1, "visit": 1, "web": "https://www.hakkaisan.co.jp/"},
    "一ノ蔵": {"founding": "1973年 (昭和48年)", "shop": 1, "visit": 1, "web": "https://ichinokura.co.jp/"},
    "菊正宗": {"founding": "1659年 (万治2年)", "shop": 1, "visit": 1, "web": "https://www.kikumasamune.co.jp/"},
    "月桂冠": {"founding": "1637年 (寛永14年)", "shop": 1, "visit": 1, "web": "https://www.gekkeikan.co.jp/"},
    "宝酒造": {"founding": "1842年 (天保13年)", "shop": 1, "visit": 0, "web": "https://www.takarashuzo.co.jp/"},
    "白鶴酒造": {"founding": "1743年 (寛保3年)", "shop": 1, "visit": 1, "web": "https://www.hakutsuru.co.jp/"},
    "黄桜": {"founding": "1925年 (大正14年)", "shop": 1, "visit": 1, "web": "https://kizakura.co.jp/"},
    "大関": {"founding": "1711年 (正徳元年)", "shop": 1, "visit": 1, "web": "https://www.ozeki.co.jp/"},
    "日本盛": {"founding": "1889年 (明治22年)", "shop": 1, "visit": 1, "web": "https://www.nihonsakari.co.jp/"},
    "新政酒造": {"founding": "1852年 (嘉永5年)", "shop": 1, "visit": 0, "web": "http://www.aramasa.jp/"},
    "高木酒造": {"founding": "1615年 (元和元年)", "shop": 0, "visit": 0, "web": ""},
    "西酒造": {"founding": "1845年 (弘化2年)", "shop": 1, "visit": 1, "web": "https://www.nishi-shuzo.co.jp/"},
    "霧島酒造": {"founding": "1916年 (大正5年)", "shop": 1, "visit": 1, "web": "https://www.kirishima.co.jp/"},
    "三和酒類": {"founding": "1958年 (昭和33年)", "shop": 1, "visit": 1, "web": "https://www.iichiko.co.jp/"},
    "黒龍酒造": {"founding": "1804年 (文化元年)", "shop": 1, "visit": 1, "web": "https://www.kokuryu.co.jp/"},
    "加藤吉平商店": {"founding": "1860年 (万延元年)", "shop": 1, "visit": 1, "web": "https://www.born.jp/"},
    "朝日酒造": {"founding": "1830年 (天保元年)", "shop": 1, "visit": 1, "web": "https://www.asahi-shuzo.co.jp/"},
}

# Update breweries details
cur.execute("SELECT id, name, kura_name, website, founding_year FROM breweries WHERE status != 'rejected'")
breweries = cur.fetchall()

b_updated = 0
for b in breweries:
    bid = b['id']
    name = b['name'] or ''
    kura = b['kura_name'] or ''
    web = b['website'] or ''
    founding = b['founding_year'] or ''
    
    new_founding = founding
    new_shop = 0
    new_visit = 0
    new_web = web
    
    for k_key, k_info in WELL_KNOWN_BREWERIES_DETAIL.items():
        if k_key in name or k_key in kura or name in k_key:
            new_founding = k_info['founding']
            new_shop = k_info['shop']
            new_visit = k_info['visit']
            if not new_web and k_info['web']:
                new_web = k_info['web']
            break
            
    if new_founding != founding or new_web != web:
        cur.execute("UPDATE breweries SET founding_year = ?, shop_available = ?, visitation_allowed = ?, website = ? WHERE id = ?",
                    (new_founding, new_shop, new_visit, new_web, bid))
        b_updated += 1

conn.commit()

# Enrich Product Yeast, Water Source, and Serving Temperature
cur.execute("SELECT id, brand_name, spec_name, category, ssi_type, yeast, water_source, serving_temperature FROM products")
products = [dict(r) for r in cur.fetchall()]

p_updated = 0
for p in products:
    pid = p['id']
    brand = p['brand_name'] or ''
    spec = p['spec_name'] or ''
    cat = p['category'] or ''
    ssi = p['ssi_type'] or ''
    text = f"{brand} {spec} {cat} {ssi}"
    
    cur_yeast = p['yeast'] or ''
    cur_water = p['water_source'] or ''
    cur_temp = p['serving_temperature'] or ''
    
    new_yeast = cur_yeast
    new_water = cur_water
    new_temp = cur_temp
    
    # Yeast mining
    if not new_yeast:
        if '協会7号' in text or '7号酵母' in text: new_yeast = '7号酵母 (きょうかい7号)'
        elif '協会9号' in text or '9号酵母' in text: new_yeast = '9号酵母 (きょうかい9号)'
        elif '1801' in text or '1801号' in text: new_yeast = '1801号酵母'
        elif '1401' in text: new_yeast = '1401号酵母 (金沢酵母)'
        elif '6号' in text: new_yeast = '6号酵母 (新政酵母)'
        elif 'きょうかい' in text or '酵母' in text: new_yeast = '蔵内自社酵母'

    # Water source mining
    if not new_water:
        if '伏流水' in text or '名水' in text or '湧水' in text: new_water = '蔵内湧水・天然伏流水'
        elif '極軟水' in text: new_water = '超軟水 (超ソフト)'
        elif '中硬水' in text or '宮水' in text: new_water = '中硬水 (宮水系)'

    # Serving Temperature mining based on SSI type & Category
    if not new_temp:
        if ssi == '薫酒' or '大吟醸' in cat or '純米大吟醸' in cat or 'スパークリング' in cat:
            new_temp = '冷やして (10℃〜12℃前後・花冷え)'
        elif ssi == '爽酒' or '本醸造' in cat or '普通酒' in cat or '生酒' in cat:
            new_temp = '良く冷やして (5℃〜10℃・雪冷え)'
        elif ssi == '醇酒' or '純米' in cat or '山廃' in cat or '生酛' in cat:
            new_temp = 'ぬる燗・常温 (15℃〜40℃・お燗が映える)'
        elif ssi == '熟酒' or '古酒' in cat or '熟成' in cat:
            new_temp = '常温〜ぬる燗 (15℃〜45℃)'

    if new_yeast != cur_yeast or new_water != cur_water or new_temp != cur_temp:
        cur.execute("UPDATE products SET yeast = ?, water_source = ?, serving_temperature = ? WHERE id = ?",
                    (new_yeast, new_water, new_temp, pid))
        p_updated += 1

conn.commit()

print(f"==========================================")
print(f"✨ 酒蔵 ＆ 銘柄詳細情報の深層高精度マイニング完了:")
print(f" - 更新・補完された酒蔵数: {b_updated} 件")
print(f" - 呑み頃温度・酵母・仕込み水を補完した製品数: {p_updated} 件")
print("==========================================")

conn.close()
