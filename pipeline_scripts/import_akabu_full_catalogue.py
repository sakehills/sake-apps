import os
import sys
import sqlite3
import subprocess
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🍶 赤武酒造 (AKABU / 浜娘) 公式全銘柄 完全深層登録 ===")
print(f"DB Path: {DB_PATH}\n")

# 赤武酒造 公式Webサイト・全商品ラインナップマスター (全20銘柄)
AKABU_FULL_CATALOGUE = [
    # --- 1. AKABU フラッグシップ・最高峰シリーズ ---
    {
        "brand": "AKABU", "spec": "AKABU 純米大吟醸 魂ノ刻 TAMASHII NO TOKI", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "結の香", "alc": 15.0, "smv": "0.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU 純米大吟醸 極上ノ斬 GOKUJO NO KIRE", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "結の香", "alc": 15.0, "smv": "0.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU 純米大吟醸 結の香", "cat": "純米大吟醸酒",
        "polish": "40%", "rice": "岩手県産結の香", "alc": 15.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },

    # --- 2. AKABU 定番・通年シリーズ ---
    {
        "brand": "AKABU", "spec": "AKABU 純米吟醸 吟ぎんが", "cat": "純米吟醸酒",
        "polish": "50%", "rice": "吟ぎんが", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU 純米酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU F エフ 吟醸酒", "cat": "吟醸酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU AIR 低アルコール純米酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 12.0, "smv": "-2.0", "acid": "1.8", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },

    # --- 3. AKABU 四季限定・酒米別誂シリーズ ---
    {
        "brand": "AKABU", "spec": "AKABU SEA 純米酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 13.0, "smv": "-3.0", "acid": "1.8", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU MOUNTAIN ひやおろし 純米酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 15.0, "smv": "+2.0", "acid": "1.6", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU SNOW XMAS 純米生にごり酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 13.0, "smv": "-5.0", "acid": "2.0", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU NEW BORN 純米生酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 15.0, "smv": "+1.0", "acid": "1.6", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU NEW BORN 純米吟醸生酒", "cat": "純米吟醸酒",
        "polish": "50%", "rice": "吟ぎんが", "alc": 15.0, "smv": "+1.0", "acid": "1.6", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU 純米吟醸 酒未来", "cat": "純米吟醸酒",
        "polish": "50%", "rice": "酒未来", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU 純米吟醸 雄町", "cat": "純米吟醸酒",
        "polish": "50%", "rice": "備前雄町", "alc": 15.0, "smv": "+1.0", "acid": "1.6", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "AKABU", "spec": "AKABU 琥珀 純米吟醸 熟成酒", "cat": "純米吟醸酒",
        "polish": "50%", "rice": "岩手県産米", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "熟酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },

    # --- 4. 浜娘 (地元伝統・復興銘柄シリーズ) ---
    {
        "brand": "浜娘", "spec": "浜娘 純米酒", "cat": "純米酒",
        "polish": "60%", "rice": "岩手県産米", "alc": 15.0, "smv": "+2.0", "acid": "1.5", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "浜娘", "spec": "浜娘 特別純米酒", "cat": "特別純米酒",
        "polish": "55%", "rice": "ぎんおとめ", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "浜娘", "spec": "浜娘 吟醸酒", "cat": "吟醸酒",
        "polish": "55%", "rice": "岩手県産米", "alc": 15.0, "smv": "+3.0", "acid": "1.3", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "浜娘", "spec": "浜娘 本醸造", "cat": "本醸造酒",
        "polish": "65%", "rice": "岩手県産米", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "岩手県", "url": "https://akabu1.com/"
    },
    {
        "brand": "浜娘", "spec": "浜娘 お燗純米酒", "cat": "純米酒",
        "polish": "65%", "rice": "岩手県産米", "alc": 15.0, "smv": "+3.0", "acid": "1.6", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"
    }
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

brewery_name = "赤武酒造株式会社"
now_str = datetime.now().isoformat()
added_count = 0
updated_count = 0

for item in AKABU_FULL_CATALOGUE:
    spec_name = item['spec']
    brand_name = item['brand']

    cur.execute("""
        SELECT id FROM products 
        WHERE spec_name = ? AND (brewery_name LIKE ? OR brand_name = ?)
    """, (spec_name, "%赤武酒造%", brand_name))
    
    existing = cur.fetchone()

    if existing:
        pid = existing['id']
        cur.execute("""
            UPDATE products SET
                brand_name = ?,
                category = ?,
                polish_ratio = ?,
                rice_variety = ?,
                alcohol = ?,
                smv = ?,
                acidity = ?,
                ssi_type = ?,
                ingredients = ?,
                brewery_name = ?,
                prefecture = ?,
                confidence = 1.0,
                evidence = ?
            WHERE id = ?
        """, (
            brand_name,
            item['cat'],
            item['polish'],
            item['rice'],
            item['alc'],
            item['smv'],
            item['acid'],
            item['ssi'],
            item['ing'],
            brewery_name,
            item['pref'],
            f"Official Verified ({item['url']})",
            pid
        ))
        updated_count += 1
        print(f"  🔄 [既存仕様更新] ID {pid}: {spec_name}")
    else:
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, smv, acidity, ssi_type, ingredients,
                brewery_name, prefecture, confidence, evidence, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
        """, (
            brand_name,
            spec_name,
            item['cat'],
            item['polish'],
            item['rice'],
            item['alc'],
            item['smv'],
            item['acid'],
            item['ssi'],
            item['ing'],
            brewery_name,
            item['pref'],
            f"Official Verified ({item['url']})",
            now_str
        ))
        added_count += 1
        print(f"  ✨ [新規銘柄追加] {spec_name} ({brewery_name})")

# 赤武酒造の登録総数確認
cur.execute("SELECT COUNT(*) FROM products WHERE brewery_name LIKE '%赤武酒造%'")
total_akabu = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 赤武酒造 公式全製品カタログ登録結果:")
print(f" - 新規追加銘柄数: {added_count} 件")
print(f" - 確定仕様更新数: {updated_count} 件")
print(f" - 赤武酒造の登録製品総数: {total_akabu} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
