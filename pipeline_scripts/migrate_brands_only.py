import os
import sys
import sqlite3
from datetime import datetime
import process_sake

# UTF-8対策
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DB = os.path.join(BASE_DIR, "移行前データ", "sakelia.db")
DEST_DB = os.path.join(os.path.dirname(BASE_DIR), "database", os.path.join("..", "database", "sake_database.db"))

def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('cp932', errors='replace').decode('cp932'))

def migrate_brands():
    if not os.path.exists(SRC_DB):
        safe_print("移行元のデータベースが見つかりません。")
        return
    if not os.path.exists(DEST_DB):
        safe_print("移行先のデータベースが見つかりません。")
        return
        
    src_conn = sqlite3.connect(SRC_DB)
    src_conn.row_factory = sqlite3.Row
    src_cursor = src_conn.cursor()
    
    dest_conn = sqlite3.connect(DEST_DB)
    dest_cursor = dest_conn.cursor()
    
    safe_print("移行元 (sakelia.db) から銘柄名（ブランド）一覧を取得します...")
    
    query = """
        SELECT 
            b.name as brand_name,
            br.name as brewery_name
        FROM brands b
        JOIN breweries br ON b.brewery_id = br.id
    """
    
    src_cursor.execute(query)
    brands = src_cursor.fetchall()
    safe_print(f"移行元ブランドデータ数: {len(brands)} 件")
    
    # 既存のお酒（spec_name, brewery_name のペア）をキャッシュ
    dest_cursor.execute("SELECT spec_name, brewery_name FROM products")
    existing_pairs = set((row[0], row[1]) for row in dest_cursor.fetchall())
    
    insert_data = []
    skipped_count = 0
    
    for b in brands:
        spec_name = b["brand_name"]
        brewery_name = b["brewery_name"]
        
        # 既にDBに同名ペアが存在する場合はスキップ
        if (spec_name, brewery_name) in existing_pairs:
            skipped_count += 1
            continue
            
        insert_data.append((
            spec_name, brewery_name, spec_name, "特定名称不明", "不明", "不明", "不明", "不明", None,
            "非公開", "非公開", "非公開",
            None, None, None, None, # 味わいマップ評価も最初は評価待ち（None）
            None, None, # クロップ画像なし
            "draft", 0.8, "migrated_brands_only", "imported brand names from sakelia.db", datetime.now().isoformat()
        ))
        
        # 重複登録を防ぐため、追加データをexisting_pairsにも追加
        existing_pairs.add((spec_name, brewery_name))

    safe_print(f"重複スキップ数: {skipped_count} 件")
    safe_print(f"新規インポート対象銘柄数: {len(insert_data)} 件")
    
    if insert_data:
        dest_cursor.executemany("""
            INSERT INTO products (
                spec_name, brewery_name, brand_name, category, ingredients, polish_ratio, rice_variety, yeast, alcohol,
                smv, acidity, amino_acidity,
                ssi_type, body_level, aroma_level, comment,
                cropped_image_path_front, cropped_image_path_back,
                status, confidence, source_id, evidence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, insert_data)
        
    dest_conn.commit()
    
    src_conn.close()
    dest_conn.close()
    
    safe_print("データ移行処理が正常終了しました。")
    
    # JSエクスポート
    process_sake.export_to_js()
    safe_print("sake_data.js を再エクスポートしました。")

if __name__ == "__main__":
    migrate_brands()
