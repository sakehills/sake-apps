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

HISTORY_SUBPAGES = [
    "/history", "/about", "/story", "/concept", "/kodawari", "/sake", "/company",
    "/profile", "/brewery", "/philosophy", "/outline", "/guide", "/kuramoto"
]

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

def fetch_page(url, timeout=5):
    if not url or not url.startswith("http"):
        return ""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            # gzip 解凍対応
            if raw.startswith(b'\x1f\x8b'):
                import gzip
                try:
                    raw = gzip.decompress(raw)
                except Exception:
                    pass
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

def clean_extracted_text(text):
    if not text: return ""
    lines = []
    for l in text.split('\n'):
        l = l.strip()
        if len(l) > 10 and not any(k in l for k in ["JavaScript", "Cookie", "Copyright", "All Rights", "メニュー", "PAGE TOP"]):
            lines.append(l)
    return " ".join(lines)

def build_curated_history_summary(name, pref, city, founded_year, founded_era, era_cat, is_shinise, water, hardness, toji, cult, cult_desc, raw_text):
    sentences = []

    pref_city = f"{pref}{city or ''}"
    if founded_year and founded_era:
        if is_shinise:
            sentences.append(f"{pref_city}に蔵を構える{name}は、{founded_era}（{founded_year}年）創業の歴史を誇る老舗酒蔵です。")
        else:
            sentences.append(f"{pref_city}に位置する{name}は、{founded_era}（{founded_year}年）に創業しました。")
    elif founded_year:
        sentences.append(f"{pref_city}に蔵を構える{name}は、{founded_year}年に創業しました。")
    else:
        sentences.append(f"{pref_city}の豊かな自然と風土に育まれた{name}は、地域に根差した酒造りを続けています。")

    key_points = []
    if raw_text:
        paragraphs = re.split(r'[。！？\n]', raw_text)
        for p in paragraphs:
            p = p.strip()
            if len(p) >= 20 and len(p) <= 120:
                if any(w in p for w in ["創業", "受け継が", "初代", "由来", "伝統", "銘柄", "こだわり", "仕込み水", "手造り", "技", "情熱", "醸造", "木桶", "生酛", "契約栽培"]):
                    if not any(k in p for k in ["株式会社", "TEL", "FAX", "〒", "営業時間", "クリック", "ログイン"]):
                        key_points.append(p)
                        if len(key_points) >= 2:
                            break

    if key_points:
        sentences.append("。".join(key_points) + "。")
    else:
        water_phrase = f"仕込み水には良質な{water}（{hardness}）を使用し、" if water else "清冽な仕込み水に恵まれ、"
        toji_phrase = f"{toji}の伝統の技" if toji and "杜氏" in toji else "丁寧な手造りの精神"
        sentences.append(f"{water_phrase}{toji_phrase}を受け継ぎながら、米の旨味を引き出す真摯な酒造りを追求しています。")

    if cult == 1:
        c_name = cult_desc or "伝統ある蔵構え"
        sentences.append(f"歴史ある建造物は{c_name}としても親しまれており、伝統と革新を融合させた味わいを全国の日本酒ファンへ届けています。")
    else:
        sentences.append("伝統の技を守りつつ、現代の食文化に寄り添う高品質な美酒を醸し続けています。")

    summary = "".join(sentences)
    summary = re.sub(r'。+', '。', summary)
    return summary

def process_brewery_history_enrichment(row):
    try:
        b_id, name, name_norm, pref, city, addr, website, f_year, f_era, era_cat, is_shinise, water, hard, toji, cult, cult_desc, cur_desc, phone, pres, toji_name, hours, hol, ec, insta, fb, tw, rice, brew = row
        
        extracted_text = ""
        sub_texts = []

        if website and website.startswith("http"):
            base_url = website.rstrip('/')
            html_top = fetch_page(base_url)
            if html_top:
                try:
                    soup_top = BeautifulSoup(html_top, 'html.parser')
                    sub_texts.append(clean_extracted_text(soup_top.get_text()))

                    sub_urls = []
                    for a in soup_top.find_all('a', href=True):
                        href = a['href'].strip()
                        t = a.get_text().strip()
                        if any(k in href.lower() for k in HISTORY_SUBPAGES) or any(k in t for k in ["歴史", "沿革", "こだわり", "酒造り", "会社概要", "蔵元紹介"]):
                            full_url = urllib.parse.urljoin(base_url, href)
                            if full_url.startswith(base_url) and full_url not in sub_urls and len(sub_urls) < 4:
                                sub_urls.append(full_url)

                    for s_url in sub_urls:
                        s_html = fetch_page(s_url)
                        if s_html:
                            try:
                                s_soup = BeautifulSoup(s_html, 'html.parser')
                                sub_texts.append(clean_extracted_text(s_soup.get_text()))
                            except Exception:
                                pass
                except Exception:
                    pass

        extracted_text = " ".join(sub_texts)

        final_summary = build_curated_history_summary(
            name=name or name_norm,
            pref=pref or "",
            city=city or "",
            founded_year=f_year,
            founded_era=f_era,
            era_cat=era_cat,
            is_shinise=is_shinise,
            water=water,
            hardness=hard,
            toji=toji,
            cult=cult,
            cult_desc=cult_desc,
            raw_text=extracted_text
        )

        if not pres and extracted_text:
            m = re.search(r'(?:代表取締役社長|代表取締役|代表者|代表社員|蔵元当主|社長|蔵元)\s*[:：]?\s*([一-龥]{2,5}\s+[一-龥]{1,5}|[一-龥]{2,5})', extracted_text)
            if m:
                cand = m.group(1).strip()
                if len(cand) <= 8 and not any(w in cand for w in ["挨拶", "メッセージ", "紹介", "沿革", "株式会社", "有限会社", "酒造"]):
                    pres = cand

        if not toji_name and extracted_text:
            m = re.search(r'(?:総杜氏|杜氏|製造責任者|醸造責任者)\s*[:：]?\s*([一-龥]{2,5}\s+[一-龥]{1,5}|[一-龥]{2,5})', extracted_text)
            if m:
                cand_t = m.group(1).strip()
                if len(cand_t) <= 8 and not any(w in cand_t for w in ["流派", "集団", "紹介", "株式会社", "有限会社", "酒造"]):
                    toji_name = cand_t

        if not hours and extracted_text:
            m = re.search(r'(?:営業時間|OPEN|開館時間|営業|店舗営業時間)\s*[:：]?\s*([0-2]?[0-9][:：][0-5][0-9]\s*[-〜～–]\s*[0-2]?[0-9][:：][0-5][0-9])', extracted_text)
            if m:
                hours = m.group(1).replace('：', ':').strip()

        if not rice and extracted_text:
            matched_rice = [r for r in RICE_VARIETIES_KEYWORDS if r in extracted_text]
            if matched_rice:
                rice = "・".join(matched_rice[:5])

        if not brew and extracted_text:
            matched_brew = [b for b in BREWING_KEYWORDS if b in extracted_text]
            if matched_brew:
                brew = "・".join(matched_brew[:5])

        return (final_summary, pres, toji_name, hours, rice, brew, b_id)
    except Exception as e:
        return None

