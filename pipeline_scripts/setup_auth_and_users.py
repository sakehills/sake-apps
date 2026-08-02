import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")

print(f"Connecting to DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    user_name TEXT NOT NULL,
    role TEXT NOT NULL,
    assigned_brewery TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

# Insert initial test users
test_users = [
    ('admin', 'password', 'システム管理者', 'system_admin', None),
    ('dassai_admin', 'password', '獺祭(旭酒造) 管理者', 'brewery_admin', '旭酒造'),
    ('hakkai_admin', 'password', '八海山(八海醸造) 管理者', 'brewery_admin', '八海醸造'),
    ('user1', 'password', '日本酒ファン太郎', 'user', None),
]

inserted_count = 0
for u_id, pwd, u_name, role, brewery in test_users:
    try:
        cursor.execute("""
            INSERT INTO users (user_id, password, user_name, role, assigned_brewery)
            VALUES (?, ?, ?, ?, ?)
        """, (u_id, pwd, u_name, role, brewery))
        inserted_count += 1
    except sqlite3.IntegrityError:
        # User already exists, update info
        cursor.execute("""
            UPDATE users SET password = ?, user_name = ?, role = ?, assigned_brewery = ?
            WHERE user_id = ?
        """, (pwd, u_name, role, brewery, u_id))

conn.commit()
print(f"Users table initialized! Inserted/Updated {len(test_users)} accounts.")

# Display all users
cursor.execute("SELECT id, user_id, user_name, role, assigned_brewery FROM users")
all_u = cursor.fetchall()
print("\n--- 👤 登録済みアカウント一覧 ---")
for u in all_u:
    print(f" ID: {u[1]} | 名前: {u[2]} | ロール: {u[3]} | 担当酒蔵: {u[4] or 'なし'}")

conn.close()
