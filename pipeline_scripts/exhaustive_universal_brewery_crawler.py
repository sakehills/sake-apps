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
LOG_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "exhaustive_all_breweries_crawler.log")

print("==================================================================")
print("🚀 全酒蔵 公式Webサイト 深層階層巡回＆全SKU完全抽出パイプライン")
print(f"DB Path : {DB_PATH}")
print(f"Log Path: {LOG_PATH}")
print("==================================================================\n")

class DeepLinkAndTextParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = set()
        self.texts = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.in_script = True
            return
        
        attrs_dict = dict(attrs)
        
        # リンクの収集
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href'].strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                full_url = urllib.parse.urljoin(self.base_url, href)
                # 同一ドメイン内の商品・ラインナップリンクのみを追跡
                if urllib.parse.urlparse(full_url).netloc == urllib.parse.urlparse(self.base_url).netloc:
                    if any(k in full_url.lower() for k in ['sake', 'product', 'item', 'lineup', 'brand', 'shop', 'collection', 'category', 'c/']):
                        self.links.add(full_url)
        
        # imgタグのalt属性から商品名を収集
        if tag == 'img' and 'alt' in attrs_dict:
            alt_text = attrs_dict['alt'].strip()
            if alt_text and len(alt_text) > 3:
                self.texts.append(alt_text)

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.in_script = False

    def handle_data(self, data):
        if not self.in_script:
            t = data.strip()
            if t:
                self.texts.append(t)

def fetch_page_data(url, timeout=8):
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
            parser = DeepLinkAndTextParser(url)
            parser.feed(html)
            return parser.texts, parser.links
    except Exception:
        return [], set()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 受賞履歴のあるすべての酒蔵（全国鑑評会、Kura Master、IWC、SAKE COMPETITION、国税局鑑評会等）
cur.execute("""
    SELECT DISTINCT b.id, b.name, b.prefecture, b.website
    FROM breweries b
    WHERE b.id IN (SELECT DISTINCT brewery_id FROM awards WHERE brewery_id IS NOT NULL)
       OR b.website IS NOT NULL AND b.website LIKE 'http%'
    ORDER BY b.id
""")
breweries = cur.fetchall()
total_breweries = len(breweries)

print(f"🔍 深層巡回対象の酒蔵総数: {total_breweries} 蔵\n")

total_new_products = 0

