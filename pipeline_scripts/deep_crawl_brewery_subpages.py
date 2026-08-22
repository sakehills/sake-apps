import sqlite3
import os
import re
import csv
import sys
import io
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
BACKUP_DIR = r"C:\Users\hitos\Antigravity-Playground\japanese-sake-db\database-backup"
MIGRATION_DIR = os.path.join(BACKUP_DIR, "migrations")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

RICE_VARIETIES_KEYWORDS = [
    "山田錦", "雄町", "五百万石", "美山錦", "出羽燦々", "出羽の里", "雪女神", "秋田酒こまち",
    "吟風", "彗星", "きたしずく", "八反錦", "千本錦", "祝", "亀の尾", "愛山", "備前雄町",
    "赤磐雄町", "華吹雪", "華想い", "美郷錦", "越淡麗", "一本〆", "ひとごこち", "金紋錦",
    "強力", "神力", "玉栄", "渡船", "山田穂", "サキホコレ", "吟の夢", "松山三井"
]

BREWING_KEYWORDS = [
    "生酛", "きもと", "山廃", "木桶", "全量純米", "無濾過生原酒", "無濾過", "原酒",
    "直汲み", "中取り", "袋吊り", "雫取り", "四季醸造", "長期熟成", "古酒", "瓶燗火入れ",
    "低温発酵", "氷温貯蔵", "冷蔵完備", "特定名称酒のみ"
]

SUBPAGE_PATTERNS = [
    "/company", "/about", "/access", "/shop", "/tour", "/guide", "/info",
    "/profile", "/brewery", "/kodawari", "/sake", "/outline"
]

def fetch_page(url, timeout=5):
    if not url or not url.startswith("http"):
        return ""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            content_type = response.headers.get('Content-Type', '')
            encoding = 'utf-8'
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1].split(';')[0].strip().lower()
            elif b'charset=shift_jis' in raw.lower() or b'charset=sjis' in raw.lower():
                encoding = 'shift_jis'
            elif b'charset=euc-jp' in raw.lower():
                encoding = 'euc-jp'
            elif b'charset=cp932' in raw.lower():
                encoding = 'cp932'
            try:
                return raw.decode(encoding, errors='replace')
            except Exception:
                return raw.decode('utf-8', errors='replace')
    except Exception:
        return ""

