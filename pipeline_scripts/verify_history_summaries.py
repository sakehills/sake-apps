import sqlite3
import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM breweries")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM breweries WHERE description IS NOT NULL AND TRIM(description) != ''")
desc_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM breweries WHERE president_name IS NOT NULL AND TRIM(president_name) != ''")
pres_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM breweries WHERE toji_name IS NOT NULL AND TRIM(toji_name) != ''")
toji_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM breweries WHERE opening_hours IS NOT NULL AND TRIM(opening_hours) != ''")
hours_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM breweries WHERE main_rice_varieties IS NOT NULL AND TRIM(main_rice_varieties) != ''")
rice_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM breweries WHERE brewing_features IS NOT NULL AND TRIM(brewing_features) != ''")
brew_count = cursor.fetchone()[0]

print(f"=== 🏛️ 酒蔵マスター 歴史サマリ & 詳細情報充足度 ===")
print(f"全酒蔵数: {total} 蔵")
print(f"歴史・こだわりサマリ (description): {desc_count}/{total} ({(desc_count/total)*100:.1f}%)")
print(f"代表者名 (president_name): {pres_count}/{total} ({(pres_count/total)*100:.1f}%)")
print(f"杜氏・醸造責任者 (toji_name): {toji_count}/{total} ({(toji_count/total)*100:.1f}%)")
print(f"直売所営業時間 (opening_hours): {hours_count}/{total} ({(hours_count/total)*100:.1f}%)")
print(f"主な使用酒米 (main_rice_varieties): {rice_count}/{total} ({(rice_count/total)*100:.1f}%)")
print(f"醸造特徴 (brewing_features): {brew_count}/{total} ({(brew_count/total)*100:.1f}%)")

print("\n--- 🌟 主要酒蔵の歴史サマリ サンプル抽出 ---")
sample_ids = [1, 29, 100, 500, 1000, 1500]
cursor.execute(f"SELECT id, name, prefecture, founded_year, founded_era, description FROM breweries WHERE id IN ({','.join(map(str, sample_ids))})")
for r in cursor.fetchall():
    print(f"\n[{r[0]}] {r[1]} ({r[2]}) 創業: {r[3]}年 ({r[4]})")
    print(f"  📝 歴史サマリ: {r[5]}")

conn.close()
