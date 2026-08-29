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
LOG_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "exhaustive_all_breweries_crawler.log")

print("=== 🔄 クロールログからの全製品SKU 徹底精密復元＆ブランド名・スペック適正化 ===")
print(f"DB Path : {DB_PATH}")
print(f"Log Path: {LOG_PATH}\n")

# 1. ログファイルから全抽出SKUをパース
extracted_items = []
current_brewery = ""
current_pref = ""
current_url = ""

if not os.path.exists(LOG_PATH):
    print("❌ クロールログファイルが見つかりません。")
    sys.exit(1)

with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        if "🏭 ID" in line:
            m = re.search(r'ID \d+:\s*(.*?)\s*\((.*?)\)\s*-\s*(http.*)', line)
            if m:
                current_brewery = m.group(1).strip()
                current_pref = m.group(2).strip()
                current_url = m.group(3).strip()
        elif "✨ [新規SKU抽出]" in line:
            # ✨ [新規SKU抽出] 神渡　純米大吟醸　箱入 [純米大吟醸酒] (米: 国産米, 精米: 非公開)
            m = re.search(r'✨ \[新規SKU抽出\] (.*?) \[(.*?)\] \(米:\s*(.*?), 精米:\s*(.*?)\)', line)
            if m:
                spec_raw = m.group(1).strip()
                cat = m.group(2).strip()
                rice = m.group(3).strip()
                polish = m.group(4).strip()
                if current_brewery:
                    extracted_items.append({
                        "brewery": current_brewery,
                        "pref": current_pref,
                        "url": current_url,
                        "spec": spec_raw,
                        "cat": cat,
                        "rice": rice,
                        "polish": polish
                    })

print(f"📄 クロールログから解析された全レコード数: {len(extracted_items)} 件")

# ノイズ・グッズ・ナビゲーション用語の判定
NOISE_PATTERNS = [
    "ガイド", "徹底解説", "前掛", "腹巻", "平盃", "石鹸", "チョコ", "グラス", "Tシャツ", "タオル",
    "数量を増やす", "数量を減らす", "無料", "税込", "円", "参加！！", "予約開始", "発売中！",
    "掲載いただきました", "取り上げていただきました", "受賞いたしました", "選出されました",
    "登場！", "のお知らせ", "製造断念", "紹介されました", "ご案内", "おすすめの", "ですか？",
    "お悩み", "常識を覆す", "とは？", "見る", "検索結果", "の部", "部門", "賞", "トロフィー",
    "チャレンジ", "大会", "コンテスト", "コンクール", "鑑評会", "開催", "仕込み中", "上槽",
    "出荷開始", "販売開始", "登場", "新発売", "新登場", "NEWS", "ニュース", "ブログ", "イベント",
    "概要", "ヒミツ", "祭り", "休売", "おすすめ", "ぜひ", "お楽しみ", "特徴的", "素晴らしい",
    "こだわり", "丁寧", "仕込み水を加え", "アルコール度数を抑えた", "酒粕", "粕",
    "カート", "ログイン", "購入", "プライバシーポリシー", "利用規約", "お問い合わせ", "配送料",
    "会員登録", "マイページ", "特定商取引法", "ページトップ"
]

def is_noise(text):
    if len(text) < 3 or len(text) > 45:
        return True
    if text.endswith(("です。", "ます。", "でした。", "ください。", "になります。", "ございます。")):
        return True
    return any(np in text for np in NOISE_PATTERNS)

# ブランド名の精密抽出
def extract_clean_brand(spec, brew):
    s = spec
    clean_brew = brew.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").replace("合同会社", "").strip()
    
    # プレフィックスの剥ぎ取り
    for pref in [
        "本格芋焼酎", "本格麦焼酎", "本格米焼酎", "本格黒糖焼酎", "本格そば焼酎", "本格焼酎",
        "芋焼酎", "麦焼酎", "米焼酎", "黒糖焼酎", "そば焼酎", "琉球泡盛", "泡盛",
        "純米大吟醸酒", "純米大吟醸", "純米吟醸酒", "純米吟醸", "特別純米酒", "特別純米",
        "大吟醸酒", "大吟醸", "吟醸酒", "吟醸", "特別本醸造酒", "特別本醸造", "本醸造酒", "本醸造",
        "純米酒", "純米", "普通酒", "スパークリング日本酒", "スパークリング",
        "クラフトサケ", "クラフトどぶろく", "どぶろく", "リキュール", "果実酒", "梅酒", "ゆず酒",
        "無濾過生原酒", "生原酒", "生酒", "原酒", "にごり酒", "ひやおろし", "しぼりたて", "初しぼり", "秋あがり"
    ]:
        if s.startswith(pref):
            s = s[len(pref):].strip()

    if clean_brew and s.startswith(clean_brew):
        s = s[len(clean_brew):].strip()

    if " " in s:
        b = s.split()[0].strip()
    elif "　" in s:
        b = s.split("　")[0].strip()
    else:
        b = s[:6].strip()

    if len(b) <= 1 or b in ["本格", "純米", "大吟", "本醸", "特別", "リキュ", "スパ"]:
        b = clean_brew if clean_brew else spec[:4]

    return b

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

now_str = subprocess.check_output([sys.executable, "-c", "from datetime import datetime; print(datetime.now().isoformat())"]).decode().strip()

valid_restored = 0
skipped_noise = 0

for item in extracted_items:
    raw_spec = item['spec']
    # HTMLタグや特殊文字のクレンジング
    clean_spec = raw_spec.replace('<br />', ' ').replace('<br>', ' ').replace('&nbsp;', ' ').replace('　', ' ')
    clean_spec = " ".join(clean_spec.split()).strip()

    if is_noise(clean_spec):
        skipped_noise += 1
        continue

    # アルコール度数の推定
    alc_match = re.search(r'(\d{1,2}(?:\.\d+)?)度', clean_spec)
    if alc_match:
        alc = float(alc_match.group(1))
    elif item['cat'] in ['本格焼酎', '泡盛']:
        alc = 25.0
    elif item['cat'] == 'リキュール':
        alc = 10.0
    else:
        alc = 15.0

    brand = extract_clean_brand(clean_spec, item['brewery'])

    # 厳格な重複チェック（同一蔵＋同一スペック名）
    cur.execute("""
        SELECT id FROM products 
        WHERE spec_name = ? AND brewery_name = ?
    """, (clean_spec, item['brewery']))
    
    existing = cur.fetchone()
    if not existing:
        try:
            cur.execute("""
                INSERT INTO products (
                    brand_name, spec_name, category, polish_ratio, rice_variety,
                    alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
            """, (
                brand,
                clean_spec,
                item['cat'],
                item['polish'],
                item['rice'],
                alc,
                item['brewery'],
                item['pref'],
                f"Exhaustive Crawler Verified ({item['url']})",
                now_str
            ))
            valid_restored += 1
        except sqlite3.IntegrityError:
            pass

conn.commit()

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
total_brews = cur.fetchone()[0]

conn.close()

print(f"\n==========================================")
print(f"🎉 全銘柄SKU 精密復元＆再構築 結果:")
print(f"・新規復元・追加された正規製品数: {valid_restored} 件")
print(f"・除外されたノイズ件数          : {skipped_noise} 件")
print(f"・データベース最終登録製品総数  : {total_prods} 件")
print(f"・紐付け酒蔵総数                : {total_brews} 蔵")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
