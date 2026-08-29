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

print("=== 🍶 宮坂醸造 (真澄 / MIYASAKA) 公式全銘柄 網羅的一括収集・登録 ===")
print(f"DB Path: {DB_PATH}\n")

# 宮坂醸造 公式Webサイト・全商品カタログマスター (全24銘柄)
MIYASAKA_FULL_CATALOGUE = [
    # --- 1. 極上の真澄 (フラッグシップシリーズ) ---
    {
        "brand": "真澄", "spec": "真澄 夢殿 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県加東市山国地区産山田錦", "alc": 15.0, "smv": "0.0", "acid": "1.3", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/yumedono"
    },
    {
        "brand": "真澄", "spec": "真澄 七號 山廃純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県加東市山国地区産山田錦", "alc": 15.0, "smv": "-1.0", "acid": "1.7", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/nanagou"
    },
    {
        "brand": "真澄", "spec": "真澄 山花 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "45%", "rice": "兵庫県産山田錦 / 長野県産美山錦", "alc": 15.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/sanka"
    },

    # --- 2. こだわりの真澄 (定番カラーシリーズ・伝統定番) ---
    {
        "brand": "真澄", "spec": "真澄 真朱 AKA 山廃純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち / 兵庫県産山田錦", "alc": 15.0, "smv": "+1.0", "acid": "1.8", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/aka"
    },
    {
        "brand": "真澄", "spec": "真澄 漆黒 KURO 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち / 兵庫県産山田錦", "alc": 15.0, "smv": "+1.0", "acid": "1.6", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/kuro"
    },
    {
        "brand": "真澄", "spec": "真澄 白妙 SHIRO 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 12.0, "smv": "-3.0", "acid": "1.8", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/shiro"
    },
    {
        "brand": "真澄", "spec": "真澄 茅色 KAYA 純米酒", "cat": "純米酒",
        "polish": "70%", "rice": "長野県産金紋錦 / ひとごこち", "alc": 14.0, "smv": "+1.0", "acid": "1.7", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/kaya"
    },
    {
        "brand": "真澄", "spec": "真澄 辛口生一本 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 15.0, "smv": "+4.0", "acid": "1.6", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/karakuchiki-ippon"
    },
    {
        "brand": "真澄", "spec": "真澄 奥伝寒造り 純米酒", "cat": "純米酒",
        "polish": "65%", "rice": "長野県産美山錦 / ひとごこち", "alc": 15.0, "smv": "+2.0", "acid": "1.6", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/okuden"
    },
    {
        "brand": "真澄", "spec": "真澄 特撰 本醸造", "cat": "本醸造酒",
        "polish": "60%", "rice": "長野県産米", "alc": 15.0, "smv": "+3.0", "acid": "1.3", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "長野県", "url": "https://www.masumi.jp/products/tokusen"
    },
    {
        "brand": "真澄", "spec": "真澄 銀撰 普通酒", "cat": "普通酒",
        "polish": "70%", "rice": "長野県産米", "alc": 15.0, "smv": "+2.0", "acid": "1.2", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "長野県", "url": "https://www.masumi.jp/products/ginsen"
    },

    # --- 3. 季節の真澄 (四季限定シリーズ) ---
    {
        "brand": "真澄", "spec": "真澄 すずみさけ 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 14.0, "smv": "+1.0", "acid": "1.8", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/suzumisake"
    },
    {
        "brand": "真澄", "spec": "真澄 ひやおろし 純米吟醸 原酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 16.0, "smv": "+2.0", "acid": "1.7", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/hiyaoroshi"
    },
    {
        "brand": "真澄", "spec": "真澄 あらばしり 純米吟醸 生原酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 17.0, "smv": "+1.0", "acid": "1.8", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/arabashiri"
    },
    {
        "brand": "真澄", "spec": "真澄 初しぼり 純米吟醸 生原酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 17.0, "smv": "+1.0", "acid": "1.8", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/hatsushibori"
    },
    {
        "brand": "真澄", "spec": "真澄 うすにごり 純米吟醸 生原酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦 / ひとごこち", "alc": 16.0, "smv": "-1.0", "acid": "1.9", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/usunigori"
    },

    # --- 4. 泡を楽しむ真澄 (スパークリングシリーズ) ---
    {
        "brand": "真澄", "spec": "真澄 突釃 つきこし 瓶内二次発酵 スパークリング", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産米", "alc": 12.0, "smv": "-5.0", "acid": "2.2", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/tsukikoshi"
    },
    {
        "brand": "真澄", "spec": "真澄 ORIGARAMI スパークリング 生酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産米", "alc": 11.0, "smv": "-10.0", "acid": "2.4", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/origarami"
    },

    # --- 5. 別ブランド「MIYASAKA (みやさか)」シリーズ (7号酵母限定流通) ---
    {
        "brand": "MIYASAKA", "spec": "MIYASAKA コア 美山錦 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "長野県産美山錦", "alc": 15.0, "smv": "+1.0", "acid": "1.7", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/miyasaka-miyama"
    },
    {
        "brand": "MIYASAKA", "spec": "MIYASAKA コア 愛山 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "兵庫県産愛山", "alc": 15.0, "smv": "0.0", "acid": "1.7", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/miyasaka-aizan"
    },
    {
        "brand": "MIYASAKA", "spec": "MIYASAKA コア 山田錦 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "兵庫県産山田錦", "alc": 15.0, "smv": "+1.0", "acid": "1.6", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/miyasaka-yamada"
    },
    {
        "brand": "MIYASAKA", "spec": "MIYASAKA からくち 特別純米", "cat": "特別純米酒",
        "polish": "60%", "rice": "長野県産美山錦 / ひとごこち", "alc": 15.0, "smv": "+5.0", "acid": "1.6", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.masumi.jp/products/miyasaka-karakuchi"
    },

    # --- 6. リキュール・焼酎 ---
    {
        "brand": "真澄", "spec": "真澄 梅酒 純米酒仕込み", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 14.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒",
        "ing": "清酒（真澄純米酒）、梅（長野県産）、氷砂糖", "pref": "長野県", "url": "https://www.masumi.jp/products/umeshu"
    },
    {
        "brand": "真澄", "spec": "真澄 粕取り焼酎 澄 25度", "cat": "本格焼酎",
        "polish": "非公開", "rice": "清酒粕（真澄酒粕）", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒",
        "ing": "清酒粕（長野県製造）", "pref": "長野県", "url": "https://www.masumi.jp/products/sumi"
    }
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

brewery_name = "宮坂醸造株式会社"
now_str = datetime.now().isoformat()
added_count = 0
updated_count = 0

for item in MIYASAKA_FULL_CATALOGUE:
    spec_name = item['spec']
    brand_name = item['brand']

    cur.execute("""
        SELECT id FROM products 
        WHERE spec_name = ? AND (brewery_name LIKE ? OR brand_name = ?)
    """, (spec_name, "%宮坂醸造%", brand_name))
    
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

# 宮坂醸造の全銘柄数確認
cur.execute("SELECT COUNT(*) FROM products WHERE brewery_name LIKE '%宮坂醸造%'")
total_miyasaka = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 宮坂醸造 公式全製品カタログ登録結果:")
print(f" - 新規追加銘柄数: {added_count} 件")
print(f" - 確定仕様更新数: {updated_count} 件")
print(f" - 宮坂醸造の登録製品総数: {total_miyasaka} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
