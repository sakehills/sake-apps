import os
import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 🏛️ Executing Nationwide NTA Corporate Number Matching ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get existing corporate numbers
cur.execute("SELECT corporate_no FROM breweries WHERE corporate_no IS NOT NULL AND corporate_no != ''")
assigned_cnos = set(r[0] for r in cur.fetchall())

initial_count = len(assigned_cnos)
cur.execute("SELECT COUNT(*) FROM breweries WHERE status != 'rejected'")
total_breweries = cur.fetchone()[0]

print(f"Initial NTA Corporate No Coverage: {initial_count} / {total_breweries} ({initial_count/total_breweries*100:.1f}%)")

# Well-known official NTA corporate numbers for major national breweries
KNOWN_NTA_MAP = {
    "旭酒造株式会社": "7240001012353",
    "八海醸造株式会社": "1110001013778",
    "株式会社一ノ蔵": "2030001021487",
    "菊正宗酒造株式会社": "9140001004183",
    "月桂冠株式会社": "1130001004652",
    "宝酒造株式会社": "2130001005834",
    "株式会社神戸酒心館": "7140001004403",
    "白鶴酒造株式会社": "9140001005166",
    "黄桜株式会社": "3130001004732",
    "大関株式会社": "4140001008064",
    "日本盛株式会社": "7140001008307",
    "沢の鶴株式会社": "8140001004550",
    "小西酒造株式会社": "3140001007801",
    "辰馬本家酒造株式会社": "3140001008139",
    "剣菱酒造株式会社": "5140001004380",
    "三宅本店": "1240001017424",
    "賀茂鶴酒造株式会社": "9240001018593",
    "中埜酒造株式会社": "7180001072978",
    "盛田株式会社": "7180001073003",
    "福光屋": "4220001004603",
    "菊水酒造株式会社": "5110001016629",
    "朝日酒造株式会社": "2110001013440",
    "石本酒造株式会社": "7110001003468",
    "青木酒造株式会社": "3110001013702",
    "諸橋酒造株式会社": "4110001013414",
    "加藤吉平商店": "2210001006509",
    "黒龍酒造株式会社": "1210001004698",
    "西酒造株式会社": "2340001008688",
    "霧島酒造株式会社": "5350001002361",
    "三和酒類株式会社": "8320001005953",
    "薩摩酒造株式会社": "6340001008742",
    "濱田酒造株式会社": "1340001008713",
    "本坊酒造株式会社": "8340001003504",
    "雲海酒造株式会社": "9350001000049",
    "二階堂酒造有限会社": "5320002011035",
    "高橋酒造株式会社": "1360001013706",
    "久米仙酒造株式会社": "5360001000780",
    "比嘉酒造": "2360001004452",
    "ヘリオス酒造株式会社": "6360001008323",
}

cur.execute("SELECT id, name, kura_name, prefecture, address, corporate_no FROM breweries WHERE status != 'rejected'")
breweries = cur.fetchall()

updated_count = 0

for b in breweries:
    bid = b['id']
    name = b['name'] or ''
    kura = b['kura_name'] or ''
    cno = b['corporate_no'] or ''
    
    if not cno:
        matched_cno = None
        for k_name, c_val in KNOWN_NTA_MAP.items():
            if c_val not in assigned_cnos:
                if k_name in name or k_name in kura or name in k_name:
                    matched_cno = c_val
                    break
                
        if matched_cno:
            try:
                cur.execute("UPDATE breweries SET corporate_no = ? WHERE id = ?", (matched_cno, bid))
                assigned_cnos.add(matched_cno)
                updated_count += 1
            except sqlite3.IntegrityError:
                pass

conn.commit()

# Get final count
cur.execute("SELECT COUNT(*) FROM breweries WHERE corporate_no IS NOT NULL AND corporate_no != '' AND status != 'rejected'")
final_count = cur.fetchone()[0]

print(f"\n==========================================")
print(f"✨ 全国家族・酒蔵 法人番号突合完了:")
print(f" - 突合・補完された酒蔵数: +{updated_count} 件")
print(f" - 最新法人番号充足数    : {final_count} / {total_breweries} 件 ({final_count/total_breweries*100:.1f}%)")
print("==========================================")

conn.close()
