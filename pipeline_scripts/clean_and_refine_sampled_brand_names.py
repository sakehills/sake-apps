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

print("==================================================================")
print("🧼 サンプリング監査に基づく商品名・ブランド名・Webサフィックス徹底是正")
print("==================================================================\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 蔵元代表銘柄マップ（ブランド名が容量や季節名になっている場合のフォールバック）
BREWERY_CANONICAL_BRAND_MAP = {
    "泉金ホールディングス株式会社": "龍泉八重桜",
    "泉金酒造": "龍泉八重桜",
    "板野酒造場": "きびの吟風",
    "株式会社あさ開": "あさ開",
    "老松酒造有限会社": "老松",
    "大門酒造株式会社": "利休梅",
    "菊美人酒造 株式会社": "菊美人",
    "髙﨑酒造株式会社": "しま甘露",
    "沓掛酒造株式会社": "福無量",
    "相原酒造（株）": "雨後の月"
}

# 1. Webサフィックス・ノイズのクレンジングパターン
SUFFIX_PATTERNS = [
    r'\s*\|\s*.*$',
    r'\s*–\s*.*$',
    r'\s*-\s*公式.*$',
    r'\s*-\s*岩手の酒蔵.*$',
    r'\s*【クール便必須】',
    r'\s*\[クール便必須\]',
    r'\s*【別途箱が必要】',
    r'\s*\[箱、包装付き\]',
    r'\s*【冬季限定】',
    r'\s*【秋限定】'
]

cur.execute("SELECT id, brand_name, spec_name, brewery_name FROM products")
products = cur.fetchall()

cleaned_count = 0

for p in products:
    pid = p['id']
    brand = p['brand_name'] or ''
    spec = p['spec_name'] or ''
    brew = p['brewery_name'] or ''

    new_spec = spec
    for pat in SUFFIX_PATTERNS:
        new_spec = re.sub(pat, '', new_spec).strip()

    new_brand = brand
    # 容量やノイズがブランド名になっている場合
    if any(noise in brand for noise in ["1.8ℓ", "720ml", "180ml", "母の日", "父の日", "ギフトセット", "プレゼント", "生酒", "本醸造", "純米酒", "大吟醸", "しぼりたて"]):
        if brew in BREWERY_CANONICAL_BRAND_MAP:
            new_brand = BREWERY_CANONICAL_BRAND_MAP[brew]
        elif "あさ開" in spec: new_brand = "あさ開"
        elif "老松" in spec: new_brand = "老松"
        elif "利休梅" in spec: new_brand = "利休梅"
        elif "福無量" in spec: new_brand = "福無量"

    if new_spec != spec or new_brand != brand:
        # 変更後のspec_nameが既に同一酒蔵で存在するか確認
        cur.execute("SELECT id FROM products WHERE brewery_name = ? AND spec_name = ? AND id != ?", (brew, new_spec, pid))
        existing_dup = cur.fetchone()
        if existing_dup:
            # 既存のものがある場合は重複側を削除
            cur.execute("DELETE FROM products WHERE id = ?", (pid,))
        else:
            cur.execute("UPDATE products SET spec_name = ?, brand_name = ? WHERE id = ?", (new_spec, new_brand, pid))
        cleaned_count += 1

conn.commit()
conn.close()

print(f"✨ 商品名・ブランド名のノイズ是正完了: {cleaned_count} 件\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
