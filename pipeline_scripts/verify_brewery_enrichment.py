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

print("==================== 酒蔵マスター拡充結果 検証 ====================")
cursor.execute("SELECT count(*) FROM breweries")
total_breweries = cursor.fetchone()[0]
print(f"総酒蔵数: {total_breweries} 蔵\n")

# 時代区分の内訳
cursor.execute("SELECT era_category, count(*) FROM breweries GROUP BY era_category ORDER BY count(*) DESC")
print("【時代区分別の酒蔵数】")
for row in cursor.fetchall():
    cat = row[0] if row[0] else "不明"
    print(f"  ・{cat:15}: {row[1]:4} 蔵")

# 老舗（100年以上）の集計
cursor.execute("SELECT count(*) FROM breweries WHERE is_shinise = 1")
shinise_cnt = cursor.fetchone()[0]
print(f"\n創業100年以上の老舗酒蔵: {shinise_cnt} 蔵 ({shinise_cnt/total_breweries*100:.1f}%)")

# 水質硬度の内訳
cursor.execute("SELECT water_hardness_type, count(*) FROM breweries GROUP BY water_hardness_type ORDER BY count(*) DESC")
print("\n【水質硬度別の酒蔵数】")
for row in cursor.fetchall():
    print(f"  ・{row[0]:10}: {row[1]:4} 蔵")

# 主な杜氏流派の集計
cursor.execute("SELECT toji_guild, count(*) FROM breweries GROUP BY toji_guild ORDER BY count(*) DESC LIMIT 10")
print("\n【上位杜氏流派・醸造体制】")
for row in cursor.fetchall():
    print(f"  ・{row[0]:25}: {row[1]:4} 蔵")

# 文化財・見学・試飲・カフェの集計
cursor.execute("SELECT count(*) FROM breweries WHERE is_cultural_property = 1")
cult_cnt = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM breweries WHERE visitation_allowed = 1")
visit_cnt = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM breweries WHERE has_tasting = 1")
taste_cnt = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM breweries WHERE has_cafe_restaurant = 1")
cafe_cnt = cursor.fetchone()[0]

print("\n【観光・施設・文化財の集計】")
print(f"  ・登録有形文化財・歴史的建造物: {cult_cnt:4} 蔵")
print(f"  ・酒蔵見学対応可能蔵        : {visit_cnt:4} 蔵")
print(f"  ・試飲・直売所・角打ち併設  : {taste_cnt:4} 蔵")
print(f"  ・カフェ・レストラン併設    : {cafe_cnt:4} 蔵")

# 有名酒蔵のサンプルチェック
print("\n【代表的酒蔵の拡充データサンプル】")
cursor.execute("""
    SELECT name, prefecture, founded_year, founded_era, era_category, water_source_name, water_hardness_type, toji_guild, tour_info, is_cultural_property
    FROM breweries
    WHERE name IN ('白鶴酒造', '八海醸造', '旭酒造', '新政酒造', '末廣酒造', '月桂冠', '平和酒造') OR name_norm IN ('白鶴酒造', '八海醸造', '旭酒造', '新政酒造', '末廣酒造', '月桂冠', '平和酒造')
    LIMIT 7
""")
for r in cursor.fetchall():
    print(f"\n[蔵名]: {r[0]} ({r[1]})")
    print(f"  - 創業: {r[2]}年 ({r[3]} / {r[4]})")
    print(f"  - 仕込み水: {r[5]} (硬度: {r[6]})")
    print(f"  - 杜氏流派: {r[7]}")
    print(f"  - 見学・文化財: {r[8]} | 文化財フラグ: {r[9]}")

conn.close()
