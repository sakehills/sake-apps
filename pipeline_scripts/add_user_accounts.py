import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")

print(f"Connecting to DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Accounts to add/update
new_users = [
    ('hitoshi', 'hitoshi', 'hitoshi', 'system_admin', None),
    ('user2', 'user2', 'user2', 'user', None),
    ('user3', 'user3', 'user3', 'user', None),
]

for u_id, pwd, u_name, role, brewery in new_users:
    cursor.execute("""
        INSERT INTO users (user_id, password, user_name, role, assigned_brewery)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            password=excluded.password,
            user_name=excluded.user_name,
            role=excluded.role,
            assigned_brewery=excluded.assigned_brewery
    """, (u_id, pwd, u_name, role, brewery))

conn.commit()
print("Added new accounts: hitoshi, user2, user3 successfully!")

# Print all users in DB
cursor.execute("SELECT id, user_id, user_name, role, assigned_brewery FROM users ORDER BY id ASC")
all_users = cursor.fetchall()
print("\n--- 👤 全登録アカウント一覧 ---")
for u in all_users:
    print(f" ID: {u[1]:<12} | パスワード: {u[1]:<12} | 名前: {u[2]:<20} | ロール: {u[3]:<15} | 酒蔵: {u[4] or 'なし'}")

conn.close()
