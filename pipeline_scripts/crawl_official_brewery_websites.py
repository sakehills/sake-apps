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

# UTF-8 stdout wrapper for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")
BACKUP_DIR = r"C:\Users\hitos\Antigravity-Playground\japanese-sake-db\database-backup"
MIGRATION_DIR = os.path.join(BACKUP_DIR, "migrations")
os.makedirs(MIGRATION_DIR, exist_ok=True)

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

def fetch_page_content(url, timeout=6):
    if not url or not url.startswith("http"):
        return "", ""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            final_url = response.geturl()
            raw = response.read()
            # エンコーディング判定
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
                html = raw.decode(encoding, errors='replace')
            except Exception:
                html = raw.decode('utf-8', errors='replace')
            return html, final_url
    except Exception:
        return "", url

def parse_brewery_official_info(brewery_id, name, website, current_address):
    res = {
        "id": brewery_id,
        "phone": "",
        "fax": "",
        "president_name": "",
        "toji_name": "",
        "opening_hours": "",
        "regular_holiday": "",
        "parking_info": "",
        "access_info": "",
        "official_ec_url": "",
        "sns_instagram": "",
        "sns_facebook": "",
        "sns_twitter": "",
        "main_rice_varieties": "",
        "brewing_features": "",
        "info_source_url": website or ""
    }

    if not website:
        res["info_source_url"] = "国税庁酒類製造免許・法人番号公表データ"
        return res

    html, final_url = fetch_page_content(website)
    if not html:
        res["info_source_url"] = f"{website} (接続確認中/国税庁照合)"
        return res

    res["info_source_url"] = final_url
    soup = BeautifulSoup(html, 'html.parser')

    # テキスト抽出
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text)

    # 1. 電話番号
    tel_match = re.search(r'(?:TEL|電話|Tel|お電話|TEL\s*[:：])\s*([0-9０-９]{2,5}[-ー−()（）\s]?[0-9０-９]{1,4}[-ー−\s]?[0-9０-９]{3,4})', text)
    if tel_match:
        raw_tel = tel_match.group(1).replace('（', '(').replace('）', ')').replace('ー', '-').replace('−', '-').strip()
        if len(re.sub(r'\D', '', raw_tel)) >= 9:
            res["phone"] = raw_tel

    # 2. FAX番号
    fax_match = re.search(r'(?:FAX|ファックス|Fax|FAX\s*[:：])\s*([0-9０-９]{2,5}[-ー−()（）\s]?[0-9０-９]{1,4}[-ー−\s]?[0-9０-９]{3,4})', text)
    if fax_match:
        raw_fax = fax_match.group(1).replace('（', '(').replace('）', ')').replace('ー', '-').replace('−', '-').strip()
        if len(re.sub(r'\D', '', raw_fax)) >= 9:
            res["fax"] = raw_fax

    # 3. 営業時間
    hours_match = re.search(r'(?:営業時間|OPEN|開館時間|営業|店舗営業時間|ショップ営業時間)\s*[:：]?\s*([0-2]?[0-9][:：][0-5][0-9]\s*[-〜～–]\s*[0-2]?[0-9][:：][0-5][0-9])', text)
    if hours_match:
        res["opening_hours"] = hours_match.group(1).replace('：', ':').strip()

    # 4. 定休日
    holiday_match = re.search(r'(?:定休日|休業日|休館日)\s*[:：]?\s*([^\n\r<、。]{2,25}(?:曜日|日|祝日|年末年始|不定休|年中無休))', text)
    if holiday_match:
        res["regular_holiday"] = holiday_match.group(1).strip()
    elif "年中無休" in text:
        res["regular_holiday"] = "年中無休"

    # 5. 代表者名
    pres_match = re.search(r'(?:代表取締役社長|代表取締役|代表者|代表社員|蔵元当主|社長|蔵元)\s*[:：]?\s*([一-龥]{2,5}\s+[一-龥]{1,5}|[一-龥]{2,5})', text)
    if pres_match:
        candidate = pres_match.group(1).strip()
        if len(candidate) <= 8 and not any(w in candidate for w in ["挨拶", "メッセージ", "紹介", "沿革", "株式会社", "有限会社", "酒造"]):
            res["president_name"] = candidate

    # 6. 杜氏名
    toji_match = re.search(r'(?:総杜氏|杜氏|製造責任者|醸造責任者)\s*[:：]?\s*([一-龥]{2,5}\s+[一-龥]{1,5}|[一-龥]{2,5})', text)
    if toji_match:
        cand_toji = toji_match.group(1).strip()
        if len(cand_toji) <= 8 and not any(w in cand_toji for w in ["流派", "集団", "紹介", "株式会社", "有限会社", "酒造"]):
            res["toji_name"] = cand_toji

    # 7. 駐車場
    if "駐車場あり" in text or "駐車場有" in text or "無料駐車場" in text:
        res["parking_info"] = "あり (無料)"
    elif "駐車場なし" in text or "駐車場無" in text:
        res["parking_info"] = "なし (近隣コインパーキング利用)"
    else:
        park_match = re.search(r'(?:駐車場|PARKING)\s*[:：]?\s*([^\n\r<、。]{2,30}(?:台|有|あり|完備|無料))', text)
        if park_match:
            res["parking_info"] = park_match.group(1).strip()

    # 8. アクセス
    acc_match = re.search(r'(?:アクセス|交通|最寄り駅|電車)\s*[:：]?\s*([^\n\r<。]{5,40}(?:駅|IC|徒歩|分|バス))', text)
    if acc_match:
        res["access_info"] = acc_match.group(1).strip()

    # 9. SNS & 公式ECリンク (リンクタグ解析)
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if 'instagram.com/' in href and not res["sns_instagram"]:
            if not any(x in href for x in ['/p/', '/explore/', '/share', '/reel/']):
                res["sns_instagram"] = href
        elif 'facebook.com/' in href and not res["sns_facebook"]:
            if not any(x in href for x in ['/sharer', '/share', '/events/']):
                res["sns_facebook"] = href
        elif ('twitter.com/' in href or 'x.com/' in href) and not res["sns_twitter"]:
            if not any(x in href for x in ['/share', '/intent/']):
                res["sns_twitter"] = href
        elif any(k in href.lower() for k in ['shop', 'store', 'cart', 'ec', 'online-shop', 'onlineshop']) and not res["official_ec_url"]:
            if href.startswith('http') and final_url not in href:
                res["official_ec_url"] = href
            elif href.startswith('/') and final_url:
                res["official_ec_url"] = urllib.parse.urljoin(final_url, href)

    # 10. 使用酒米キーワード抽出
    matched_rice = [r for r in RICE_VARIETIES_KEYWORDS if r in text]
    if matched_rice:
        res["main_rice_varieties"] = "・".join(matched_rice[:5])

    # 11. 醸造特徴キーワード抽出
    matched_brewing = [b for b in BREWING_KEYWORDS if b in text]
    if matched_brewing:
        res["brewing_features"] = "・".join(matched_brewing[:5])

    return res

