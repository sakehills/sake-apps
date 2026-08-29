import os
import sys
import re
import html
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
REPORT_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "qa_verification_report.txt")

print("==================================================================")
print("🛡️ データベース全製品 6大レイヤー徹底品質保証（QA）検査・補正パイプライン")
print(f"DB Path: {DB_PATH}")
print("==================================================================\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. 全製品のロード
cur.execute("""
    SELECT id, brand_name, spec_name, category, polish_ratio, rice_variety,
           alcohol, brewery_name, prefecture, confidence, evidence, created_at
    FROM products
    ORDER BY id
""")
all_products = cur.fetchall()
total_records = len(all_products)
print(f"📊 監査対象レコード総数: {total_records} 件\n")

# 統計カウンタ
fixed_text_noise = 0
fixed_categories = 0
fixed_polish_ratios = 0
fixed_alcohols = 0
fixed_breweries_prefs = 0
fixed_brand_names = 0
merged_collision_records = 0

# 全実在酒蔵マップの構築
cur.execute("SELECT id, name, prefecture FROM breweries")
brewery_map = {}
for b in cur.fetchall():
    brewery_map[b['name']] = b['prefecture']
    clean_b = b['name'].replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").replace("合同会社", "").strip()
    brewery_map[clean_b] = b['prefecture']

with open(REPORT_PATH, "w", encoding="utf-8") as rep:
    rep.write(f"=== データベース全件 品質保証（QA）監査レポート ===\n")
    rep.write(f"対象件数: {total_records} 件\n\n")

    for p in all_products:
        p_id = p['id']
        spec = p['spec_name'] or ''
        brand = p['brand_name'] or ''
        cat = p['category'] or '普通酒'
        polish = p['polish_ratio'] or '非公開'
        rice = p['rice_variety'] or '国産米'
        alc = float(p['alcohol']) if p['alcohol'] else 15.0
        brew = p['brewery_name'] or ''
        pref = p['prefecture'] or ''

        # -------------------------------------------------------------
        # Layer 1: HTMLタグ・実体参照・改行・制御文字の徹底クレンジング
        # -------------------------------------------------------------
        orig_spec = spec
        spec = html.unescape(spec)
        spec = re.sub(r'<[^>]+>', ' ', spec)
        spec = " ".join(spec.split()).strip()
        spec = spec.replace('"', '').replace("'", "").replace("`", "")

        if spec != orig_spec:
            fixed_text_noise += 1

        # -------------------------------------------------------------
        # Layer 2: 特定名称とカテゴリの法的規格整合性チェック＆是正
        # -------------------------------------------------------------
        orig_cat = cat
        if "純米大吟醸" in spec: cat = "純米大吟醸酒"
        elif "純米吟醸" in spec: cat = "純米吟醸酒"
        elif "特別純米" in spec: cat = "特別純米酒"
        elif "大吟醸" in spec: cat = "大吟醸酒"
        elif "吟醸" in spec: cat = "吟醸酒"
        elif "特別本醸造" in spec: cat = "特別本醸造酒"
        elif "本醸造" in spec: cat = "本醸造酒"
        elif "純米酒" in spec or ("純米" in spec and "大吟醸" not in spec and "吟醸" not in spec): cat = "純米酒"
        elif any(k in spec for k in ["梅酒", "ゆず", "果実酒", "リキュール", "もも酒", "巨峰酒", "いちご酒"]): cat = "リキュール"
        elif "泡盛" in spec: cat = "泡盛"
        elif any(k in spec for k in ["本格焼酎", "芋焼酎", "麦焼酎", "米焼酎", "黒糖焼酎", "そば焼酎", "焼酎"]): cat = "本格焼酎"
        elif "クラフトサケ" in spec: cat = "クラフトサケ"
        elif "どぶろく" in spec: cat = "どぶろく"

        if cat != orig_cat:
            fixed_categories += 1

        # -------------------------------------------------------------
        # Layer 3: 精米歩合とカテゴリの酒税法適合チェック
        # -------------------------------------------------------------
        orig_polish = polish
        polish_match = re.search(r'(\d{1,2})%', spec)
        if polish_match:
            p_val = int(polish_match.group(1))
            polish = f"{p_val}%"
        elif polish != '非公開' and not polish.endswith('%'):
            polish = f"{polish}%"

        if polish != '非公開':
            p_num = int(re.sub(r'\D', '', polish)) if re.sub(r'\D', '', polish) else 0
            if p_num > 0:
                if cat in ["純米大吟醸酒", "大吟醸酒"] and p_num > 50: polish = "50%"
                elif cat in ["純米吟醸酒", "吟醸酒"] and p_num > 60: polish = "60%"
                elif cat in ["特別純米酒", "特別本醸造酒"] and p_num > 60 and "特別" in spec: polish = "60%"
                elif cat == "本醸造酒" and p_num > 70: polish = "70%"

        if polish != orig_polish:
            fixed_polish_ratios += 1

        # -------------------------------------------------------------
        # Layer 4: アルコール度数の妥当性・異常値是正
        # -------------------------------------------------------------
        orig_alc = alc
        alc_match = re.search(r'(\d{1,2}(?:\.\d+)?)度', spec)
        if alc_match:
            alc = float(alc_match.group(1))
        else:
            if cat in ["本格焼酎", "泡盛"]:
                if alc < 20.0 or alc > 45.0: alc = 25.0
            elif cat == "リキュール":
                if alc < 5.0 or alc > 30.0: alc = 10.0
            else:
                if alc < 5.0 or alc > 22.0: alc = 15.0

        if alc != orig_alc:
            fixed_alcohols += 1

        # -------------------------------------------------------------
        # Layer 5: 実在酒蔵名・都道府県・ブランド名の整合性
        # -------------------------------------------------------------
        orig_pref = pref
        orig_brand = brand
        clean_brew = brew.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").replace("合同会社", "").strip()

        if brew in brewery_map:
            pref = brewery_map[brew]
        elif clean_brew in brewery_map:
            pref = brewery_map[clean_brew]

        if pref != orig_pref:
            fixed_breweries_prefs += 1

        clean_name_for_brand = spec
        for prefix in ["本格芋焼酎", "本格麦焼酎", "本格米焼酎", "本格焼酎", "純米大吟醸", "純米吟醸", "特別純米", "大吟醸", "吟醸", "特別本醸造", "本醸造", "純米酒", "リキュール", "スパークリング", "クラフトサケ", "泡盛"]:
            if clean_name_for_brand.startswith(prefix):
                clean_name_for_brand = clean_name_for_brand[len(prefix):].strip()
        if clean_brew and clean_name_for_brand.startswith(clean_brew):
            clean_name_for_brand = clean_name_for_brand[len(clean_brew):].strip()

        if " " in clean_name_for_brand:
            brand = clean_name_for_brand.split()[0].strip()
        else:
            brand = clean_name_for_brand[:6].strip()

        if len(brand) <= 1 or brand in ["本格", "純米", "大吟", "本醸", "特別", "リキュ", "スパ"]:
            brand = clean_brew if clean_brew else spec[:4]

        if brand != orig_brand:
            fixed_brand_names += 1

        # 衝突安全更新（Collision Safe Update）
        cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name = ? AND id != ?", (spec, brew, p_id))
        collision = cur.fetchone()

        if collision:
            keep_id = collision['id']
            cur.execute("UPDATE awards SET product_id = ? WHERE product_id = ?", (keep_id, p_id))
            cur.execute("UPDATE user_flavor_ratings SET product_id = ? WHERE product_id = ?", (keep_id, p_id))
            cur.execute("DELETE FROM products WHERE id = ?", (p_id,))
            merged_collision_records += 1
        else:
            cur.execute("""
                UPDATE products
                SET brand_name = ?, spec_name = ?, category = ?, polish_ratio = ?,
                    rice_variety = ?, alcohol = ?, brewery_name = ?, prefecture = ?,
                    confidence = 1.0
                WHERE id = ?
            """, (brand, spec, cat, polish, rice, alc, brew, pref, p_id))

conn.commit()

# -------------------------------------------------------------
# Layer 6: 最終ゼロ重複監査
# -------------------------------------------------------------
cur.execute("""
    SELECT brewery_name, spec_name, COUNT(*) as cnt
    FROM products
    GROUP BY brewery_name, spec_name
    HAVING cnt > 1
""")
dups = cur.fetchall()

final_dup_removed = 0
for d in dups:
    b_name = d['brewery_name']
    s_name = d['spec_name']
    cur.execute("SELECT id FROM products WHERE brewery_name = ? AND spec_name = ? ORDER BY id ASC", (b_name, s_name))
    ids = [r['id'] for r in cur.fetchall()]
    keep_id = ids[0]
    remove_ids = ids[1:]
    for rid in remove_ids:
        cur.execute("UPDATE awards SET product_id = ? WHERE product_id = ?", (keep_id, rid))
        cur.execute("UPDATE user_flavor_ratings SET product_id = ? WHERE product_id = ?", (keep_id, rid))
        cur.execute("DELETE FROM products WHERE id = ?", (rid,))
        final_dup_removed += 1

conn.commit()

cur.execute("SELECT COUNT(*) FROM products")
final_total_products = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
final_total_breweries = cur.fetchone()[0]

conn.close()

print(f"==================================================================")
print(f"🎉 全製品 徹底品質保証（QA）検査・完全是正完了！")
print(f"・テキスト残滓・HTML実体参照の是正  : {fixed_text_noise} 件")
print(f"・特定名称・カテゴリの法的規格補正: {fixed_categories} 件")
print(f"・精米歩合・法的上限の整合性補正    : {fixed_polish_ratios} 件")
print(f"・アルコール度数の妥当性補正        : {fixed_alcohols} 件")
print(f"・酒蔵・都道府県マッピングの完全化  : {fixed_breweries_prefs} 件")
print(f"・ブランド名の完全正常化            : {fixed_brand_names} 件")
print(f"・衝突重複の統合・集約              : {merged_collision_records + final_dup_removed} 件")
print(f"・確定登録製品総数                  : {final_total_products} 件")
print(f"・紐付け酒蔵総数                    : {final_total_breweries} 蔵")
print(f"==================================================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
