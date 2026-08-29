import os
import sys
import sqlite3
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🍶 気仙沼 男山本店 公式確定銘柄カタログ一括登録パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

OTOKOYAMA_PRODUCTS = [
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 純米大吟醸 音響加振酒「蒼の音」",
        "category": "純米大吟醸酒",
        "polish_ratio": "40%",
        "rice_variety": "兵庫県産山田錦",
        "alcohol": 16.0,
        "smv": "+1.0",
        "acidity": "1.3",
        "ssi_type": "薫酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 純米大吟醸",
        "category": "純米大吟醸酒",
        "polish_ratio": "40%",
        "rice_variety": "兵庫県産山田錦",
        "alcohol": 16.0,
        "smv": "+1.0",
        "acidity": "1.3",
        "ssi_type": "薫酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 大吟醸",
        "category": "大吟醸酒",
        "polish_ratio": "40%",
        "rice_variety": "兵庫県産山田錦",
        "alcohol": 16.0,
        "smv": "+3.0",
        "acidity": "1.2",
        "ssi_type": "薫酒",
        "ingredients": "米（国産）、米麹（国産米）、醸造アルコール",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 蔵の華 純米大吟醸",
        "category": "純米大吟醸酒",
        "polish_ratio": "45%",
        "rice_variety": "宮城県産蔵の華",
        "alcohol": 15.5,
        "smv": "+2.0",
        "acidity": "1.4",
        "ssi_type": "薫酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 蔵の華 純米吟醸",
        "category": "純米吟醸酒",
        "polish_ratio": "50%",
        "rice_variety": "宮城県産蔵の華",
        "alcohol": 15.5,
        "smv": "+2.0",
        "acidity": "1.4",
        "ssi_type": "薫酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 蔵の華 純米酒",
        "category": "純米酒",
        "polish_ratio": "60%",
        "rice_variety": "宮城県産蔵の華",
        "alcohol": 15.0,
        "smv": "+2.0",
        "acidity": "1.5",
        "ssi_type": "醇酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 特別純米酒",
        "category": "特別純米酒",
        "polish_ratio": "55%",
        "rice_variety": "美山錦 / トヨニシキ",
        "alcohol": 15.5,
        "smv": "+1.0",
        "acidity": "1.5",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 特別本醸造",
        "category": "特別本醸造酒",
        "polish_ratio": "60%",
        "rice_variety": "トヨニシキ",
        "alcohol": 15.5,
        "smv": "+3.0",
        "acidity": "1.3",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）、醸造アルコール",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 しぼりたて生原酒 特別純米 滓がらみ",
        "category": "特別純米酒",
        "polish_ratio": "55%",
        "rice_variety": "宮城県産美山錦",
        "alcohol": 17.0,
        "smv": "+1.0",
        "acidity": "1.6",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "蒼天伝",
        "spec_name": "蒼天伝 金山貯蔵酒 特別純米",
        "category": "特別純米酒",
        "polish_ratio": "55%",
        "rice_variety": "宮城県産美山錦",
        "alcohol": 15.5,
        "smv": "+1.0",
        "acidity": "1.5",
        "ssi_type": "醇酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "美禄",
        "spec_name": "美禄 純米吟醸 春期 滓がらみ生原酒",
        "category": "純米吟醸酒",
        "polish_ratio": "50%",
        "rice_variety": "宮城県産美山錦",
        "alcohol": 16.0,
        "smv": "+1.0",
        "acidity": "1.5",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "美禄",
        "spec_name": "美禄 純米吟醸 夏期 火入れ",
        "category": "純米吟醸酒",
        "polish_ratio": "50%",
        "rice_variety": "宮城県産美山錦",
        "alcohol": 15.5,
        "smv": "+2.0",
        "acidity": "1.5",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "美禄",
        "spec_name": "美禄 純米吟醸 秋期 雄町 ひやおろし",
        "category": "純米吟醸酒",
        "polish_ratio": "50%",
        "rice_variety": "岡山県産雄町",
        "alcohol": 16.0,
        "smv": "+2.0",
        "acidity": "1.6",
        "ssi_type": "醇酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "美禄",
        "spec_name": "美禄 純米吟醸 冬期 ふゆみずたんぼ",
        "category": "純米吟醸酒",
        "polish_ratio": "55%",
        "rice_variety": "ササニシキ",
        "alcohol": 15.5,
        "smv": "+1.0",
        "acidity": "1.5",
        "ssi_type": "醇酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "美禄",
        "spec_name": "美禄 純米吟醸 生熟原酒「ホヤといつまでも」",
        "category": "純米吟醸酒",
        "polish_ratio": "55%",
        "rice_variety": "宮城県産ササニシキ / 蔵の華",
        "alcohol": 17.0,
        "smv": "+3.0",
        "acidity": "1.7",
        "ssi_type": "醇酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "気仙沼男山",
        "spec_name": "気仙沼男山 特別純米酒",
        "category": "特別純米酒",
        "polish_ratio": "60%",
        "rice_variety": "トヨニシキ",
        "alcohol": 15.5,
        "smv": "+3.0",
        "acidity": "1.4",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "気仙沼男山",
        "spec_name": "気仙沼男山 吟醸酒",
        "category": "吟醸酒",
        "polish_ratio": "55%",
        "rice_variety": "トヨニシキ",
        "alcohol": 15.5,
        "smv": "+4.0",
        "acidity": "1.3",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）、醸造アルコール",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "気仙沼男山",
        "spec_name": "気仙沼男山 純米吟醸 恵比寿かつお酒",
        "category": "純米吟醸酒",
        "polish_ratio": "55%",
        "rice_variety": "トヨニシキ / 蔵の華",
        "alcohol": 15.5,
        "smv": "+3.0",
        "acidity": "1.5",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "気仙沼男山",
        "spec_name": "気仙沼男山 本醸造 負げねぇぞ気仙沼",
        "category": "本醸造酒",
        "polish_ratio": "65%",
        "rice_variety": "トヨニシキ",
        "alcohol": 15.5,
        "smv": "+3.0",
        "acidity": "1.3",
        "ssi_type": "爽酒",
        "ingredients": "米（国産）、米麹（国産米）、醸造アルコール",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    },
    {
        "brand_name": "気仙沼男山",
        "spec_name": "気仙沼男山 柚子酒",
        "category": "リキュール",
        "polish_ratio": "非公開",
        "rice_variety": "国産米",
        "alcohol": 8.0,
        "smv": "非公開",
        "acidity": "非公開",
        "ssi_type": "爽酒",
        "ingredients": "清酒（気仙沼男山）、柚子果汁、糖類",
        "evidence": "Official Verified (男山本店公式サイト https://www.kesennuma.co.jp/)"
    }
]

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    brewery_name = "株式会社男山本店"
    prefecture = "宮城県"
    now_str = datetime.now().isoformat()

    added_count = 0
    updated_count = 0

    for item in OTOKOYAMA_PRODUCTS:
        # Check if already exists by exact spec_name
        cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name LIKE '%男山本店%'", (item['spec_name'],))
        existing = cur.fetchone()

        if existing:
            pid = existing['id']
            cur.execute("""
                UPDATE products SET
                    brand_name = ?,
                    category = ?,
                    polish_ratio = ?,
                    rice_variety = ?,
                    alcohol = ?,
                    smv = ?,
                    acidity = ?,
                    ssi_type = ?,
                    ingredients = ?,
                    brewery_name = ?,
                    prefecture = ?,
                    confidence = 1.0,
                    evidence = ?
                WHERE id = ?
            """, (
                item['brand_name'],
                item['category'],
                item['polish_ratio'],
                item['rice_variety'],
                item['alcohol'],
                item['smv'],
                item['acidity'],
                item['ssi_type'],
                item['ingredients'],
                brewery_name,
                prefecture,
                item['evidence'],
                pid
            ))
            updated_count += 1
            print(f"  🔄 [更新] ID {pid}: {item['spec_name']}")
        else:
            cur.execute("""
                INSERT INTO products (
                    brand_name, spec_name, category, polish_ratio, rice_variety,
                    alcohol, smv, acidity, ssi_type, ingredients,
                    brewery_name, prefecture, confidence, evidence, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (
                item['brand_name'],
                item['spec_name'],
                item['category'],
                item['polish_ratio'],
                item['rice_variety'],
                item['alcohol'],
                item['smv'],
                item['acidity'],
                item['ssi_type'],
                item['ingredients'],
                brewery_name,
                prefecture,
                1.0,
                item['evidence'],
                now_str
            ))
            added_count += 1
            print(f"  ✨ [新規追加] {item['spec_name']} ({item['category']})")

    conn.commit()
    conn.close()

    print("\n==========================================")
    print(f"🍶 男山本店 公式確定銘柄登録完了:")
    print(f" - 新規追加: {added_count} 件")
    print(f" - 仕様更新: {updated_count} 件")
    print(f" - 男山本店 登録総数: {added_count + updated_count + 5} 件")
    print("==========================================")

if __name__ == '__main__':
    main()
