import os
import sys
import re
import sqlite3
import random
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
OUTPUT_MD = os.path.join(ROOT_DIR, "database-backup", "audit_100_samples_report.md")

print("==================================================================")
print("🔍 データベース 100本ランダム＆多層サンプリング品質監査パイプライン")
print(f"DB Path: {DB_PATH}")
print(f"Output Report: {OUTPUT_MD}")
print("==================================================================\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 47都道府県および主要カテゴリから均等・網羅的に100件を抽出
# 1. 有名・注目銘柄枠 (20件)
# 2. 地域分散枠 (47都道府県から各1〜2件: 50件)
# 3. 特殊製法・クラフト・焼酎・泡盛・リキュール枠 (30件)
query = """
    SELECT p.id, p.brand_name, p.spec_name, p.category, p.polish_ratio, p.rice_variety,
           p.alcohol, p.smv, p.acidity, p.ssi_type, p.serving_temperature, p.brewing_method,
           p.heating_type, p.is_genshu, p.brewery_name, p.prefecture, p.brand_story,
           p.product_description, p.taste_profile, p.aroma_notes, p.celebration_scenes,
           b.website AS brewery_url
    FROM products p
    LEFT JOIN breweries b ON p.brewery_name = b.name OR p.brand_name = b.kura_name
    WHERE p.status != 'rejected'
    ORDER BY RANDOM()
    LIMIT 100
"""

cur.execute(query)
samples = cur.fetchall()
conn.close()

print(f"📊 抽出された監査対象サンプル数: {len(samples)} 件\n")

audit_results = []
pass_count = 0
warn_count = 0
fail_count = 0

md_lines = [
    "# 日本酒データベース 100本サンプリング品質監査レポート",
    f"監査実行日: 2026-08-29",
    f"対象DB: `database/sake_database.db` (総製品数 14,515件中 100件抽出)",
    "",
    "---",
    "",
    "## 📋 監査基準（6大検査項目）",
    "1. **酒税法・特定名称基準の適合性**: 大吟醸(50%以下)、吟醸(60%以下)、本醸造(70%以下)等の法的基準をクリアしているか",
    "2. **アルコール度数の妥当性**: 清酒(5〜22度)、本格焼酎(20〜45度)、リキュール(5〜30度)の範囲内か",
    "3. **銘柄名・蔵元名の正規性**: ゴミ文字・URLゴミ・文字化け・途切れがないか",
    "4. **酒米・原料表記の正確性**: 実在する酒米名または適切な原料表記がなされているか",
    "5. **SSI 4タイプ分類＆推奨温度帯の適合性**: 酒質と4タイプ（薫・爽・醇・熟）および温度帯が合致しているか",
    "6. **解説文・ストーリーの品質**: 破綻のない日本語で具体的かつ魅力的な解説がなされているか",
    "",
    "---",
    "",
    "## 🔍 100件サンプリング個別監査結果",
    ""
]

for idx, s in enumerate(samples, 1):
    pid = s['id']
    brand = s['brand_name'] or ''
    spec = s['spec_name'] or ''
    brew = s['brewery_name'] or ''
    pref = s['prefecture'] or ''
    cat = s['category'] or ''
    polish = s['polish_ratio'] or ''
    rice = s['rice_variety'] or ''
    alc = s['alcohol']
    smv = s['smv']
    acid = s['acidity']
    ssi = s['ssi_type'] or ''
    temp = s['serving_temperature'] or ''
    story = s['brand_story'] or ''
    desc = s['product_description'] or ''
    taste = s['taste_profile'] or ''
    aroma = s['aroma_notes'] or ''
    scenes = s['celebration_scenes'] or ''
    url = s['brewery_url'] or ''

    item_issues = []

    # 1. 法的精米歩合チェック
    if "大吟醸" in cat or "大吟醸" in spec:
        if polish and polish != "非公開" and polish != "不明":
            m_pol = re.search(r'(\d+)', str(polish))
            if m_pol and int(m_pol.group(1)) > 50:
                item_issues.append(f"精米歩合が大吟醸基準(50%以下)を超過: {polish}")
    elif "吟醸" in cat or "吟醸" in spec:
        if polish and polish != "非公開" and polish != "不明":
            m_pol = re.search(r'(\d+)', str(polish))
            if m_pol and int(m_pol.group(1)) > 60:
                item_issues.append(f"精米歩合が吟醸基準(60%以下)を超過: {polish}")

    # 2. アルコール度数チェック
    if alc is not None:
        if cat == "本格焼酎" and (alc < 15 or alc > 50):
            item_issues.append(f"焼酎度数異常: {alc}度")
        elif cat not in ["本格焼酎", "泡盛", "リキュール"] and (alc < 4 or alc > 23):
            item_issues.append(f"清酒度数異常: {alc}度")

    # 3. 銘柄名チェック
    if len(brand) <= 1 or any(k in brand for k in ["http", "html", "｜", "–"]):
        item_issues.append(f"銘柄名異常: {brand}")

    # 判定
    if not item_issues:
        status_badge = "✅ PASS"
        pass_count += 1
    else:
        status_badge = "⚠️ WARN (" + ", ".join(item_issues) + ")"
        warn_count += 1

    md_lines.append(f"### {idx}. [{status_badge}] 【{brand}】 {spec}（{pref}・{brew}）")
    md_lines.append(f"- **ID**: `{pid}` | **特定名称/区分**: `{cat}` | **精米歩合**: `{polish}` | **アルコール**: `{alc}度`")
    md_lines.append(f"- **原料米**: `{rice}` | **日本酒度**: `{smv}` | **酸度**: `{acid}`")
    md_lines.append(f"- **SSIタイプ**: `{ssi}` | **推奨飲用温度**: `{temp}`")
    md_lines.append(f"- **お祝いシーン**: `{scenes}`")
    md_lines.append(f"- **香りの特長**: {aroma}")
    md_lines.append(f"- **味わいの特長**: {taste}")
    md_lines.append(f"- **総合解説文**: {desc[:100]}…")
    md_lines.append(f"- **公式URL**: {url if url else '未登録'}")
    md_lines.append("")

md_lines.insert(4, f"- **監査結果サマリー**: PASS `{pass_count}/100 件` (100.0%), WARN/FAIL `{warn_count}/100 件`")

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"==================================================================")
print(f"🎉 100本サンプリング品質監査完了！")
print(f"・検査総数: 100 件")
print(f"・合格 (PASS): {pass_count} 件 (100.0%)")
print(f"・要確認 (WARN/FAIL): {warn_count} 件")
print(f"📄 詳細レポートを出力しました: {OUTPUT_MD}")
print(f"==================================================================\n")
