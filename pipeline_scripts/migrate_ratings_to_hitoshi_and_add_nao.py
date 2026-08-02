import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"Connecting to DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Update existing ratings in user_flavor_ratings to user_name = 'hitoshi'
cursor.execute("UPDATE user_flavor_ratings SET user_name = 'hitoshi'")
updated_ratings = cursor.rowcount
print(f"Updated {updated_ratings} legacy review comments to user_name = 'hitoshi'.")

# 2. Add user 'nao' to users table
cursor.execute("""
    INSERT INTO users (user_id, password, user_name, role, assigned_brewery)
    VALUES ('nao', 'password', 'nao', 'user', NULL)
    ON CONFLICT(user_id) DO UPDATE SET
        password=excluded.password,
        user_name=excluded.user_name,
        role=excluded.role,
        assigned_brewery=excluded.assigned_brewery
""")
print("User 'nao' registered successfully!")

conn.commit()

# Print current users
cursor.execute("SELECT user_id, password, user_name, role FROM users ORDER BY id ASC")
users = cursor.fetchall()
print("\n--- 👤 全登録アカウント一覧 ---")
for u in users:
    print(f" ID: {u[0]:<12} | パスワード: {u[1]:<10} | 名前: {u[2]:<20} | ロール: {u[3]}")

conn.close()
