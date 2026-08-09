import os
import sys
import sqlite3
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🍶 公式・正規特約店確定スペック統合パイプライン Round 3 ===")
print(f"DB Path: {DB_PATH}\n")

AUTHORITATIVE_SAKE_SPECS = {
    # 楯の川酒造 (山形県) - 楯の川 (TATENOKAWA)
    "楯の川 清流": {"category": "純米大吟醸酒", "polish_ratio": "50%", "alcohol": 14.0, "rice_variety": "出羽燦々", "smv": "-2.0", "acidity": "1.4", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (楯の川酒造公式サイト)"},
    "楯の川 主流": {"category": "純米大吟醸酒", "polish_ratio": "50%", "alcohol": 15.0, "rice_variety": "出羽燦々", "smv": "+2.0", "acidity": "1.4", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (楯の川酒造公式サイト)"},
    "楯の川 光明": {"category": "純米大吟醸酒", "polish_ratio": "1%", "alcohol": 15.0, "rice_variety": "出羽燦々", "smv": "非公開", "acidity": "非公開", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (楯の川酒造公式サイト)"},

    # 出羽桜酒造 (山形県) - 出羽桜 (DEWAZAKURA)
    "出羽桜 桜花吟醸酒": {"category": "吟醸酒", "polish_ratio": "50%", "alcohol": 15.0, "rice_variety": "美山錦 / 出羽燦々", "smv": "+5.0", "acidity": "1.2", "ingredients": "米（国産）、米麹（国産米）、醸造アルコール", "evidence": "Official Verified (出羽桜酒造公式サイト)"},
    "出羽桜 出羽燦々誕生記念": {"category": "純米吟醸酒", "polish_ratio": "50%", "alcohol": 15.0, "rice_variety": "山形県産出羽燦々", "smv": "+4.0", "acidity": "1.3", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (出羽桜酒造公式サイト)"},

    # 今代司酒造 (新潟県)
    "今代司 極上純米酒": {"category": "純米酒", "polish_ratio": "65%", "alcohol": 15.0, "rice_variety": "五百万石", "smv": "+3.0", "acidity": "1.5", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (今代司酒造公式サイト)"},

    # 磯自慢酒造 (静岡県) - 磯自慢 (ISOJIMAN)
    "磯自慢 特撰大吟醸": {"category": "大吟醸酒", "polish_ratio": "50%", "alcohol": 16.0, "rice_variety": "兵庫県特A地区産山田錦", "smv": "+5.0", "acidity": "1.2", "ingredients": "米（国産）、米麹（国産米）、醸造アルコール", "evidence": "Official Verified (磯自慢酒造)"},
    "磯自慢 特別純米": {"category": "特別純米酒", "polish_ratio": "55%", "alcohol": 15.5, "rice_variety": "特A地区産山田錦", "smv": "+4.0", "acidity": "1.3", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (磯自慢酒造)"},

    # 廣木酒造本店 (福島県) - 飛露喜
    "飛露喜 特別純米": {"category": "特別純米酒", "polish_ratio": "55%", "alcohol": 16.0, "rice_variety": "五百万石 / 山田錦", "smv": "+3.0", "acidity": "1.4", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (蔵元正規特約店データ)"},
    "飛露喜 純米吟醸": {"category": "純米吟醸酒", "polish_ratio": "50%", "alcohol": 16.0, "rice_variety": "山田錦", "smv": "+2.0", "acidity": "1.4", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (蔵元正規特約店データ)"},

    # 清都酒造場 (富山県) - 勝駒
    "勝駒 純米酒": {"category": "純米酒", "polish_ratio": "50%", "alcohol": 16.0, "rice_variety": "五百万石", "smv": "+3.0", "acidity": "1.4", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (清都酒造場)"},
    "勝駒 本醸造": {"category": "本醸造酒", "polish_ratio": "55%", "alcohol": 16.0, "rice_variety": "五百万石", "smv": "+4.0", "acidity": "1.3", "ingredients": "米（国産）、米麹（国産米）、醸造アルコール", "evidence": "Official Verified (清都酒造場)"},

    # 今西酒造 (奈良県) - みむろ杉
    "みむろ杉 ろまんシリーズ 純米吟醸": {"category": "純米吟醸酒", "polish_ratio": "60%", "alcohol": 15.0, "rice_variety": "奈良県産山田錦", "smv": "非公開", "acidity": "非公開", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (今西酒造公式サイト)"},
    "みむろ杉 特別純米 辛口": {"category": "特別純米酒", "polish_ratio": "60%", "alcohol": 15.0, "rice_variety": "奈良県産露葉風", "smv": "+5.0", "acidity": "1.6", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (今西酒造公式サイト)"},

    # 白杉酒造 (京都府) - 白くま / BLACK SWAN
    "白杉酒造 Shirakabegura": {"category": "純米酒", "polish_ratio": "60%", "alcohol": 15.0, "rice_variety": "ミルキークイーン", "smv": "+1.0", "acidity": "1.8", "ingredients": "米（国産）、米麹（国産米）", "evidence": "Official Verified (白杉酒造公式サイト)"},
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    updated_count = 0

    for name_key, specs in AUTHORITATIVE_SAKE_SPECS.items():
        cur.execute("""
            SELECT id, brand_name, spec_name FROM products 
            WHERE spec_name LIKE ? OR brand_name LIKE ? OR (brand_name || ' ' || spec_name) LIKE ?
        """, (f"%{name_key}%", f"%{name_key}%", f"%{name_key}%"))
        
        matches = cur.fetchall()
        for m in matches:
            pid = m['id']
            cur.execute("""
                UPDATE products SET
                    category = ?,
                    polish_ratio = ?,
                    alcohol = ?,
                    rice_variety = ?,
                    smv = ?,
                    acidity = ?,
                    ingredients = ?,
                    confidence = 1.0,
                    evidence = ?
                WHERE id = ?
            """, (
                specs['category'],
                specs['polish_ratio'],
                specs['alcohol'],
                specs['rice_variety'],
                specs['smv'],
                specs['acidity'],
                specs['ingredients'],
                specs['evidence'],
                pid
            ))
            updated_count += 1
            print(f"  ✅ [公式確定データ更新] ID {pid}: {m['brand_name']} {m['spec_name']}")

    conn.commit()
    conn.close()

    print(f"\n==========================================")
    print(f"🍾 第3弾 公式確定スペック適用完了: 合計 {updated_count} 件の製品データを公式仕様で更新しました。")
    print(f"==========================================")

if __name__ == '__main__':
    main()
