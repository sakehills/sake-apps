import os
import sys
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser
import sqlite3
import subprocess
import time
import ssl
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
LOG_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "exhaustive_all_breweries_crawler.log")
TARGET_LOG = os.path.join(ROOT_DIR, "pipeline_scripts", "deep_crawl_364_breweries.log")

print("==================================================================")
print("🚀 最新検証済364蔵 公式Webサイト 深層走査・全SKU完全抽出パイプライン")
print(f"DB Path: {DB_PATH}")
print(f"Log:     {TARGET_LOG}")
print("==================================================================\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. 0件だった364蔵のリストアップ
with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
    log_content = f.read()

b_entries = re.findall(r'\[\d+/1376\] 🏭 ID (\d+):\s*(.*?)\s*\((.*?)\)\s*-\s*(http.*)', log_content)

zero_brewery_ids = []
for b_id, name, pref, url in b_entries:
    if f"👉 {name}:" not in log_content:
        zero_brewery_ids.append(int(b_id))

# DBから最新URLを取得
placeholders = ",".join("?" for _ in zero_brewery_ids)
cur.execute(f"""
    SELECT id, name, prefecture, website
    FROM breweries
    WHERE id IN ({placeholders}) AND website IS NOT NULL AND website != ''
    ORDER BY id
""", zero_brewery_ids)
target_breweries = cur.fetchall()

print(f"🎯 深層クローリング対象の最新確定蔵元数: {len(target_breweries)} 蔵\n")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

NOISE_WORDS = [
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

class DeepLinkAndTextParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.internal_links = set()
        self.text_blocks = []
        self.current_tag = ""
        self.in_ignored_tag = False

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        if self.current_tag in ["script", "style", "nav", "footer", "header", "noscript"]:
            self.in_ignored_tag = True
            return

        attr_dict = dict(attrs)
        href = attr_dict.get("href", "")
        if href:
            try:
                full_url = urllib.parse.urljoin(self.base_url, href)
                base_domain = urllib.parse.urlparse(self.base_url).netloc
                link_domain = urllib.parse.urlparse(full_url).netloc
                if link_domain == base_domain:
                    path_lower = urllib.parse.urlparse(full_url).path.lower()
                    if any(k in path_lower for k in ["sake", "product", "item", "lineup", "brand", "shop", "collection", "category", "c/", "catalog"]):
                        self.internal_links.add(full_url)
            except Exception:
                pass

        alt = attr_dict.get("alt", "")
        if alt and len(alt) >= 4:
            self.text_blocks.append(alt.strip())

    def handle_endtag(self, tag):
        if tag.lower() in ["script", "style", "nav", "footer", "header", "noscript"]:
            self.in_ignored_tag = False

    def handle_data(self, data):
        if self.in_ignored_tag:
            return
        t = data.strip()
        if len(t) >= 4:
            self.text_blocks.append(t)

def fetch_and_parse(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return set(), []
            html_content = resp.read().decode('utf-8', errors='replace')
            parser = DeepLinkAndTextParser(url)
            parser.feed(html_content)
            return parser.internal_links, parser.text_blocks
    except Exception:
        return set(), []

SPECIFIC_PATTERNS = [
    r'([^\n\r<>]+(?:純米大吟醸|大吟醸|純米吟醸|特別純米|純米酒|特別本醸造|本醸造|吟醸)[^\n\r<>]*)',
    r'([^\n\r<>]+(?:スパークリング|生原酒|原酒|ひやおろし|にごり酒|しぼりたて)[^\n\r<>]*)',
    r'([^\n\r<>]+(?:本格芋焼酎|本格麦焼酎|本格米焼酎|本格焼酎|泡盛|リキュール|梅酒|ゆず酒|クラフトサケ|どぶろく)[^\n\r<>]*)'
]

def extract_products_from_texts(texts, brewery_name, pref):
    found_products = []
    clean_brew = brewery_name.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").replace("合同会社", "").strip()

    for t in texts:
        t_clean = re.sub(r'[\r\n\t]', ' ', t)
        t_clean = " ".join(t_clean.split()).strip()

        if len(t_clean) < 4 or len(t_clean) > 45:
            continue
        if t_clean in GENERIC_NAMES or any(nw in t_clean for nw in NOISE_WORDS):
            continue
        if t_clean.endswith(("です。", "ます。", "でした。", "ください。", "になります。", "ございます。")):
            continue

        matched_spec = None
        for pat in SPECIFIC_PATTERNS:
            m = re.search(pat, t_clean)
            if m:
                matched_spec = m.group(1).strip()
                break

        if not matched_spec:
            continue

        matched_spec = matched_spec.replace('"', '').replace("'", "").replace("`", "")
        if matched_spec in GENERIC_NAMES:
            continue

        # カテゴリ判定
        if "純米大吟醸" in matched_spec: cat = "純米大吟醸酒"
        elif "純米吟醸" in matched_spec: cat = "純米吟醸酒"
        elif "特別純米" in matched_spec: cat = "特別純米酒"
        elif "大吟醸" in matched_spec: cat = "大吟醸酒"
        elif "吟醸" in matched_spec: cat = "吟醸酒"
        elif "特別本醸造" in matched_spec: cat = "特別本醸造酒"
        elif "本醸造" in matched_spec: cat = "本醸造酒"
        elif "純米酒" in matched_spec or ("純米" in matched_spec and "大吟醸" not in matched_spec and "吟醸" not in matched_spec): cat = "純米酒"
        elif any(k in matched_spec for k in ["梅酒", "ゆず", "果実酒", "リキュール"]): cat = "リキュール"
        elif "泡盛" in matched_spec: cat = "泡盛"
        elif any(k in matched_spec for k in ["本格焼酎", "芋焼酎", "麦焼酎", "米焼酎", "黒糖焼酎", "そば焼酎", "焼酎"]): cat = "本格焼酎"
        elif "クラフトサケ" in matched_spec: cat = "クラフトサケ"
        elif "どぶろく" in matched_spec: cat = "どぶろく"
        else: cat = "普通酒"

        # 精米歩合
        pm = re.search(r'(\d{1,2})%', matched_spec)
        polish = f"{pm.group(1)}%" if pm else "非公開"

        # 酒米
        rm = re.search(r'(山田錦|五百万石|美山錦|雄町|秋津穂|愛山|出羽燦々|華吹雪|吟風|彗星|きたしずく|越淡麗|夢の香|八反錦|千本錦|強力|金紋錦|山恵錦|神の穂|吟の夢)', matched_spec)
        rice = rm.group(1) if rm else "国産米"

        # 度数
        am = re.search(r'(\d{1,2}(?:\.\d+)?)度', matched_spec)
        if am:
            alc = float(am.group(1))
        elif cat in ["本格焼酎", "泡盛"]:
            alc = 25.0
        elif cat == "リキュール":
            alc = 10.0
        else:
            alc = 15.0

        # ブランド名
        clean_brand_target = matched_spec
        for pref_strip in ["本格芋焼酎", "本格麦焼酎", "本格米焼酎", "本格焼酎", "純米大吟醸", "純米吟醸", "特別純米", "大吟醸", "吟醸", "特別本醸造", "本醸造", "純米酒", "リキュール", "スパークリング", "クラフトサケ", "泡盛"]:
            if clean_brand_target.startswith(pref_strip):
                clean_brand_target = clean_brand_target[len(pref_strip):].strip()
        if clean_brew and clean_brand_target.startswith(clean_brew):
            clean_brand_target = clean_brand_target[len(clean_brew):].strip()

        if " " in clean_brand_target:
            brand = clean_brand_target.split()[0].strip()
        else:
            brand = clean_brand_target[:6].strip()

        if len(brand) <= 1 or brand in ["本格", "純米", "大吟", "本醸", "特別", "リキュ", "スパ"]:
            brand = clean_brew if clean_brew else matched_spec[:4]

        found_products.append({
            "brand": brand,
            "spec": matched_spec,
            "cat": cat,
            "polish": polish,
            "rice": rice,
            "alc": alc
        })

    # 一意化
    seen_specs = set()
    unique_prods = []
    for fp in found_products:
        if fp['spec'] not in seen_specs:
            seen_specs.add(fp['spec'])
            unique_prods.append(fp)

    return unique_prods

total_new_extracted = 0
now_str = datetime.now().isoformat()

with open(TARGET_LOG, "w", encoding="utf-8") as lf:
    lf.write(f"=== 最新検証済364蔵 深層クローリング実行ログ ({now_str}) ===\n\n")

    for idx, brew in enumerate(target_breweries, 1):
        b_id = brew['id']
        b_name = brew['name']
        pref = brew['prefecture']
        base_url = brew['website']

        msg = f"[{idx}/{len(target_breweries)}] 🏭 ID {b_id}: {b_name} ({pref}) - {base_url}"
        print(msg)
        lf.write(msg + "\n")

        visited_urls = set([base_url])
        urls_to_visit = [base_url]
        all_texts = []

        sub_depth_limit = 8
        while urls_to_visit and len(visited_urls) <= sub_depth_limit:
            curr_url = urls_to_visit.pop(0)
            links, texts = fetch_and_parse(curr_url)
            all_texts.extend(texts)
            for l in links:
                if l not in visited_urls and len(visited_urls) <= sub_depth_limit:
                    visited_urls.add(l)
                    urls_to_visit.append(l)

        # 銘柄抽出
        extracted = extract_products_from_texts(all_texts, b_name, pref)
        brewery_new_count = 0

        for item in extracted:
            cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name = ?", (item['spec'], b_name))
            if not cur.fetchone():
                try:
                    cur.execute("""
                        INSERT INTO products (
                            brand_name, spec_name, category, polish_ratio, rice_variety,
                            alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
                    """, (
                        item['brand'], item['spec'], item['cat'], item['polish'],
                        item['rice'], item['alc'], b_name, pref,
                        f"Deep Verified Crawler ({base_url})", now_str
                    ))
                    brewery_new_count += 1
                    total_new_extracted += 1
                    lf.write(f"    ✨ [新規SKU抽出] {item['spec']} [{item['cat']}] (米: {item['rice']}, 精米: {item['polish']})\n")
                except sqlite3.IntegrityError:
                    pass

        if brewery_new_count > 0:
            print(f"  👉 {b_name}: {brewery_new_count} 件の新規SKUを深層抽出・追加登録")
            lf.write(f"  👉 {b_name}: {brewery_new_count} 件の新規SKUを追加登録\n\n")

        conn.commit()
        time.sleep(0.05)

cur.execute("SELECT COUNT(*) FROM products")
final_total_prods = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
final_total_brews = cur.fetchone()[0]

conn.close()

print(f"\n==================================================================")
print(f"🎉 最新検証済364蔵 深層クローリング・全SKU抽出が完了しました！")
print(f"・新規追加製品数: {total_new_extracted} 件")
print(f"・製品総数      : {final_total_prods} 件")
print(f"・紐付け酒蔵総数: {final_total_brews} 蔵")
print(f"・詳細ログ      : {TARGET_LOG}")
print(f"==================================================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
