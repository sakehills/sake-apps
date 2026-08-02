import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"Connecting to DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Clear existing user_profiles
cursor.execute("DELETE FROM user_profiles")

# 2. Insert exactly 2 profiles: hitoshi and nao
profiles = [
    (
        'hitoshi',
        'hitoshi',
        '🍶',
        '純米酒・山廃仕込み・重厚で米の旨味がしっかり乗った無濾過生原酒を愛好。酸のキキとキレの良さを重視。',
        '丁寧かつ情熱的。香りと旨味のバランス、飲み口や後味の余韻を緻密に解説するスタイル。',
        1
    ),
    (
        'nao',
        'nao',
        '🌸',
        'フルーティーな吟醸香・華やかな香りの純米大吟醸やスパークリング酒を好むライト層。飲みやすさ重視。',
        '親しみやすく華やか。フルーティーな香りと甘み、女子会や食事との合わせやすさをレビューするスタイル。',
        0
    )
]

cursor.executemany("""
    INSERT INTO user_profiles (user_name, display_name, avatar_icon, preference_text, writing_style, is_primary)
    VALUES (?, ?, ?, ?, ?, ?)
""", profiles)

conn.commit()
print("Updated user_profiles table: Contains exactly hitoshi and nao!")

cursor.execute("SELECT id, user_name, display_name, avatar_icon, preference_text, writing_style, is_primary FROM user_profiles")
rows = cursor.fetchall()
print("\n--- 👤 管理画面ペルソナ・プロフィール一覧 (全2件) ---")
for r in rows:
    print(f" ID: {r[0]} | ユーザーID: {r[1]:<10} | 表示名: {r[2]:<10} | アイコン: {r[3]} | プライマリ: {r[5]}")
    print(f"   好み: {r[4]}")
    print(f"   文体: {r[5]}\n")

conn.close()
