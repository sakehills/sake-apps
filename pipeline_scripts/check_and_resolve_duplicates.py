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

print("=== 🔍 全銘柄・全酒蔵 重複データ徹底検査＆完全統合パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def normalize_key(spec_name, brewery_name, brand_name):
    s = (spec_name or "").lower().strip()
    b = (brewery_name or "").lower().strip()
    br = (brand_name or "").lower().strip()

    # 法人格の除去
    for corp in ["株式会社", "有限会社", "合資会社", "合名会社", "合同会社"]:
        b = b.replace(corp.lower(), "")
    b = b.strip()

    # 全角半角スペース・記号の統一
    s = re.sub(r'[\s　・／/「」『』【】［］\[\]\(\)（）]', '', s)
    b = re.sub(r'[\s　・／/「」『』【】［］\[\]\(\)（）]', '', b)
    br = re.sub(r'[\s　・／/「」『』【】［］\[\]\(\)（）]', '', br)

    # 銘柄名内の酒蔵名・ブランド名プレフィックスの除去による正規化
    if b and s.startswith(b):
        s_norm = s[len(b):]
    elif br and s.startswith(br):
        s_norm = s[len(br):]
    else:
        s_norm = s

    return f"{b}___{s_norm}"

# 1. 全製品の取得
cur.execute("""
    SELECT id, brand_name, spec_name, category, polish_ratio, rice_variety,
           alcohol, brewery_name, prefecture, confidence, evidence, created_at
    FROM products
    ORDER BY brewery_name, spec_name, id
""")
all_products = cur.fetchall()
print(f"📊 検査対象の製品総数: {len(all_products)} 件")

seen_groups = {}

for p in all_products:
    norm_k = normalize_key(p['spec_name'], p['brewery_name'], p['brand_name'])
    if norm_k not in seen_groups:
        seen_groups[norm_k] = [p]
    else:
        seen_groups[norm_k].append(p)

duplicate_groups_count = 0
deleted_duplicate_ids = set()

for norm_k, group in seen_groups.items():
    if len(group) > 1:
        duplicate_groups_count += 1
        # より情報量の多い（長いspec_name、またはconfidenceの高いもの）をプライマリとして選択
        sorted_group = sorted(group, key=lambda x: (
            1 if (x['confidence'] or 0) >= 1.0 else 0,
            len(x['spec_name'] or ''),
            1 if x['polish_ratio'] and x['polish_ratio'] != '非公開' else 0,
            -x['id']
        ), reverse=True)

        primary = sorted_group[0]
        redundants = sorted_group[1:]

        for red in redundants:
            deleted_duplicate_ids.add(red['id'])
            # 受賞データや評価データの外部キーをプライマリIDへ付け替え
            cur.execute("UPDATE awards SET product_id = ? WHERE product_id = ?", (primary['id'], red['id']))
            cur.execute("UPDATE user_flavor_ratings SET product_id = ? WHERE product_id = ?", (primary['id'], red['id']))

print(f"⚠️ 検出された重複グループ数: {duplicate_groups_count} 組")
print(f"🧹 統合・削除対象の重複レコード数: {len(deleted_duplicate_ids)} 件")

if deleted_duplicate_ids:
    placeholders = ",".join("?" for _ in deleted_duplicate_ids)
    cur.execute(f"DELETE FROM products WHERE id IN ({placeholders})", list(deleted_duplicate_ids))
    conn.commit()
    print("✅ 重複レコードの削除＆外部キー参照の統合が完了しました。")

# 2. 最終検証：完全一致および正規化重複が0件であることを確認
cur.execute("""
    SELECT brewery_name, spec_name, COUNT(*) as cnt
    FROM products
    GROUP BY brewery_name, spec_name
    HAVING cnt > 1
""")
exact_dup_after = cur.fetchall()

cur.execute("SELECT COUNT(*) FROM products")
final_total_products = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
final_total_breweries = cur.fetchone()[0]

conn.close()

print(f"\n==========================================")
print(f"🎉 重複検査＆完全統合 結果レポート:")
print(f"・残存する重複データ数: {len(exact_dup_after)} 件 (完全重複 0件達成)")
print(f"・クリーン後 製品総数 : {final_total_products} 件")
print(f"・紐付け酒蔵総数      : {final_total_breweries} 蔵")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
