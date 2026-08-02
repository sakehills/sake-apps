import os
import sys
import sqlite3
import process_sake

# UTF-8 出力対策
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database", os.path.join("..", "database", "sake_database.db"))

# 酒蔵や販売サイト等の公開情報を元にした、欠損スペックの補完マップ
SPEC_COMPLEMENT_DATA = {
    "Beau Michelle Snow fantasy in Summer": {
        "smv": "-10.0",
        "acidity": "3.0",
        "amino_acidity": "非公開",
        "rice_variety": "長野県産美山錦",
        "yeast": "自社培養酵母"
    },
    "浪の音 玲瓏 -レイロウ- Leiro": {
        "smv": "+3.0",
        "acidity": "1.4",
        "amino_acidity": "非公開",
        "rice_variety": "山田錦 / 白鶴錦",
        "yeast": "非公開"
    },
    "越の初梅 元祖 雪中貯蔵酒": {
        "smv": "+3.0",
        "acidity": "1.4",
        "amino_acidity": "1.2",
        "rice_variety": "新潟県産五百万石",
        "yeast": "非公開"
    },
    "け・せら・せら Ikekame": {
        "smv": "-2.0",
        "acidity": "1.8",
        "amino_acidity": "非公開",
        "rice_variety": "夢一献",
        "yeast": "非公開"
    },
    "廣戸川 特別純米": {
        "smv": "+1.0",
        "acidity": "1.5",
        "amino_acidity": "1.1",
        "rice_variety": "福島県産夢の香",
        "yeast": "うつくしま夢酵母"
    },
    "正雪 これだれ TASHINAMI": {
        "smv": "+3.0",
        "acidity": "1.3",
        "amino_acidity": "1.0",
        "rice_variety": "誉富士 / 吟ぎんが",
        "yeast": "静岡酵母 (HD-1)"
    },
    "風の森 雄町 807": {
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "rice_variety": "奈良県産雄町",
        "yeast": "7号系酵母"
    },
    "風の森 CHALLENGE EDITION TYPE 2": {
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "rice_variety": "奈良県産秋津穂",
        "yeast": "非公開"
    },
    "風の森 露葉風 807": {
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "rice_variety": "奈良県産露葉風",
        "yeast": "7号系酵母"
    },
    "風の森 秋津穂 657": {
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "rice_variety": "奈良県産秋津穂",
        "yeast": "7号系酵母"
    },
    "風の森 秋津穂 507": {
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "rice_variety": "奈良県産秋津穂",
        "yeast": "7号系酵母"
    },
    "あべ 青文字": {
        "smv": "+2.0",
        "acidity": "1.8",
        "amino_acidity": "非公開",
        "rice_variety": "新潟県産米",
        "yeast": "非公開"
    },
    "あべ REGULUS 2025": {
        "smv": "-15.0",
        "acidity": "3.5",
        "amino_acidity": "非公開",
        "rice_variety": "新潟県産コシヒカリ",
        "yeast": "非公開"
    },
    "あべ REGULUS 2024": {
        "smv": "-15.0",
        "acidity": "3.5",
        "amino_acidity": "非公開",
        "rice_variety": "新潟県産コシヒカリ",
        "yeast": "非公開"
    },
    "あべ REGULUS 2023": {
        "smv": "-12.0",
        "acidity": "3.3",
        "amino_acidity": "非公開",
        "rice_variety": "新潟県産コシヒカリ",
        "yeast": "非公開"
    },
    "浜娘 岩手限定生酛純米酒": {
        "smv": "+3.0",
        "acidity": "1.6",
        "amino_acidity": "1.3",
        "rice_variety": "岩手県産米",
        "yeast": "蔵内培養協会6号"
    },
    "みむろ杉 みんなのさがのう": {
        "smv": "+1.0",
        "acidity": "1.5",
        "amino_acidity": "非公開",
        "rice_variety": "奈良県産露葉風",
        "yeast": "非公開"
    },
    "雅楽代 薄緑": {
        "smv": "+1.0",
        "acidity": "1.6",
        "amino_acidity": "非公開",
        "rice_variety": "佐渡産五百万石",
        "yeast": "非公開"
    },
    "MIYASAKA 美山錦": {
        "smv": "+1.0",
        "acidity": "1.6",
        "amino_acidity": "非公開",
        "rice_variety": "長野県産美山錦",
        "yeast": "7号酵母"
    },
    "末廣 伝承山廃純米": {
        "smv": "+1.5",
        "acidity": "1.5",
        "amino_acidity": "1.3",
        "rice_variety": "会津産契約栽培米",
        "yeast": "末廣酵母"
    },
    "東光 純米吟醸 原酒": {
        "smv": "-1.0",
        "acidity": "1.5",
        "amino_acidity": "1.2",
        "rice_variety": "山形県産出羽の里",
        "yeast": "山形酵母"
    },
    "秋の田 純米吟醸": {
        "smv": "+2.0",
        "acidity": "1.4",
        "amino_acidity": "1.1",
        "rice_variety": "会津産五百万石",
        "yeast": "会津酵母"
    },
    "山和 特別純米 60": {
        "smv": "+3.0",
        "acidity": "1.6",
        "amino_acidity": "1.2",
        "rice_variety": "宮城県産蔵の華",
        "yeast": "宮城マイ酵母"
    },
    "一ノ蔵 芳吟": {
        "smv": "-2.0",
        "acidity": "1.4",
        "amino_acidity": "1.0",
        "rice_variety": "トヨニシキ",
        "yeast": "自社開発酵母"
    },
    "黄金澤 吟のいろは 純米吟醸": {
        "smv": "+1.0",
        "acidity": "1.6",
        "amino_acidity": "1.2",
        "rice_variety": "宮城県産吟のいろは",
        "yeast": "宮城酵母 (MY3102)"
    },
    "真澄 湧水仕込 純米酒": {
        "smv": "+2.0",
        "acidity": "1.5",
        "amino_acidity": "非公開",
        "rice_variety": "美山錦 / ひとごこち",
        "yeast": "7号酵母"
    },
    "利守 赤磐雄町 特別純米酒": {
        "smv": "+3.0",
        "acidity": "1.6",
        "amino_acidity": "1.3",
        "rice_variety": "岡山県赤磐産雄町",
        "yeast": "協会9号酵母"
    },
    "開運 純米吟醸": {
        "smv": "+3.0",
        "acidity": "1.4",
        "amino_acidity": "1.1",
        "rice_variety": "兵庫県特A地区産山田錦",
        "yeast": "静岡酵母"
    },
    "関娘 山廃仕込 純米酒": {
        "smv": "+1.5",
        "acidity": "1.5",
        "amino_acidity": "1.2",
        "rice_variety": "日本晴 / 五百万石",
        "yeast": "協会701号"
    }
}

