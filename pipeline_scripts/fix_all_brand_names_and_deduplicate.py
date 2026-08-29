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

print("=== 🛠️ 全銘柄ブランド名（brand_name）徹底修正＆重複完全解消パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# カテゴリ・特定名称プレフィックス一覧
PREFIXES_TO_STRIP = [
    "本格芋焼酎", "本格麦焼酎", "本格米焼酎", "本格黒糖焼酎", "本格そば焼酎", "本格焼酎",
    "芋焼酎", "麦焼酎", "米焼酎", "黒糖焼酎", "そば焼酎", "琉球泡盛", "泡盛",
    "超特撰", "特撰", "上撰", "佳撰",
    "純米大吟醸酒", "純米大吟醸", "純米吟醸酒", "純米吟醸", "特別純米酒", "特別純米",
    "大吟醸酒", "大吟醸", "吟醸酒", "吟醸", "特別本醸造酒", "特別本醸造", "本醸造酒", "本醸造",
    "純米酒", "純米", "普通酒", "スパークリング日本酒", "スパークリング",
    "クラフトサケ", "クラフトどぶろく", "どぶろく",
    "リキュール", "果実酒", "梅酒", "ゆず酒",
    "無濾過生原酒", "生原酒", "生酒", "原酒", "にごり酒", "ひやおろし", "しぼりたて", "初しぼり", "秋あがり"
]

# 1. 全銘柄の brand_name と spec_name を正規化・修正
cur.execute("SELECT id, brand_name, spec_name, category, brewery_name FROM products")
products = cur.fetchall()

fixed_brands_count = 0

for p in products:
    p_id = p['id']
    spec = p['spec_name'] or ''
    current_brand = p['brand_name'] or ''
    brew = p['brewery_name'] or ''

    # 1. spec_name から不要なカテゴリプレフィックスを剥がして真のブランド/銘柄名を抽出
    cleaned_name = spec
    changed = True
    while changed:
        changed = False
        for pref in PREFIXES_TO_STRIP:
            if cleaned_name.startswith(pref):
                cleaned_name = cleaned_name[len(pref):].strip()
                changed = True
                break

    # 先頭が酒蔵名で始まっている場合
    clean_brew = brew.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").strip()
    if clean_brew and cleaned_name.startswith(clean_brew):
        cleaned_name = cleaned_name[len(clean_brew):].strip()

    # ブランド名の抽出
    if " " in cleaned_name:
        extracted_brand = cleaned_name.split()[0].strip()
    else:
        # 空白がない場合は、最大8文字または英数字・漢字ブロック
        extracted_brand = cleaned_name[:8].strip()

    if not extracted_brand:
        extracted_brand = clean_brew if clean_brew else current_brand

    # brand_nameが特定名称のぶつ切り（本格芋焼、純米大吟など）になっている場合は置き換え
    if (
        current_brand in ["本格芋焼", "本格焼酎", "本格麦焼", "本格米焼", "純米大吟", "純米吟醸", "特別純米", "大吟醸酒", "本醸造酒", "リキュー", "スパーク", "クラフト", "どぶろく"]
        or len(current_brand) <= 2
        or any(current_brand.startswith(pref) for pref in ["本格", "純米", "大吟", "本醸", "特別", "リキュ"])
    ):
        cur.execute("UPDATE products SET brand_name = ? WHERE id = ?", (extracted_brand, p_id))
        fixed_brands_count += 1

print(f"✨ 修正された brand_name レコード数: {fixed_brands_count} 件")

# 2. 全面重複マージの再実行 (さつま白若潮 ID 21508 と ID 22214 などの統合)
def normalize_core(spec_name, brewery_name):
    s = (spec_name or "").lower().strip()
    b = (brewery_name or "").lower().strip()
    for corp in ["株式会社", "有限会社", "合資会社", "合名会社", "合同会社"]:
        b = b.replace(corp.lower(), "")
    b = b.strip()

    for pref in PREFIXES_TO_STRIP:
        s = s.replace(pref.lower(), "")

    s = re.sub(r'[\s　・／/「」『』【】［］\[\]\(\)（）]', '', s)
    s = re.sub(r'\d+度', '', s)
    s = re.sub(r'\d+%', '', s)
    b = re.sub(r'[\s　・／/「」『』【】［］\[\]\(\)（）]', '', b)
    return f"{b}___{s}"

cur.execute("""
    SELECT id, brand_name, spec_name, category, polish_ratio, rice_variety,
           alcohol, brewery_name, confidence
    FROM products
    ORDER BY brewery_name, id
""")
all_prods = cur.fetchall()

groups = {}
for p in all_prods:
    k = normalize_core(p['spec_name'], p['brewery_name'])
    if k not in groups:
        groups[k] = [p]
    else:
        groups[k].append(p)

deleted_ids = set()
for k, group in groups.items():
    if len(group) > 1:
        # 最も完成度の高いレコード（スペース区切りがあり度数やスペックが明記されているもの）を残す
        sorted_g = sorted(group, key=lambda x: (
            1 if " " in (x['spec_name'] or '') else 0,
            1 if (x['alcohol'] or 0) > 15.0 or (x['alcohol'] or 0) == 25.0 else 0,
            len(x['spec_name'] or ''),
            -x['id']
        ), reverse=True)

        primary = sorted_g[0]
        for red in sorted_g[1:]:
            deleted_ids.add(red['id'])
            cur.execute("UPDATE awards SET product_id = ? WHERE product_id = ?", (primary['id'], red['id']))
            cur.execute("UPDATE user_flavor_ratings SET product_id = ? WHERE product_id = ?", (primary['id'], red['id']))

if deleted_ids:
    placeholders = ",".join("?" for _ in deleted_ids)
    cur.execute(f"DELETE FROM products WHERE id IN ({placeholders})", list(deleted_ids))
    print(f"🧹 重複していた旧クローラー残存レコード削除数: {len(deleted_ids)} 件")

conn.commit()

# 若潮酒造のレコードを再確認
cur.execute("SELECT id, brand_name, spec_name, alcohol, brewery_name FROM products WHERE brewery_name LIKE '%若潮%'")
print("\n【若潮酒造の現在の確定データ】")
for r in cur.fetchall():
    print(f"  ・ID {r['id']}: brand_name=【{r['brand_name']}】 | spec_name=【{r['spec_name']}】 (Alc: {r['alcohol']}度)")

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.close()

print(f"\n==========================================")
print(f"🍶 最終クリーン後 登録製品総数: {total_prods} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