def deep_enrich_single_brewery(row):
    b_id, name, website, phone, pres, toji, hours, hol, ec, insta, fb, tw, rice, brew = row
    if not website or not website.startswith("http"):
        return None

    # すでに主要項目が揃っていればスキップ
    if phone and pres and hours and ec:
        return None

    base_url = website.rstrip('/')
    # サブページの候補探索
    html_top = fetch_page(base_url)
    if not html_top:
        return None

    soup_top = BeautifulSoup(html_top, 'html.parser')
    sub_urls = []

    # サイト内リンクから会社概要・アクセス・店舗リンクを検出
    for a in soup_top.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text().strip()
        if any(k in href.lower() for k in SUBPAGE_PATTERNS) or any(k in text for k in ["会社概要", "アクセス", "店舗", "見学", "酒造り", "こだわり", "オンラインショップ"]):
            full_sub_url = urllib.parse.urljoin(base_url, href)
            if full_sub_url.startswith(base_url) and full_sub_url not in sub_urls and len(sub_urls) < 3:
                sub_urls.append(full_sub_url)

    # 結合テキストの解析
    combined_texts = [soup_top.get_text(separator=' ')]
    for sub in sub_urls:
        sub_html = fetch_page(sub)
        if sub_html:
            sub_soup = BeautifulSoup(sub_html, 'html.parser')
            combined_texts.append(sub_soup.get_text(separator=' '))

    all_text = re.sub(r'\s+', ' ', " ".join(combined_texts))

    # 電話
    if not phone:
        m = re.search(r'(?:TEL|電話|Tel|TEL\s*[:：])\s*([0-9０-９]{2,5}[-ー−()（）\s]?[0-9０-９]{1,4}[-ー−\s]?[0-9０-９]{3,4})', all_text)
        if m:
            raw_t = m.group(1).replace('（', '(').replace('）', ')').replace('ー', '-').replace('−', '-').strip()
            if len(re.sub(r'\D', '', raw_t)) >= 9:
                phone = raw_t

    # 代表者
    if not pres:
        m = re.search(r'(?:代表取締役社長|代表取締役|代表者|代表社員|蔵元当主|社長)\s*[:：]?\s*([一-龥]{2,5}\s+[一-龥]{1,5}|[一-龥]{2,5})', all_text)
        if m:
            cand = m.group(1).strip()
            if len(cand) <= 8 and not any(w in cand for w in ["挨拶", "メッセージ", "紹介", "沿革", "株式会社", "有限会社", "酒造"]):
                pres = cand

    # 杜氏
    if not toji:
        m = re.search(r'(?:総杜氏|杜氏|製造責任者|醸造責任者)\s*[:：]?\s*([一-龥]{2,5}\s+[一-龥]{1,5}|[一-龥]{2,5})', all_text)
        if m:
            cand_t = m.group(1).strip()
            if len(cand_t) <= 8 and not any(w in cand_t for w in ["流派", "集団", "紹介", "株式会社", "有限会社", "酒造"]):
                toji = cand_t

    # 営業時間
    if not hours:
        m = re.search(r'(?:営業時間|OPEN|開館時間|営業|店舗営業時間)\s*[:：]?\s*([0-2]?[0-9][:：][0-5][0-9]\s*[-〜～–]\s*[0-2]?[0-9][:：][0-5][0-9])', all_text)
        if m:
            hours = m.group(1).replace('：', ':').strip()

    # 定休日
    if not hol:
        m = re.search(r'(?:定休日|休業日|休館日)\s*[:：]?\s*([^\n\r<、。]{2,25}(?:曜日|日|祝日|年末年始|不定休|年中無休))', all_text)
        if m:
            hol = m.group(1).strip()
        elif "年中無休" in all_text:
            hol = "年中無休"

    # 酒米
    if not rice:
        matched_rice = [r for r in RICE_VARIETIES_KEYWORDS if r in all_text]
        if matched_rice:
            rice = "・".join(matched_rice[:5])

    # 醸造特徴
    if not brew:
        matched_brew = [b for b in BREWING_KEYWORDS if b in all_text]
        if matched_brew:
            brew = "・".join(matched_brew[:5])

    return (phone, pres, toji, hours, hol, rice, brew, b_id)

def run_deep_crawl():
    print("[*] サブページ深層解析パイプライン開始...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, website, phone, president_name, toji_name, opening_hours, regular_holiday,
               official_ec_url, sns_instagram, sns_facebook, sns_twitter, main_rice_varieties, brewing_features
        FROM breweries
        WHERE website IS NOT NULL AND website LIKE 'http%'
    """)
    rows = cursor.fetchall()
    print(f"[*] 解析対象酒蔵: {len(rows)} 蔵")

    updated_items = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(deep_enrich_single_brewery, r): r[0] for r in rows}
        done = 0
        for f in as_completed(futures):
            res = f.result()
            if res:
                updated_items.append(res)
            done += 1
            if done % 300 == 0:
                print(f"  [進捗] {done}/{len(rows)} 蔵のサブページ深層解析完了...")

    print(f"[*] 更新対象: {len(updated_items)} 蔵のデータを書き込み中...")
    cursor.executemany("""
        UPDATE breweries
        SET phone = COALESCE(NULLIF(?, ''), phone),
            president_name = COALESCE(NULLIF(?, ''), president_name),
            toji_name = COALESCE(NULLIF(?, ''), toji_name),
            opening_hours = COALESCE(NULLIF(?, ''), opening_hours),
            regular_holiday = COALESCE(NULLIF(?, ''), regular_holiday),
            main_rice_varieties = COALESCE(NULLIF(?, ''), main_rice_varieties),
            brewing_features = COALESCE(NULLIF(?, ''), brewing_features)
        WHERE id = ?
    """, updated_items)
    conn.commit()

    # CSV同期エクスポート
    csv_export_path = os.path.join(BACKUP_DIR, "breweries.csv")
    cursor.execute("PRAGMA table_info(breweries)")
    all_headers = [c[1] for c in cursor.fetchall()]
    cursor.execute("SELECT * FROM breweries ORDER BY id ASC")
    all_rows = cursor.fetchall()
    with open(csv_export_path, "w", encoding="utf-8-sig", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(all_headers)
        for r in all_rows:
            writer.writerow(r)
    print(f"[OK] 最新データで同期エクスポート完了: {csv_export_path}")
    conn.close()

if __name__ == "__main__":
    run_deep_crawl()