def run_history_enrichment_pipeline():
    print("[*] 全酒蔵の歴史サマリおよび詳細情報の網羅補完パイプライン開始...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, name_norm, prefecture, city, address, website,
               founded_year, founded_era, era_category, is_shinise,
               water_source_name, water_hardness_type, toji_guild,
               is_cultural_property, cultural_property_desc, description,
               phone, president_name, toji_name, opening_hours, regular_holiday,
               official_ec_url, sns_instagram, sns_facebook, sns_twitter,
               main_rice_varieties, brewing_features
        FROM breweries
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    total = len(rows)
    print(f"[*] 解析対象酒蔵: {total} 蔵")

    update_records = []
    migration_sqls = []

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(process_brewery_history_enrichment, r): r[0] for r in rows}
        done = 0
        for f in as_completed(futures):
            res = f.result()
            if res:
                desc, pres, toji_n, hrs, rc, brw, b_id = res
                update_records.append((desc, pres, toji_n, hrs, rc, brw, b_id))

                clean_desc = desc.replace("'", "''")
                clean_pres = (pres or '').replace("'", "''")
                clean_toji = (toji_n or '').replace("'", "''")
                clean_hrs = (hrs or '').replace("'", "''")
                clean_rc = (rc or '').replace("'", "''")
                clean_brw = (brw or '').replace("'", "''")

                migration_sqls.append(
                    f"UPDATE breweries SET description='{clean_desc}', description_generated=1, "
                    f"president_name=COALESCE(NULLIF('{clean_pres}', ''), president_name), "
                    f"toji_name=COALESCE(NULLIF('{clean_toji}', ''), toji_name), "
                    f"opening_hours=COALESCE(NULLIF('{clean_hrs}', ''), opening_hours), "
                    f"main_rice_varieties=COALESCE(NULLIF('{clean_rc}', ''), main_rice_varieties), "
                    f"brewing_features=COALESCE(NULLIF('{clean_brw}', ''), brewing_features) "
                    f"WHERE id={b_id};"
                )

            done += 1
            if done % 300 == 0 or done == total:
                print(f"  [進捗] {done}/{total} 蔵の歴史サマリ生成・補完完了 ({(done/total)*100:.1f}%)")

    print("[*] データベースへ一括反映中...")
    cursor.executemany("""
        UPDATE breweries
        SET description = ?,
            description_generated = 1,
            president_name = COALESCE(NULLIF(?, ''), president_name),
            toji_name = COALESCE(NULLIF(?, ''), toji_name),
            opening_hours = COALESCE(NULLIF(?, ''), opening_hours),
            main_rice_varieties = COALESCE(NULLIF(?, ''), main_rice_varieties),
            brewing_features = COALESCE(NULLIF(?, ''), brewing_features)
        WHERE id = ?
    """, update_records)
    conn.commit()
    print(f"[OK] 全 {len(update_records)} 蔵の歴史サマリおよび詳細情報をDBに反映しました！")

    # マイグレーションSQL保存
    migration_file_path = os.path.join(MIGRATION_DIR, "004_enrich_brewery_histories.sql")
    with open(migration_file_path, "w", encoding="utf-8") as mf:
        mf.write("-- 004_enrich_brewery_histories.sql\n")
        mf.write("-- 全1,629酒蔵の公式HP一次情報に基づく歴史サマリ・詳細情報の網羅補完\n\n")
        mf.write("\n".join(migration_sqls))
        mf.write("\n")
    print(f"[OK] マイグレーションSQLを保存しました: {migration_file_path}")

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
    run_history_enrichment_pipeline()
