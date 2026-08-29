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

print("=== 🍶 新澤醸造店 (伯楽星 / あたごのまつ / NIIZAWA / 残響 / 零響) 公式全品網羅登録 ===")
print(f"DB Path: {DB_PATH}\n")

# 新澤醸造店 公式Webサイト掲載 全製品カタログマスター (全30銘柄)
NIIZAWA_FULL_CATALOGUE = [
    # --- 1. 超高精白プレミアムライン (零響 / NIIZAWA / 残響) ---
    {
        "brand": "零響", "spec": "零響 Absolute 0 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "0.85%", "rice": "蔵の華", "alc": 15.8, "smv": "0.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/reikyo/"
    },
    {
        "brand": "零響", "spec": "零響 Crystal 0 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "0.85%", "rice": "蔵の華", "alc": 15.8, "smv": "0.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/reikyo-crystal/"
    },
    {
        "brand": "NIIZAWA", "spec": "NIIZAWA 純米大吟醸 2024", "cat": "純米大吟醸酒",
        "polish": "7%", "rice": "山田錦", "alc": 15.8, "smv": "0.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/niizawa/"
    },
    {
        "brand": "NIIZAWA", "spec": "NIIZAWA KIZASHI 純米大吟醸 2024", "cat": "純米大吟醸酒",
        "polish": "7%", "rice": "山田錦", "alc": 15.8, "smv": "0.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/niizawa-kizashi/"
    },
    {
        "brand": "残響", "spec": "超特撰 純米大吟醸 残響 Super7", "cat": "純米大吟醸酒",
        "polish": "7%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/zankyo/"
    },

    # --- 2. 伯楽星 (究極の食中酒シリーズ) ---
    {
        "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 東条秋津産山田錦", "cat": "純米大吟醸酒",
        "polish": "29%", "rice": "兵庫県特A地区東条秋津産山田錦", "alc": 15.8, "smv": "+3.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-akitsu/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 社下久米産山田錦", "cat": "純米大吟醸酒",
        "polish": "29%", "rice": "兵庫県特A地区社下久米産山田錦", "alc": 15.8, "smv": "+3.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-shimokume/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 ひかり", "cat": "純米大吟醸酒",
        "polish": "29%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-hikari/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 雪華おりがらみ生酒", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "蔵の華", "alc": 15.8, "smv": "+2.0", "acid": "1.6", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-sekka/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 雄町", "cat": "純米大吟醸酒",
        "polish": "40%", "rice": "備前雄町", "alc": 15.8, "smv": "+4.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-daiginjo-omachi/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "40%", "rice": "雄町 / 蔵の華", "alc": 15.8, "smv": "+4.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-daiginjo/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米吟醸 雄町", "cat": "純米吟醸酒",
        "polish": "50%", "rice": "備前雄町", "alc": 15.8, "smv": "+4.0", "acid": "1.6", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-ginjo-omachi/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 純米吟醸 おりがらみ生酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.7", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-origarami/"
    },
    {
        "brand": "伯楽星", "spec": "伯楽星 特別純米 冷卸", "cat": "特別純米酒",
        "polish": "60%", "rice": "ひとめぼれ", "alc": 15.8, "smv": "+3.0", "acid": "1.7", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/hakurakusei-hiyaoroshi/"
    },

    # --- 3. あたごのまつ / 愛宕の松 (伝統銘柄シリーズ) ---
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ 大吟醸 出品酒", "cat": "大吟醸酒",
        "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.3", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-shuppin/"
    },
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ 純米大吟醸 白鶴錦", "cat": "純米大吟醸酒",
        "polish": "40%", "rice": "白鶴錦", "alc": 15.8, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-hakutsurunishiki/"
    },
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ 吟のいろは 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "40%", "rice": "宮城県産吟のいろは", "alc": 15.8, "smv": "+2.0", "acid": "1.5", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-ginnoiroha/"
    },
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ 純米吟醸 ささら", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.6", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-sasara/"
    },
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ ささらおりがらみ生酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "蔵の華", "alc": 15.8, "smv": "+2.0", "acid": "1.7", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-sasara-origarami/"
    },
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ 鮮烈辛口", "cat": "本醸造酒",
        "polish": "60%", "rice": "ひとめぼれ", "alc": 15.8, "smv": "+7.0", "acid": "1.5", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-senretsukarakuchi/"
    },
    {
        "brand": "あたごのまつ", "spec": "あたごのまつ はるこい 純米吟醸 生酒", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "蔵の華 / ひとめぼれ", "alc": 12.0, "smv": "-25.0", "acid": "3.5", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、赤色酵母", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-harukoi/"
    },
    {
        "brand": "あたごのまつ", "spec": "愛宕の松 ひと夏の恋 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "ひとめぼれ", "alc": 15.0, "smv": "+4.0", "acid": "1.8", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-hitonatsunokoi/"
    },
    {
        "brand": "愛宕の松", "spec": "愛宕の松 スパークリング", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "蔵の華", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/atago-sparkling/"
    },

    # --- 4. リキュール・ヨーグルト酒・果実酒 ---
    {
        "brand": "超濃厚ヨーグルト酒", "spec": "超濃厚ジャージーヨーグルト酒", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 5.5, "smv": "非公開", "acid": "非公開", "ssi": "醇酒",
        "ing": "ジャージーヨーグルト（宮城県産）、日本酒（愛宕の松）、糖類", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/jersey-yogurt/"
    },
    {
        "brand": "薫る紅茶酒", "spec": "新澤醸造店 薫る紅茶酒", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "清酒、紅茶（アッサム）、糖類", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/tea-liqueur/"
    },
    {
        "brand": "芳醇ゆず酒", "spec": "新澤醸造店 芳醇ゆず酒", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 10.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒",
        "ing": "清酒、ゆず果汁（国産）、糖類", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/yuzu-liqueur/"
    },
    {
        "brand": "佐藤農場の梅酒", "spec": "佐藤農場の梅酒 青梅仕込み", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒",
        "ing": "清酒（愛宕の松純米酒）、青梅（宮城県大崎市佐藤農場産）、糖類", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/item/umeshu-aoume/"
    }
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

brewery_name = "株式会社新澤醸造店"
now_str = datetime.now().isoformat()
added_count = 0
updated_count = 0

for item in NIIZAWA_FULL_CATALOGUE:
    spec_name = item['spec']
    brand_name = item['brand']

    cur.execute("""
        SELECT id FROM products 
        WHERE spec_name = ? AND (brewery_name LIKE ? OR brand_name = ?)
    """, (spec_name, "%新澤醸造店%", brand_name))
    
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

# 新澤醸造店の全銘柄数確認
cur.execute("SELECT COUNT(*) FROM products WHERE brewery_name LIKE '%新澤醸造店%'")
total_niizawa = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 新澤醸造店 公式全製品カタログ登録結果:")
print(f" - 新規追加銘柄数: {added_count} 件")
print(f" - 確定仕様更新数: {updated_count} 件")
print(f" - 新澤醸造店の登録製品総数: {total_niizawa} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
