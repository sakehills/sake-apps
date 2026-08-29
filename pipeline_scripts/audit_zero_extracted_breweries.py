import os
import sys
import re
import sqlite3

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT_DIR, "pipeline_scripts", "exhaustive_all_breweries_crawler.log")
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🔍 クロール時 抽出0件だった酒蔵の徹底原因究明＆リストアップ ===")

with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
    log_content = f.read()

b_entries = re.findall(r'\[\d+/1376\] 🏭 ID (\d+):\s*(.*?)\s*\((.*?)\)\s*-\s*(http.*)', log_content)

zero_breweries = []
for b_id, name, pref, url in b_entries:
    # 抽出成功ログ: 👉 {name}: X 件の新規SKU
    if f"👉 {name}:" not in log_content:
        zero_breweries.append({
            "id": b_id,
            "name": name,
            "pref": pref,
            "url": url.strip()
        })

print(f"📊 クロール走査総蔵数       : {len(b_entries)} 蔵")
print(f"⚠️ クロールで0件だった酒蔵数 : {len(zero_breweries)} 蔵")

print("\n【0件だった主な蔵元とその原因例】")
for zb in zero_breweries[:30]:
    print(f"・ID {zb['id']}: {zb['name']} ({zb['pref']}) - {zb['url']}")
