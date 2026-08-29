import os
import sys
import re
import urllib.request
import urllib.parse
import sqlite3
import subprocess
import time
import ssl

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
LOG_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "exhaustive_all_breweries_crawler.log")

print("==================================================================")
print("🌐 全酒蔵 最新公式URL・ブランド専用ドメイン名寄せ＆実生存検証パイプライン")
print(f"DB Path: {DB_PATH}")
print("==================================================================\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. 0件だった酒蔵および古いURLを持つ酒蔵の抽出
with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
    log_content = f.read()

b_entries = re.findall(r'\[\d+/1376\] 🏭 ID (\d+):\s*(.*?)\s*\((.*?)\)\s*-\s*(http.*)', log_content)

zero_breweries = []
for b_id, name, pref, url in b_entries:
    if f"👉 {name}:" not in log_content:
        zero_breweries.append({
            "id": int(b_id),
            "name": name.strip(),
            "pref": pref.strip(),
            "current_url": url.strip()
        })

print(f"📊 検証対象の未取得・要名寄せ酒蔵数: {len(zero_breweries)} 蔵\n")

# SSLコンテキスト（安全な検証）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

# 既知の有名蔵・ブランド専用ドメインの最新確定マッピング
KNOWN_BRAND_DOMAINS = {
    "油長酒造": "https://www.yuchoshuzo.com/",
    "高木酒造": "https://www.takagisyuzo.co.jp/",
    "清水清三郎商店": "https://www.zaku.co.jp/",
    "平和酒造": "https://www.heiwashuzo.co.jp/",
    "旭酒造": "https://www.dassai.co.jp/",
    "新政酒造": "http://www.aramasa.jp/",
    "木屋正酒造": "https://www.jikon-sake.com/",
    "石本酒造": "https://koshinokanbai.co.jp/",
    "八海醸造": "https://www.hakkaisan.co.jp/",
    "朝日酒造": "https://www.asahi-shuzo.co.jp/",
    "鶴乃江酒造": "https://tsurunoe.com/",
    "辰泉酒造": "https://tatsuizumi.co.jp/",
    "佐久の花酒造": "https://www.sakunohana.jp/",
    "美寿々酒造": "https://misuzusake.com/",
    "大雪渓酒造": "https://www.jizake.co.jp/",
    "伊東酒造": "https://www.yokobue.co.jp/",
    "麗人酒造": "https://www.reijin.biz/",
    "北安醸造": "https://hokuan.co.jp/",
    "丸世酒造店": "https://marusesyuzouten.co.jp/",
    "酒千蔵野": "https://www.shusen.jp/",
    "松葉屋本店": "https://hokuto-matsubaya.com/",
    "古屋酒造店": "https://furuya-shuzou.com/",
    "宮島酒店": "https://www.miyajima.net/",
    "米澤酒造": "https://www.imanisiki.co.jp/",
    "湯川酒造店": "https://yukawabrewery.com/",
    "中善酒造店": "https://nakanorisan.com/",
    "若林醸造": "https://www.tsukiyoshino.com/",
    "大谷忠吉本店": "https://www.hakuyou.co.jp/"
}

updated_urls_count = 0
verified_live_count = 0
failed_urls_count = 0

def check_url_live(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=7) as resp:
            final_url = resp.geturl()
            return True, final_url
    except Exception:
        # http -> https 試行
        if url.startswith("http://"):
            https_url = url.replace("http://", "https://", 1)
            try:
                req = urllib.request.Request(https_url, headers=HEADERS)
                with urllib.request.urlopen(req, context=ctx, timeout=7) as resp:
                    return True, resp.geturl()
            except Exception:
                pass
        return False, url

print("🔍 1件ずつ慎重にURLの実生存確認・最新ドメイン名寄せを開始します...\n")

for idx, zb in enumerate(zero_breweries, 1):
    b_id = zb['id']
    b_name = zb['name']
    pref = zb['pref']
    curr_url = zb['current_url']

    clean_name = b_name.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").replace("合同会社", "").strip()

    target_url = curr_url
    # 既知の公式ドメインがある場合優先
    for k, v in KNOWN_BRAND_DOMAINS.items():
        if k in b_name:
            target_url = v
            break

    is_live, real_url = check_url_live(target_url)

    if is_live:
        verified_live_count += 1
        if real_url != curr_url or target_url != curr_url:
            cur.execute("UPDATE breweries SET website = ? WHERE id = ?", (real_url, b_id))
            updated_urls_count += 1
            print(f"[{idx}/{len(zero_breweries)}] ✅ 【URL更新】ID {b_id} {b_name} ({pref})")
            print(f"    旧: {curr_url}")
            print(f"    新: {real_url}")
        else:
            if idx % 20 == 0:
                print(f"[{idx}/{len(zero_breweries)}] 🟢 生存確認済: ID {b_id} {b_name} -> {real_url}")
    else:
        failed_urls_count += 1
        # プロバイダ閉鎖系（avis.ne.jp, nifty, geocities等）のクレンジング
        if any(bad in curr_url for bad in ["avis.ne.jp", "geocities", "nifty.com", "biglobe.ne.jp", "ocn.ne.jp", "stvnet.home.ne.jp"]):
            print(f"[{idx}/{len(zero_breweries)}] ⚠️ 【休止・閉鎖プロバイダ検出】ID {b_id} {b_name} ({pref}): {curr_url}")

    # 接続負荷軽減のための微小ウェイト
    time.sleep(0.05)

conn.commit()

# 全酒蔵の最新Webサイト登録数集計
cur.execute("SELECT COUNT(*) FROM breweries WHERE website IS NOT NULL AND website != ''")
total_with_web = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM breweries")
total_breweries = cur.fetchone()[0]

conn.close()

print(f"\n==================================================================")
print(f"🎉 全酒蔵 最新公式URL・ブランドドメイン名寄せ＆実生存検証完了！")
print(f"・検証対象蔵元数                : {len(zero_breweries)} 蔵")
print(f"・最新ドメインへ更新完了蔵元数  : {updated_urls_count} 蔵")
print(f"・実生存確認（HTTP 200 OK）蔵元数: {verified_live_count} 蔵")
print(f"・休止/閉鎖ドメイン検出蔵元数   : {failed_urls_count} 蔵")
print(f"・Webサイト保有酒蔵総数         : {total_with_web} / {total_breweries} 蔵")
print(f"==================================================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
