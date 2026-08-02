import os
import sys
import sqlite3
import json
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

CATEGORY_MAP = {
    "tokubetsu_honjozo": "特別本醸造",
    "daiginjo": "大吟醸",
    "junmai_daiginjo": "純米大吟醸",
    "honjozo": "本醸造",
    "junmai_ginjo": "純米吟醸",
    "ginjo": "吟醸",
    "junmai": "純米酒",
    "tokubetsu_junmai": "特別純米",
    "yamahai_junmai": "山廃純米"
}

def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('cp932', errors='replace').decode('cp932'))

def format_ingredients(ing_str):
    if not ing_str:
        return "米(国産)、米麹(国産米)"
    try:
        # JSON配列の場合
        arr = json.loads(ing_str)
        if isinstance(arr, list):
            return ", ".join(arr)
    except:
        pass
    # すでに文字列の場合
    return ing_str.replace("[", "").replace("]", "").replace('"', "").replace("'", "")

def auto_summary_ssi(category):
    cat_lower = category.lower() if category else ""
    if "daiginjo" in cat_lower or "ginjo" in cat_lower or "吟醸" in cat_lower:
        return {
            "ssi_type": "薫酒",
            "body_level": "中間",
            "aroma_level": "華やかフルーティ",
            "comment": "華やかな香りと軽快な味わいが調和した、フルーティで気品ある日本酒です。"
        }
    elif "honjozo" in cat_lower or "本醸造" in cat_lower or "爽" in cat_lower:
        return {
            "ssi_type": "爽酒",
            "body_level": "淡麗辛口",
            "aroma_level": "すっきりおだやか",
            "comment": "軽快でキレの良い味わい。雑味が少なく喉越しが非常にクリアな辛口のお酒です。"
        }
    else:
        return {
            "ssi_type": "醇酒",
            "body_level": "濃醇",
            "aroma_level": "しっかり個性的",
            "comment": "お米本来のふくよかなコクと旨味がしっかりと主張する、芳醇で飲みごたえのある味わいです。"
        }

def migrate():
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
    
    safe_print("移行前データ (sakelia.db) から製品データを取得します...")
    
    query = """
        SELECT 
            p.id as src_pid,
            p.spec_name,
            b.name as brand_name,
            br.name as brewery_name,
            br.address as brewery_address,
            p.category,
            p.polish_ratio,
            p.rice_variety,
            p.yeast,
            p.alcohol,
            p.smv,
            p.acidity,
            p.ingredients,
            p.amino_acidity
        FROM products p
        JOIN brands b ON p.brand_id = b.id
        JOIN breweries br ON b.brewery_id = br.id
    """
    
    src_cursor.execute(query)
    products = src_cursor.fetchall()
    
    product_id_map = {} # {src_product_id: dest_product_id}
    
    safe_print(f"合計 {len(products)} 件のお酒データを移行します...")
    
    for p in products:
        # 重複チェック（同一 spec_name ＆ brewery_name があればスキップ）
        dest_cursor.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name = ?", (p["spec_name"], p["brewery_name"]))
        existing = dest_cursor.fetchone()
        
        if existing:
            dest_pid = existing[0]
            product_id_map[p["src_pid"]] = dest_pid
            safe_print(f"重複スキップ (既に存在します): {p['spec_name']} (ID: {dest_pid})")
            continue
            
        # カテゴリ日本語変換
        jp_category = CATEGORY_MAP.get(p["category"], p["category"] or "特定名称不明")
        
        # 原材料フォーマット
        ingredients_formatted = format_ingredients(p["ingredients"])
        
        # 精米歩合
        polish_str = f"{p['polish_ratio']}%" if p["polish_ratio"] else "非公開"
        
        # 日本酒度
        smv_val = p["smv"]
        smv_str = f"+{smv_val}" if smv_val is not None and smv_val > 0 else (str(smv_val) if smv_val is not None else "非公開")
        
        # 酸度/アミノ酸度
        acidity_str = str(p["acidity"]) if p["acidity"] is not None else "非公開"
        amino_str = str(p["amino_acidity"]) if p["amino_acidity"] is not None else "非公開"
        
        # 味わいサマリー自動算出
        summary = auto_summary_ssi(p["category"] or "")
        
        dest_cursor.execute("""
            INSERT INTO products (
                spec_name, brewery_name, brand_name, category, ingredients, polish_ratio, rice_variety, yeast, alcohol,
                smv, acidity, amino_acidity,
                ssi_type, body_level, aroma_level, comment,
                cropped_image_path_front, cropped_image_path_back,
                status, confidence, source_id, evidence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["spec_name"], p["brewery_name"], p["brand_name"], jp_category, ingredients_formatted, polish_str,
            p["rice_variety"] or "非公開", p["yeast"] or "非公開", p["alcohol"],
            smv_str, acidity_str, amino_str,
            summary["ssi_type"], summary["body_level"], summary["aroma_level"], summary["comment"],
            None, None, # クロップ画像はなし
            "draft", 0.9, "migrated_sakelia", "imported from sakelia.db", datetime.now().isoformat()
        ))
        
        dest_pid = dest_cursor.lastrowid
        product_id_map[p["src_pid"]] = dest_pid
        safe_print(f"インポート完了: {p['spec_name']} (新ID: {dest_pid})")

    # クチコミの移行
    safe_print("口コミデータ (user_flavor_ratings) を移行します...")
    src_cursor.execute("SELECT * FROM user_flavor_ratings")
    ratings = src_cursor.fetchall()
    
    ratings_migrated = 0
    for r in ratings:
        src_pid = r["product_id"]
        dest_pid = product_id_map.get(src_pid)
        
        if not dest_pid:
            continue
            
        # 重複チェック（同一 product_id, user_name, comment があればスキップ）
        user_name = "hitocie" if r["user_id"] == "hitocie" else r["user_id"]
        if not user_name:
            user_name = "一般ユーザー"
            
        dest_cursor.execute("""
            SELECT id FROM user_flavor_ratings 
            WHERE product_id = ? AND user_name = ? AND comment = ?
        """, (dest_pid, user_name, r["comment"]))
        
        if dest_cursor.fetchone():
            continue
            
        dest_cursor.execute("""
            INSERT INTO user_flavor_ratings (
                product_id, user_name, ssi_type, body_level, aroma_level, comment, user_id, created_at, rating_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dest_pid, user_name, r["ssi_type"], r["body_level"], r["aroma_level"], r["comment"],
            r["user_id"] or "dummy_sns_source", r["created_at"] or datetime.now().isoformat(), None
        ))
        ratings_migrated += 1
        
    dest_conn.commit()
    
    src_conn.close()
    dest_conn.close()
    
    safe_print(f"データ移行処理が正常終了しました。({ratings_migrated} 件の口コミをインポート)")
    
    # sake_data.js の再エクスポート
    process_sake.export_to_js()
    safe_print("sake_data.js を再エクスポートしました。")

if __name__ == "__main__":
    migrate()
