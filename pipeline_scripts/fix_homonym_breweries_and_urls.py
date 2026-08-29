import os
import sys
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== 🛠️ 同名・類似酒蔵のID紐付け＆公式URL 整合性修正パイプライン ===\n")

# 1. 清水清三郎商店（三重県・作）の公式URL修正
cur.execute("""
    UPDATE breweries
    SET website = 'https://www.zaku.co.jp/'
    WHERE id = 3811 OR name LIKE '%清水清三郎商店%'
""")
print("✅ [URL修正] 清水清三郎商店（作） -> https://www.zaku.co.jp/")

# 2. 和歌山の平和酒造（紀土・鶴梅）への受賞酒ID紐付け修正
cur.execute("SELECT id FROM breweries WHERE name LIKE '%平和酒造%' AND prefecture LIKE '%和歌山%'")
wakayama_heiwa = cur.fetchone()
if wakayama_heiwa:
    w_id = wakayama_heiwa['id']
    cur.execute("""
        UPDATE awards
        SET brewery_id = ?, brewery_name = '平和酒造株式会社'
        WHERE brand_name IN ('紀土', '鶴梅')
    """, (w_id,))
    print(f"✅ [ID整合] 紀土・鶴梅の受賞レコード -> 和歌山・平和酒造 (ID {w_id}) に再紐付け")

# 3. 岐阜の渡辺酒造店（蓬莱）への受賞酒ID紐付け修正
cur.execute("SELECT id FROM breweries WHERE name LIKE '%渡辺酒造店%' AND prefecture LIKE '%岐阜%'")
gifu_watanabe = cur.fetchone()
if gifu_watanabe:
    g_id = gifu_watanabe['id']
    cur.execute("""
        UPDATE awards
        SET brewery_id = ?, brewery_name = '有限会社渡辺酒造店'
        WHERE brand_name = '蓬莱'
    """, (g_id,))
    print(f"✅ [ID整合] 蓬莱の受賞レコード -> 岐阜・渡辺酒造店 (ID {g_id}) に再紐付け")

# 4. 山口の旭酒造（獺祭）への受賞酒ID紐付け修正
cur.execute("SELECT id FROM breweries WHERE name LIKE '%旭酒造%' AND prefecture LIKE '%山口%'")
yamaguchi_asahi = cur.fetchone()
if yamaguchi_asahi:
    y_id = yamaguchi_asahi['id']
    cur.execute("""
        UPDATE awards
        SET brewery_id = ?, brewery_name = '旭酒造株式会社'
        WHERE brand_name = '獺祭'
    """, (y_id,))
    print(f"✅ [ID整合] 獺祭の受賞レコード -> 山口・旭酒造 (ID {y_id}) に再紐付け")

# 5. 山形の高木酒造（十四代・朝日鷹）への受賞酒ID紐付け修正
cur.execute("SELECT id FROM breweries WHERE name LIKE '%高木酒造%' AND prefecture LIKE '%山形%'")
yamagata_takagi = cur.fetchone()
if yamagata_takagi:
    t_id = yamagata_takagi['id']
    cur.execute("""
        UPDATE awards
        SET brewery_id = ?, brewery_name = '高木酒造株式会社'
        WHERE brand_name IN ('十四代', '朝日鷹')
    """, (t_id,))
    print(f"✅ [ID整合] 十四代・朝日鷹の受賞レコード -> 山形・高木酒造 (ID {t_id}) に再紐付け")

# 6. 全酒蔵のURL状況を再監査
cur.execute("""
    SELECT COUNT(*) FROM breweries b
    JOIN awards a ON a.brewery_id = b.id
    WHERE (b.website IS NULL OR b.website = '' OR b.website NOT LIKE 'http%')
""")
missing_url_count = cur.fetchone()[0]
print(f"\n📊 受賞酒蔵の公式URL欠損数: {missing_url_count} 件 (0件で完全整合)")

conn.commit()
conn.close()

# CSVバックアップ自動同期
print("\n🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
