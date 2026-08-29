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

LOG_FILES = [
    os.path.join(ROOT_DIR, "pipeline_scripts", "crawler_110_breweries.log"),
    os.path.join(ROOT_DIR, "pipeline_scripts", "crawler_21_new_breweries.log"),
    os.path.join(ROOT_DIR, "pipeline_scripts", "crawler_tax_bureau_breweries.log"),
    os.path.join(ROOT_DIR, "pipeline_scripts", "exhaustive_all_breweries_crawler.log")
]

print("=== 🔍 過去の全クロールログ・全削除レコード 網羅的徹底監査 ===")
print(f"DB Path: {DB_PATH}\n")

all_historical_extracted = []

for log_path in LOG_FILES:
    if not os.path.exists(log_path):
        continue
    print(f"📖 ログファイル解析中: {os.path.basename(log_path)}")
    current_brew = ""
    current_pref = ""
    current_url = ""
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "ID " in line and ("[" in line or "🏭" in line):
                m = re.search(r'ID \d+:\s*(.*?)\s*\((.*?)\)(?:\s*-\s*(http.*))?', line)
                if m:
                    current_brew = m.group(1).strip()
                    current_pref = m.group(2).strip()
                    current_url = m.group(3).strip() if m.group(3) else ""
            elif "✨ [新規" in line:
                # ✨ [新規銘柄抽出] 銘柄名 (カテゴリ)
                # ✨ [新規SKU抽出] 銘柄名 [カテゴリ] (米: ..., 精米: ...)
                m1 = re.search(r'✨ \[新規銘柄抽出\] (.*?) \((.*?)\)', line)
                m2 = re.search(r'✨ \[新規SKU抽出\] (.*?) \[(.*?)\]', line)
                if m1:
                    spec_raw = m1.group(1).strip()
                    cat = m1.group(2).strip()
                    if current_brew:
                        all_historical_extracted.append((current_brew, current_pref, spec_raw, cat, current_url, os.path.basename(log_path)))
                elif m2:
                    spec_raw = m2.group(1).strip()
                    cat = m2.group(2).strip()
                    if current_brew:
                        all_historical_extracted.append((current_brew, current_pref, spec_raw, cat, current_url, os.path.basename(log_path)))

print(f"📊 過去の全クロールログから発見された総抽出レコード数: {len(all_historical_extracted)} 件\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 現在DBに登録されている銘柄のセット
cur.execute("SELECT brewery_name, spec_name FROM products")
current_db_items = set()
for r in cur.fetchall():
    current_db_items.add((r['brewery_name'], r['spec_name']))

# 過去ログにあり、現在DBに存在しない銘柄の分類
missing_legitimate_products = []
missing_noise_items = []

NOISE_CHECK = [
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
    "会員登録", "マイページ", "特定商取引法", "ページトップ", "完売", "(0件)"
]

GENERIC_NAMES = [
    '大吟醸', '純米大吟醸', '純米吟醸', '特別純米', '特別純米酒', '純米酒',
    '吟醸', '吟醸酒', '本醸造', '本醸造酒', '特別本醸造', '特別本醸造酒',
    '普通酒', 'リキュール', '本格焼酎', '泡盛', 'スパークリング', 'にごり酒',
    'しぼりたて', 'ひやおろし', '生酒', '原酒', '生原酒', '無濾過生原酒',
    '大吟醸酒', '純米大吟醸酒', '純米吟醸酒', 'クラフトサケ', 'どぶろく',
    '本格芋焼酎', '本格麦焼酎', '本格米焼酎'
]

seen_missing = set()

for brew, pref, spec, cat, url, log_source in all_historical_extracted:
    clean_s = spec.replace('<br />', ' ').replace('<br>', ' ').replace('&nbsp;', ' ').replace('　', ' ')
    clean_s = " ".join(clean_s.split()).strip()

    if (brew, clean_s) in current_db_items:
        continue
    
    dedup_k = (brew, clean_s)
    if dedup_k in seen_missing:
        continue
    seen_missing.add(dedup_k)

    # ノイズ判定
    is_noise_flag = False
    if clean_s in GENERIC_NAMES or len(clean_s) < 3 or len(clean_s) > 48:
        is_noise_flag = True
    elif clean_s.endswith(("です。", "ます。", "でした。", "ください。", "になります。", "ございます。")):
        is_noise_flag = True
    elif any(nc in clean_s for nc in NOISE_CHECK):
        is_noise_flag = True

    if is_noise_flag:
        missing_noise_items.append((brew, pref, clean_s, cat, log_source))
    else:
        missing_legitimate_products.append((brew, pref, clean_s, cat, url, log_source))

print(f"【監査結果】")
print(f"1. 過去に抽出されたが現在未登録の「正当な銘柄候補」: {len(missing_legitimate_products)} 件")
print(f"2. 削除・除外された「ノイズ・ブログ・解説文テキスト」: {len(missing_noise_items)} 件\n")

# 正当な銘柄候補をDBへ復元登録
now_str = subprocess.check_output([sys.executable, "-c", "from datetime import datetime; print(datetime.now().isoformat())"]).decode().strip()

restored_count = 0
for brew, pref, spec, cat, url, log_source in missing_legitimate_products:
    alc = 25.0 if cat in ['本格焼酎', '泡盛'] else (10.0 if cat == 'リキュール' else 15.0)
    brand_guess = spec.split()[0] if " " in spec else spec[:6]
    
    try:
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
            ) VALUES (?, ?, ?, '非公開', '国産米', ?, ?, ?, 1.0, ?, ?, 'active')
        """, (brand_guess, spec, cat, alc, brew, pref, f"Historical Log Restoration ({log_source})", now_str))
        restored_count += 1
    except sqlite3.IntegrityError:
        pass

conn.commit()

cur.execute("SELECT COUNT(*) FROM products")
total_prods = cur.fetchone()[0]

conn.close()

print(f"✨ 過去全ログから正当銘柄として復元登録完了: {restored_count} 件")
print(f"🍶 最終登録製品総数: {total_prods} 件\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