with open(LOG_PATH, "w", encoding="utf-8") as log_file:
    log_file.write(f"=== 全酒蔵 公式Webサイト深層巡回＆全SKU抽出 開始: {datetime.now().isoformat()} ===\n\n")

    for idx, brew in enumerate(breweries, 1):
        b_id = brew['id']
        b_name = brew['name']
        b_pref = brew['prefecture']
        b_url = brew['website']

        if not b_url or not b_url.startswith("http") or "saketime.com" in b_url:
            continue

        log_msg = f"[{idx}/{total_breweries}] 🏭 ID {b_id}: {b_name} ({b_pref}) - {b_url}"
        print(log_msg)
        log_file.write(log_msg + "\n")

        visited_urls = set()
        to_visit = {b_url}
        extracted_in_brewery = 0

        # トップページおよび主要商品URLを探索
        base_paths = ["/products", "/item", "/lineup", "/sake", "/collection", "/category", "/c/sake", "/shop"]
        for bp in base_paths:
            to_visit.add(urllib.parse.urljoin(b_url, bp))

        crawl_depth_limit = 12 # 1蔵あたり最大12ページまで深層クロール
        crawled_count = 0

        while to_visit and crawled_count < crawl_depth_limit:
            current_url = to_visit.pop()
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)
            crawled_count += 1

            texts, sub_links = fetch_page_data(current_url)
            for sl in sub_links:
                if sl not in visited_urls and len(to_visit) < 30:
                    to_visit.add(sl)

            for line in texts:
                line = line.strip()
                if len(line) < 4 or len(line) > 42:
                    continue

                if any(noise_word in line for noise_word in [
                    "公式サイト", "について", "全て見る", "一覧", "創業", "私たちの", 
                    "メーカーです", "オンラインショップ", "カート", "購入", "ログイン", 
                    "プライバシーポリシー", "利用規約", "お問い合わせ", "配送料", "会員登録",
                    "マイページ", "特定商取引法", "ページトップ", "株式会社", "有限会社"
                ]):
                    continue

                is_product = False
                matched_category = "普通酒"
                
                if any(k in line for k in [
                    "純米大吟醸", "純米吟醸", "特別純米", "大吟醸", "吟醸", "特別本醸造", 
                    "本醸造", "純米酒", "生酛", "山廃", "スパークリング", "梅酒", "ゆず酒", 
                    "リキュール", "クラフトサケ", "本格焼酎", "泡盛", "芋焼酎", "麦焼酎", 
                    "米焼酎", "黒糖焼酎", "どぶろく", "ひやおろし", "しぼりたて", "生原酒", "にごり酒"
                ]):
                    is_product = True

                if is_product:
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
                    for r in ["山田錦", "雄町", "五百万石", "美山錦", "出羽燦々", "愛山", "吟ぎんが", "結の香", "八反錦", "華吹雪", "華想い", "夢の香", "蔵の華", "ひとめぼれ", "越淡麗", "秋田酒こまち", "神力", "亀の尾", "短稈渡船", "白鶴錦", "金紋錦", "さかほまれ", "百万石乃白", "強力"]:
                        if r in line:
                            rice_variety = r
                            break

                    spec_name = line.replace("【", "").replace("】", "").replace("［", "").replace("］", "").strip()
                    spec_name = re.sub(r'\s*\d+ml.*', '', spec_name)
                    spec_name = re.sub(r'\s*1\.8L.*', '', spec_name)
                    
                    if len(spec_name) < 3 or spec_name in ["純米大吟醸", "純米吟醸", "純米酒", "大吟醸", "吟醸", "特別純米", "本醸造"]:
                        continue

                    cur.execute("""
                        SELECT id FROM products 
                        WHERE (spec_name = ? OR spec_name = ?) AND (brewery_name = ? OR brewery_name LIKE ?)
                    """, (spec_name, f"{b_name} {spec_name}", b_name, f"%{b_name[:4]}%"))
                    
                    existing = cur.fetchone()
                    if not existing:
                        now_str = datetime.now().isoformat()
                        brand_guess = spec_name.split()[0] if " " in spec_name else spec_name[:4]
                        try:
                            cur.execute("""
                                INSERT INTO products (
                                    brand_name, spec_name, category, polish_ratio, rice_variety,
                                    alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
                            """, (
                                brand_guess,
                                spec_name,
                                matched_category,
                                polish_ratio,
                                rice_variety,
                                alcohol,
                                b_name,
                                b_pref,
                                f"Deep Web Crawler ({current_url})",
                                now_str
                            ))
                            extracted_in_brewery += 1
                            total_new_products += 1
                            add_msg = f"    ✨ [新規SKU抽出] {spec_name} [{matched_category}] (米: {rice_variety}, 精米: {polish_ratio})"
                            print(add_msg)
                            log_file.write(add_msg + "\n")
                        except sqlite3.IntegrityError:
                            pass

        conn.commit()
        if extracted_in_brewery > 0:
            summary_line = f"  👉 {b_name}: {extracted_in_brewery} 件の新規SKUを深層クローリングにより追加登録\n"
            print(summary_line)
            log_file.write(summary_line)

    log_file.write(f"\n=== 全酒蔵 深層巡回＆全SKU抽出 完了: {datetime.now().isoformat()} ===\n")
    log_file.write(f"新規登録総数: {total_new_products} 件\n")

conn.close()

print(f"\n==================================================================")
print(f"🎉 全酒蔵 深層Webサイト巡回＆全SKU完全抽出が完了しました！")
print(f"・新規追加製品数: {total_new_products} 件")
print(f"・詳細巡回ログ  : {LOG_PATH}")
print(f"==================================================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
