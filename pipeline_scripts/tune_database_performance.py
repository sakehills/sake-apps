import os
import sqlite3
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== ⚡ Creating SQLite Indexes for Ultra High Performance ===")
print(f"DB Path: {DB_PATH}\n")

start_t = time.time()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_products_brewery ON products(brewery_name);",
    "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_name);",
    "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);",
    "CREATE INDEX IF NOT EXISTS idx_products_ssi ON products(ssi_type);",
    "CREATE INDEX IF NOT EXISTS idx_awards_product ON awards(product_id);",
    "CREATE INDEX IF NOT EXISTS idx_ratings_product ON user_flavor_ratings(product_id);",
    "CREATE INDEX IF NOT EXISTS idx_breweries_name ON breweries(name);",
    "CREATE INDEX IF NOT EXISTS idx_breweries_status ON breweries(status);",
]

for idx_sql in indexes:
    cur.execute(idx_sql)
    print(f" Executed: {idx_sql}")

conn.commit()

# Optimize SQLite WAL & PRAGMA
cur.execute("PRAGMA journal_mode=WAL;")
cur.execute("PRAGMA synchronous=NORMAL;")
cur.execute("PRAGMA cache_size=-64000;") # 64MB Cache
conn.commit()

elapsed = (time.time() - start_t) * 1000
print(f"\n==========================================")
print(f"✨ SQLite DB インデックス作成 ＆ WAL最適化完了 ({elapsed:.1f} ms)")
print("==========================================")

conn.close()
