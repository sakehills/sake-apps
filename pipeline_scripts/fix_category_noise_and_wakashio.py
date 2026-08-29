import os
import sys
import re
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🛠️ カテゴリ単体名・不完全テキスト・成分説明文の徹底クレンジング ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. 単なるカテゴリ名・分類名のみの不完全レコードの削除
cur.execute("""
    DELETE FROM products
    WHERE (
        spec_name IN (
            '本格芋焼酎', '本格麦焼酎', '本格米焼酎', '本格黒糖焼酎', '本格焼酎', '本格そば焼酎',
            '芋焼酎', '麦焼酎', '米焼酎', '黒糖焼酎', 'そば焼酎', '泡盛', '琉球泡盛',
            '純米大吟醸', '純米吟醸', '特別純米', '純米酒', '大吟醸', '吟醸', '特別本醸造', '本醸造', '普通酒',
            '純米大吟醸酒', '純米吟醸酒', '特別純米酒', '大吟醸酒', '吟醸酒', '特別本醸造酒', '本醸造酒',
            'リキュール', '果実酒', 'クラフトサケ', 'どぶろく', 'スパークリング', '生酒', '原酒',
            '生原酒', '無濾過生原酒', 'にごり酒', 'ひやおろし', 'しぼりたて', '秋あがり', '初しぼり',
            '梅酒', 'ゆず酒', '長期熟成酒', '古酒', '熟成酒'
        )
        OR spec_name LIKE '・%'
        OR spec_name LIKE '%・カルダモン%'
        OR spec_name LIKE '%・いちご%'
        OR spec_name LIKE '%を使用した%'
        OR spec_name LIKE '%で仕込んだ%'
        OR spec_name LIKE '%です。'
        OR spec_name LIKE '%ます。'
        OR spec_name LIKE '%でした。'
        OR spec_name LIKE '%ください。'
        OR spec_name LIKE '%になります。'
        OR spec_name LIKE '%ございます。'
        OR spec_name LIKE '%おすすめ%'
        OR spec_name LIKE '%の検索結果%'
    ) AND confidence = 1.0 AND evidence LIKE '%Web Crawler%'
""")

deleted_cat_count = cur.rowcount
print(f"🧹 単体カテゴリ名・文章系不完全レコード削除件数: {deleted_cat_count} 件")

# 2. 若潮酒造 (鹿児島県志布志市) の正規公式ラインナップ登録
WAKASHIO_OFFICIAL_CATALOGUE = [
    {"brand": "さつま若潮", "spec": "さつま白若潮 本格芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "黄金千貫・白麹", "alc": 25.0},
    {"brand": "さつま若潮", "spec": "さつま黒若潮 本格芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "黄金千貫・黒麹", "alc": 25.0},
    {"brand": "さつま若潮", "spec": "さつま黄若潮 本格芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "黄金千貫・黄麹", "alc": 25.0},
    {"brand": "千亀女", "spec": "千亀女 甕仕込み 本格芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "黄金千貫・黒麹", "alc": 25.0},
    {"brand": "千亀女", "spec": "千亀女 甕仕込み 本格麦焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "二条大麦・白麹", "alc": 25.0},
    {"brand": "GLOW", "spec": "GLOW 01 本格芋焼酎 フルーティー 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "サツマイモ・香り酵母", "alc": 25.0},
    {"brand": "GLOW", "spec": "GLOW 02 本格芋焼酎 ハーバル 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "サツマイモ・香り酵母", "alc": 25.0},
    {"brand": "樵", "spec": "樵（きこり） 本格芋焼酎 天然アルカリ温泉水仕込み 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "黄金千貫・白麹", "alc": 25.0},
    {"brand": "歩", "spec": "歩（あゆむ） 本格芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "サツマイモ・米麹", "alc": 25.0}
]

cur.execute("SELECT id FROM breweries WHERE name LIKE '%若潮酒造%'")
brew_row = cur.fetchone()
if brew_row:
    cur.execute("UPDATE breweries SET website = 'https://wakashio.com/' WHERE id = ?", (brew_row['id'],))

now_str = subprocess.check_output([sys.executable, "-c", "from datetime import datetime; print(datetime.now().isoformat())"]).decode().strip()

for item in WAKASHIO_OFFICIAL_CATALOGUE:
    cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name LIKE '%若潮酒造%'", (item['spec'],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, '若潮酒造株式会社', '鹿児島県', 1.0, 'Official Verified (https://wakashio.com/)', ?, 'active')
        """, (item['brand'], item['spec'], item['cat'], item['polish'], item['rice'], item['alc'], now_str))
        print(f"✨ [若潮酒造 正規登録] {item['spec']}")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
total_brews = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 最終クリーン後 登録製品総数: {total_prods} 件")
print(f"🏭 紐付け酒蔵総数            : {total_brews} 蔵")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