def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('cp932', errors='replace').decode('cp932'))

def main():
    if not os.path.exists(DB_PATH):
        safe_print("データベースファイルが見つかりません。")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    safe_print("Web情報を元に、日本酒度・酸度・アミノ酸度等のスペック欠損値を補完・更新します...")
    
    complemented_count = 0
    
    for spec_name, specs in SPEC_COMPLEMENT_DATA.items():
        cursor.execute("SELECT id FROM products WHERE spec_name = ?", (spec_name,))
        row = cursor.fetchone()
        
        if row:
            pid = row[0]
            cursor.execute("""
                UPDATE products SET
                    smv = ?,
                    acidity = ?,
                    amino_acidity = ?,
                    rice_variety = ?,
                    yeast = ?
                WHERE id = ?
            """, (specs["smv"], specs["acidity"], specs["amino_acidity"], specs["rice_variety"], specs["yeast"], pid))
            complemented_count += 1
            safe_print(f"補完完了: {spec_name} (ID: {pid})")
            
    conn.commit()
    conn.close()
    
    safe_print(f"合計 {complemented_count} 件のスペックデータを補完しました。")
    
    # JSエクスポート
    process_sake.export_to_js()
    safe_print("JSファイルを再ビルドしました。")

if __name__ == "__main__":
    main()
