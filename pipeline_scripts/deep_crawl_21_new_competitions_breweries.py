import os
import sys
import re
import json
import sqlite3
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
LOG_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "crawler_21_new_breweries.log")

print("==================================================================")
print("🚀 新規4コンペ受賞 21酒蔵 公式Webサイト完全巡回・全件自動抽出ループ開始")
print(f"DB Path : {DB_PATH}")
print(f"Log Path: {LOG_PATH}")
print("==================================================================\n")

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_script = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.in_script = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.in_script = False
    def handle_data(self, data):
        if not self.in_script:
            text = data.strip()
            if text:
                self.result.append(text)
    def get_text(self):
        return "\n".join(self.result)

def fetch_url_text(url, timeout=10):
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            charset = 'utf-8'
            if b'charset=euc-jp' in content.lower():
                charset = 'euc-jp'
            elif b'charset=shift_jis' in content.lower() or b'charset=sjis' in content.lower() or b'charset=cp932' in content.lower():
                charset = 'cp932'
            
            html = content.decode(charset, errors='replace')
            parser = HTMLTextExtractor()
            parser.feed(html)
            return parser.get_text(), html
    except Exception as e:
        return None, str(e)

PRODUCT_PATH_CANDIDATES = [
    "",
    "/products",
    "/products/",
    "/item",
    "/item/",
    "/lineup",
    "/lineup/",
    "/sake",
    "/sake/",
    "/collection",
    "/collection/",
    "/brand",
    "/brand/",
    "/product-category/sake/",
    "/shop",
    "/shop/",
    "/brew/",
    "/items/"
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 4大コンペ受賞全21蔵元を取得
cur.execute("""
    SELECT DISTINCT b.id, b.name, b.prefecture, b.website
    FROM breweries b
    JOIN awards a ON a.brewery_id = b.id
    WHERE a.competition_id IN (10037, 10044, 10045, 10046, 10047)
    ORDER BY b.id
""")
breweries = cur.fetchall()
total_breweries = len(breweries)

print(f"🔍 巡回対象の酒蔵数: {total_breweries} 蔵\n")

total_new_products = 0

with open(LOG_PATH, "w", encoding="utf-8") as log_file:
    log_file.write(f"=== 新規4大コンペ受賞 21酒蔵 公式Webサイト巡回ログ 開始: {datetime.now().isoformat()} ===\n\n")

    for idx, brew in enumerate(breweries, 1):
        b_id = brew['id']
        b_name = brew['name']
        b_pref = brew['prefecture']
        b_url = brew['website']
        
        log_msg = f"[{idx}/{total_breweries}] ID {b_id}: {b_name} ({b_pref}) - URL: {b_url}"
        print(log_msg)
        log_file.write(log_msg + "\n")

        if not b_url or not b_url.startswith("http"):
            continue

        base_url = b_url.rstrip("/")
        visited_pages = set()
        extracted_in_brewery = 0

        for path in PRODUCT_PATH_CANDIDATES:
            target_url = base_url + path
            if target_url in visited_pages:
                continue
            visited_pages.add(target_url)

            text, raw_html = fetch_url_text(target_url, timeout=8)
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if len(line) < 4 or len(line) > 45:
                    continue

                # ノイズ語の除外
                if any(noise_word in line for noise_word in [
                    "公式サイト", "について", "全て見る", "一覧", "創業", "私たちの", 
                    "メーカーです", "オンラインショップ", "カート", "購入", "ログイン", "プライバシーポリシー"
                ]):
                    continue

                is_product_match = False
                matched_category = "普通酒"
                
                if any(k in line for k in [
                    "純米大吟醸", "純米吟醸", "特別純米", "大吟醸", "吟醸", "特別本醸造", 
                    "本醸造", "純米酒", "生酛", "山廃", "スパークリング", "梅酒", "ゆず酒", 
                    "リキュール", "クラフトサケ", "本格焼酎", "泡盛", "芋焼酎", "麦焼酎", 
                    "米焼酎", "黒糖焼酎", "どぶろく", "ひやおろし", "しぼりたて", "生原酒", "にごり酒"
                ]):
                    is_product_match = True

                if is_product_match:
                    if "純米大吟醸" in line: matched_category = "純米大吟醸酒"
                    elif "純米吟醸" in line: matched_category = "純米吟醸酒"
                    elif "特別純米" in line: matched_category = "特別純米酒"
                    elif "大吟醸" in line: matched_category = "大吟醸酒"
                    elif "吟醸" in line: matched_category = "吟醸酒"
                    elif "特別本醸造" in line: matched_category = "特別本醸造酒"
                    elif "本醸造" in line: matched_category = "本醸造酒"
                    elif "純米" in line: matched_category = "純米酒"
                    elif "梅酒" in line or "リキュール" in line or "ゆず" in line: matched_category = "リキュール"
                    elif "泡盛" in line: matched_category = "泡盛"
                    elif "焼酎" in line: matched_category = "本格焼酎"
                    elif "クラフトサケ" in line: matched_category = "クラフトサケ"
                    elif "どぶろく" in line: matched_category = "どぶろく"

                    polish_match = re.search(r'(\d{1,2})%', line)
                    polish_ratio = f"{polish_match.group(1)}%" if polish_match else "非公開"

                    alc_match = re.search(r'(\d{1,2}(?:\.\d+)?)度', line)
                    alcohol = float(alc_match.group(1)) if alc_match else 15.0

                    rice_variety = "国産米"
                    for r in ["山田錦", "雄町", "五百万石", "美山錦", "出羽燦々", "愛山", "吟ぎんが", "結の香", "八反錦", "華吹雪", "華想い", "夢の香", "蔵の華", "ひとめぼれ", "越淡麗", "秋田酒こまち", "神力", "亀の尾", "短稈渡船", "白鶴錦", "金紋錦", "さかほまれ", "百万石乃白"]:
                        if r in line:
                            rice_variety = r
                            break

                    spec_name = line.replace("【", "").replace("】", "").replace("［", "").replace("］", "").strip()
                    
                    cur.execute("""
                        SELECT id FROM products 
                        WHERE spec_name = ? AND brewery_name = ?
                    """, (spec_name, b_name))
                    
                    existing = cur.fetchone()
                    if not existing:
                        now_str = datetime.now().isoformat()
                        try:
                            cur.execute("""
                                INSERT INTO products (
                                    brand_name, spec_name, category, polish_ratio, rice_variety,
                                    alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
                            """, (
                                spec_name.split()[0] if " " in spec_name else spec_name[:6],
                                spec_name,
                                matched_category,
                                polish_ratio,
                                rice_variety,
                                alcohol,
                                b_name,
                                b_pref,
                                f"Official Web Crawler ({target_url})",
                                now_str
                            ))
                            extracted_in_brewery += 1
                            total_new_products += 1
                            add_msg = f"    ✨ [新規銘柄抽出] {spec_name} ({matched_category})"
                            print(add_msg)
                            log_file.write(add_msg + "\n")
                        except sqlite3.IntegrityError:
                            pass

        conn.commit()
        summary_line = f"  👉 {b_name}: {extracted_in_brewery} 件の新規製品を公式Webから自動抽出・登録完了\n"
        print(summary_line)
        log_file.write(summary_line)

    log_file.write(f"\n=== 21酒蔵 公式Webサイト巡回 完了: {datetime.now().isoformat()} ===\n")
    log_file.write(f"新規登録総数: {total_new_products} 件\n")

conn.close()

print(f"\n==================================================================")
print(f"🎉 新規4コンペ受賞 21酒蔵 公式Webサイト完全巡回・自動抽出が完了しました！")
print(f"・新規追加製品数: {total_new_products} 件")
print(f"・詳細巡回ログ  : {LOG_PATH}")
print(f"==================================================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
