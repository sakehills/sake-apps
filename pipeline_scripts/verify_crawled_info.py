import sqlite3
import os
import io
import sys

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("==================== 公式HP一次情報 抽出結果 検証 ====================")
cursor.execute("SELECT count(*) FROM breweries")
total = cursor.fetchone()[0]
print(f"総酒蔵数: {total} 蔵\n")

fields = [
    ("代表電話番号 (phone)", "phone"),
    ("FAX番号 (fax)", "fax"),
    ("代表者・蔵元当主名 (president_name)", "president_name"),
    ("杜氏・醸造責任者名 (toji_name)", "toji_name"),
    ("直売所営業時間 (opening_hours)", "opening_hours"),
    ("定休日 (regular_holiday)", "regular_holiday"),
    ("駐車場情報 (parking_info)", "parking_info"),
    ("交通アクセス情報 (access_info)", "access_info"),
    ("公式オンラインショップ (official_ec_url)", "official_ec_url"),
    ("公式Instagram (sns_instagram)", "sns_instagram"),
    ("公式Facebook (sns_facebook)", "sns_facebook"),
    ("公式X / Twitter (sns_twitter)", "sns_twitter"),
    ("使用酒米情報 (main_rice_varieties)", "main_rice_varieties"),
    ("醸造・酒造り特徴 (brewing_features)", "brewing_features"),
    ("一次情報出典URL (info_source_url)", "info_source_url")
]

print("【各公式一次情報項目の取得件数・充足率】")
for label, col in fields:
    cursor.execute(f"SELECT count(*) FROM breweries WHERE {col} IS NOT NULL AND {col} != ''")
    cnt = cursor.fetchone()[0]
    pct = (cnt / total) * 100
    print(f"  ・{label:40}: {cnt:4} 蔵 ({pct:5.1f}%)")

print("\n【主要蔵の公式一次情報 抽出サンプル】")
cursor.execute("""
    SELECT name, phone, president_name, toji_name, opening_hours, official_ec_url, sns_instagram, main_rice_varieties, brewing_features, info_source_url
    FROM breweries
    WHERE name IN ('八海醸造株式会社', '旭酒造株式会社', '白鶴酒造株式会社', '新政酒造株式会社', '末廣酒造株式会社') OR name_norm IN ('八海醸造株式会社', '旭酒造株式会社', '白鶴酒造株式会社', '新政酒造株式会社', '末廣酒造株式会社')
    LIMIT 5
""")
for r in cursor.fetchall():
    print(f"\n■ [蔵名]: {r[0]}")
    print(f"   - TEL: {r[1]} | 代表者: {r[2]} | 杜氏: {r[3]}")
    print(f"   - 営業時間: {r[4]}")
    print(f"   - 公式EC: {r[5]}")
    print(f"   - 公式Instagram: {r[6]}")
    print(f"   - 使用酒米: {r[7]}")
    print(f"   - 醸造特徴: {r[8]}")
    print(f"   - 出典URL: {r[9]}")

conn.close()
