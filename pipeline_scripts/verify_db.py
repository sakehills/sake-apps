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

print("=== DB Verification Check ===")
tables = [
    "breweries", "brands", "products", "competitions", "competition_events", 
    "awards", "user_flavor_ratings", "users", "user_profiles", "sources", 
    "brewery_aliases", "merge_candidates", "sake_bottles"
]

for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = cursor.fetchone()[0]
    cursor.execute(f"SELECT * FROM {t} LIMIT 1")
    sample = cursor.fetchone()
    print(f"Table '{t:22}': {cnt:6} records | Sample ID: {sample[0] if sample else 'None'}")

# 簡単な結合クエリチェック
cursor.execute("""
    SELECT p.id, p.brand_name, p.brewery_name, p.category, p.jan_code, p.prefecture
    FROM products p
    WHERE p.jan_code IS NOT NULL AND p.jan_code != ''
    LIMIT 3
""")
print("\nProducts with JAN code sample:")
for row in cursor.fetchall():
    print(" ", row)

# 口コミ・評価の確認
cursor.execute("SELECT COUNT(*), AVG(total_score) FROM user_flavor_ratings")
rating_cnt, avg_score = cursor.fetchone()
print(f"\nUser Flavor Ratings: {rating_cnt} reviews, Avg Total Score: {avg_score:.2f}")

conn.close()
