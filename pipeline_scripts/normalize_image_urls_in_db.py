import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 🖼️ Normalizing All Image URLs in Database to Relative Web Paths ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def clean_path(p):
    if not p: return p
    p_str = str(p).strip()
    idx = p_str.find('cropped_images')
    if idx != -1:
        rel = '/' + p_str[idx:].replace('\\', '/')
        return rel
    return p_str.replace('\\', '/')

# 1. Update products table
cur.execute("SELECT id, cropped_image_path_front, cropped_image_path_back FROM products")
prods = cur.fetchall()

p_updated = 0
for r in prods:
    pid = r['id']
    f_img = r['cropped_image_path_front']
    b_img = r['cropped_image_path_back']
    
    new_f = clean_path(f_img)
    new_b = clean_path(b_img)
    
    if new_f != f_img or new_b != b_img:
        cur.execute("UPDATE products SET cropped_image_path_front = ?, cropped_image_path_back = ? WHERE id = ?", (new_f, new_b, pid))
        p_updated += 1

conn.commit()

# 2. Update user_flavor_ratings table
cur.execute("SELECT id, rating_image, rating_image_2 FROM user_flavor_ratings")
ratings = cur.fetchall()

r_updated = 0
for r in ratings:
    rid = r['id']
    img1 = r['rating_image']
    img2 = r['rating_image_2']
    
    new_1 = clean_path(img1)
    new_2 = clean_path(img2)
    
    if new_1 != img1 or new_2 != img2:
        cur.execute("UPDATE user_flavor_ratings SET rating_image = ?, rating_image_2 = ? WHERE id = ?", (new_1, new_2, rid))
        r_updated += 1

conn.commit()

print(f"==========================================")
print(f"✨ 全画像パスの相対Webパス正規化完了:")
print(f" - products テーブル更新件数          : {p_updated} 件")
print(f" - user_flavor_ratings テーブル更新件数: {r_updated} 件")
print("==========================================")

# Verify sample rows
cur.execute("SELECT id, brand_name, cropped_image_path_front FROM products LIMIT 5")
print("\n--- 📸 正規化後の画像パスサンプル (5件) ---")
for r in cur.fetchall():
    print(f" ID {r['id']}: {r['brand_name']} ➔ {r['cropped_image_path_front']}")

conn.close()
