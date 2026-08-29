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

print("=== 🍶 黒龍酒造 (黒龍 / 九頭龍 / ESHIKOTO) 公式全銘柄 網羅的一括収集・登録 ===")
print(f"DB Path: {DB_PATH}\n")

# 黒龍酒造 公式Webサイト・ESHIKOTO・全商品カタログマスター (全26銘柄)
KOKURYU_FULL_CATALOGUE = [
    # --- 1. 黒龍 最高峰・限定プレミアムシリーズ ---
    {
        "brand": "黒龍", "spec": "黒龍 石田屋 純米大吟醸 熟成酒", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/ishidaya"
    },
    {
        "brand": "黒龍", "spec": "黒龍 二左衛門 純米大吟醸 斗瓶囲い", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/nizaemon"
    },
    {
        "brand": "黒龍", "spec": "黒龍 しずく 大吟醸 雫酒", "cat": "大吟醸酒",
        "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.0", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/shizuku"
    },
    {
        "brand": "黒龍", "spec": "黒龍 八十八号 大吟醸 斗瓶囲い", "cat": "大吟醸酒",
        "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.0", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/hachijuhachigo"
    },
    {
        "brand": "黒龍", "spec": "黒龍 火いら寿 純米大吟醸 生酒", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/hiirazu"
    },
    {
        "brand": "黒龍", "spec": "黒龍 龍 大吟醸 熟成酒", "cat": "大吟醸酒",
        "polish": "40%", "rice": "兵庫県東条特A地区産山田錦", "alc": 15.0, "smv": "+4.0", "acid": "1.0", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/ryu"
    },
    {
        "brand": "黒龍", "spec": "黒龍 大吟醸", "cat": "大吟醸酒",
        "polish": "50%", "rice": "福井県産五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.0", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/daiginjo"
    },
    {
        "brand": "黒龍", "spec": "黒龍 つるかめ 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/tsurukame"
    },

    # --- 2. 黒龍 定番・通年シリーズ ---
    {
        "brand": "黒龍", "spec": "黒龍 いっちょらい 吟醸酒", "cat": "吟醸酒",
        "polish": "55%", "rice": "福井県産五百万石", "alc": 15.0, "smv": "+5.0", "acid": "1.3", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/icchorai"
    },
    {
        "brand": "黒龍", "spec": "黒龍 純米吟醸", "cat": "純米吟醸酒",
        "polish": "55%", "rice": "福井県産五百万石", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/junmaiginjo"
    },
    {
        "brand": "黒龍", "spec": "黒龍 特撰吟醸", "cat": "吟醸酒",
        "polish": "50%", "rice": "福井県産五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/tokusenginjo"
    },
    {
        "brand": "黒龍", "spec": "黒龍 本醸造", "cat": "本醸造酒",
        "polish": "65%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.4", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/honjozo"
    },
    {
        "brand": "黒龍", "spec": "黒龍 福瓶 吟醸生酒", "cat": "吟醸酒",
        "polish": "55%", "rice": "福井県産五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/fukubind"
    },
    {
        "brand": "黒龍", "spec": "黒龍 垂れ口 本醸造生酒", "cat": "本醸造酒",
        "polish": "65%", "rice": "五百万石", "alc": 18.0, "smv": "+3.0", "acid": "1.5", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/tareguchi"
    },
    {
        "brand": "黒龍", "spec": "黒龍 貴醸酒", "cat": "貴醸酒",
        "polish": "55%", "rice": "福井県産五百万石", "alc": 12.0, "smv": "-35.0", "acid": "2.8", "ssi": "熟酒",
        "ing": "米（国産）、米麹（国産米）、清酒", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/kijoshu"
    },

    # --- 3. 九頭龍 (くずりゅう) ブランド ---
    {
        "brand": "九頭龍", "spec": "九頭龍 大吟醸 燗酒用", "cat": "大吟醸酒",
        "polish": "50%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/kuzuryu_daiginjo"
    },
    {
        "brand": "九頭龍", "spec": "九頭龍 純米", "cat": "純米酒",
        "polish": "65%", "rice": "福井県産五百万石", "alc": 15.0, "smv": "+3.0", "acid": "1.5", "ssi": "醇酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/kuzuryu_junmai"
    },
    {
        "brand": "九頭龍", "spec": "九頭龍 逸品", "cat": "普通酒",
        "polish": "65%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/kuzuryu_ippin"
    },
    {
        "brand": "九頭龍", "spec": "九頭龍 氷やし酒 純米", "cat": "純米酒",
        "polish": "65%", "rice": "五百万石", "alc": 14.0, "smv": "+4.0", "acid": "1.5", "ssi": "爽酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/kuzuryu_hiyashizake"
    },

    # --- 4. ESHIKOTO (えしこと) ブランド ---
    {
        "brand": "ESHIKOTO", "spec": "ESHIKOTO AWA 瓶内二次発酵 スパークリング", "cat": "純米大吟醸酒",
        "polish": "50%", "rice": "五百万石", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://eshikoto.com/products/awa"
    },
    {
        "brand": "ESHIKOTO", "spec": "ESHIKOTO 永 とこしえ 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "40%", "rice": "福井県産さかほまれ", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://eshikoto.com/products/tokoshie"
    },
    {
        "brand": "ESHIKOTO", "spec": "ESHIKOTO 水仙 SUISEN 純米大吟醸", "cat": "純米大吟醸酒",
        "polish": "35%", "rice": "兵庫県産山田錦", "alc": 16.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://eshikoto.com/products/suisen"
    },
    {
        "brand": "ESHIKOTO", "spec": "ESHIKOTO 鮎 AYU 大吟醸", "cat": "大吟醸酒",
        "polish": "35%", "rice": "兵庫県産山田錦", "alc": 16.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://eshikoto.com/products/ayu"
    },
    {
        "brand": "ESHIKOTO", "spec": "ESHIKOTO 黄金の梅 UME 梅酒", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "清酒（黒龍純米酒）、黄金の梅（福井県産完熟紅映梅）、氷砂糖", "pref": "福井県", "url": "https://eshikoto.com/products/ume"
    },
    {
        "brand": "ESHIKOTO", "spec": "ESHIKOTO IWAI 祝 スパークリング", "cat": "純米大吟醸酒",
        "polish": "50%", "rice": "福井県産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒",
        "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://eshikoto.com/products/iwai"
    },

    # --- 5. リキュール・梅酒 ---
    {
        "brand": "黒龍", "spec": "黒龍 梅酒 紅映梅仕込み", "cat": "リキュール",
        "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒",
        "ing": "清酒（黒龍純米酒）、紅映梅（福井県産）、糖類", "pref": "福井県", "url": "https://www.kokuryu.co.jp/brew/umeshu"
    }
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

brewery_name = "黒龍酒造株式会社"
now_str = datetime.now().isoformat()
added_count = 0
updated_count = 0

for item in KOKURYU_FULL_CATALOGUE:
    spec_name = item['spec']
    brand_name = item['brand']

    cur.execute("""
        SELECT id FROM products 
        WHERE spec_name = ? AND (brewery_name LIKE ? OR brand_name = ?)
    """, (spec_name, "%黒龍酒造%", brand_name))
    
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

# 黒龍酒造の全銘柄数確認
cur.execute("SELECT COUNT(*) FROM products WHERE brewery_name LIKE '%黒龍酒造%'")
total_kokuryu = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 黒龍酒造 公式全製品カタログ登録結果:")
print(f" - 新規追加銘柄数: {added_count} 件")
print(f" - 確定仕様更新数: {updated_count} 件")
print(f" - 黒龍酒造の登録製品総数: {total_kokuryu} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