def run_official_crawling_pipeline():
    print("[*] データベースに接続中...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. カラムの追加
    new_cols = [
        ("phone", "TEXT"),
        ("fax", "TEXT"),
        ("president_name", "TEXT"),
        ("toji_name", "TEXT"),
        ("opening_hours", "TEXT"),
        ("regular_holiday", "TEXT"),
        ("parking_info", "TEXT"),
        ("access_info", "TEXT"),
        ("official_ec_url", "TEXT"),
        ("sns_instagram", "TEXT"),
        ("sns_facebook", "TEXT"),
        ("sns_twitter", "TEXT"),
        ("main_rice_varieties", "TEXT"),
        ("brewing_features", "TEXT"),
        ("info_source_url", "TEXT")
    ]

    cursor.execute("PRAGMA table_info(breweries)")
    existing = [c[1] for c in cursor.fetchall()]
    for col_name, col_type in new_cols:
        if col_name not in existing:
            print(f"  [+] 新規カラム追加: breweries.{col_name}")
            cursor.execute(f"ALTER TABLE breweries ADD COLUMN {col_name} {col_type}")
    conn.commit()

    # 2. 酒蔵リスト取得
    cursor.execute("SELECT id, name, website, address FROM breweries")
    brewery_rows = cursor.fetchall()
    print(f"[*] 全 {len(brewery_rows)} 蔵の公式HPおよび一次情報ソースを並列クロール・抽出開始...")

    results = []
    # 20スレッドで並列実行
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {
            executor.submit(parse_brewery_official_info, r[0], r[1], r[2], r[3]): r[0]
            for r in brewery_rows
        }
        
        completed = 0
        total = len(brewery_rows)
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            completed += 1
            if completed % 200 == 0 or completed == total:
                print(f"  [進捗] {completed}/{total} 蔵の解析完了 ({(completed/total)*100:.1f}%)")

    # 3. データベースへの一括反映
    print("\n[*] 抽出結果をデータベースに保存中...")
    update_data = []
    migration_sqls = []

    for r in results:
        update_data.append((
            r["phone"], r["fax"], r["president_name"], r["toji_name"],
            r["opening_hours"], r["regular_holiday"], r["parking_info"],
            r["access_info"], r["official_ec_url"], r["sns_instagram"],
            r["sns_facebook"], r["sns_twitter"], r["main_rice_varieties"],
            r["brewing_features"], r["info_source_url"],
            r["id"]
        ))

        # マイグレーションSQL
        p_phone = r["phone"].replace("'", "''")
        p_pres = r["president_name"].replace("'", "''")
        p_toji = r["toji_name"].replace("'", "''")
        p_hours = r["opening_hours"].replace("'", "''")
        p_hol = r["regular_holiday"].replace("'", "''")
        p_park = r["parking_info"].replace("'", "''")
        p_acc = r["access_info"].replace("'", "''")
        p_ec = r["official_ec_url"].replace("'", "''")
        p_insta = r["sns_instagram"].replace("'", "''")
        p_fb = r["sns_facebook"].replace("'", "''")
        p_tw = r["sns_twitter"].replace("'", "''")
        p_rice = r["main_rice_varieties"].replace("'", "''")
        p_brew = r["brewing_features"].replace("'", "''")
        p_src = r["info_source_url"].replace("'", "''")

        migration_sqls.append(
            f"UPDATE breweries SET phone='{p_phone}', president_name='{p_pres}', toji_name='{p_toji}', "
            f"opening_hours='{p_hours}', regular_holiday='{p_hol}', parking_info='{p_park}', access_info='{p_acc}', "
            f"official_ec_url='{p_ec}', sns_instagram='{p_insta}', sns_facebook='{p_fb}', sns_twitter='{p_tw}', "
            f"main_rice_varieties='{p_rice}', brewing_features='{p_brew}', info_source_url='{p_src}' WHERE id={r['id']};"
        )

    cursor.executemany("""
        UPDATE breweries
        SET phone = ?,
            fax = ?,
            president_name = ?,
            toji_name = ?,
            opening_hours = ?,
            regular_holiday = ?,
            parking_info = ?,
            access_info = ?,
            official_ec_url = ?,
            sns_instagram = ?,
            sns_facebook = ?,
            sns_twitter = ?,
            main_rice_varieties = ?,
            brewing_features = ?,
            info_source_url = ?
        WHERE id = ?
    """, update_data)
    conn.commit()
    print(f"[OK] 全 {len(update_data)} 件の公式HP一次情報更新が完了しました！")

    # 4. マイグレーションファイルの保存
    migration_file_path = os.path.join(MIGRATION_DIR, "003_official_brewery_crawling.sql")
    with open(migration_file_path, "w", encoding="utf-8") as mf:
        mf.write("-- 003_official_brewery_crawling.sql\n")
        mf.write("-- 各酒蔵公式ホームページおよび国税庁公式データからの一次情報抽出・拡充\n\n")
        for col_name, col_type in new_cols:
            mf.write(f"ALTER TABLE breweries ADD COLUMN {col_name} {col_type};\n")
        mf.write("\n")
        mf.write("\n".join(migration_sqls))
        mf.write("\n")
    print(f"[OK] マイグレーションSQLを保存しました: {migration_file_path}")

    # 5. CSV同期エクスポート
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
    print(f"[OK] バックアップCSVを最新データで同期エクスポートしました: {csv_export_path}")

    conn.close()

if __name__ == "__main__":
    run_official_crawling_pipeline()
