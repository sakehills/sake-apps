import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🥃 焼酎・泡盛 ＆ クラフトサケ 超大拡張 パイプライン開始 ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# List of rich Shochu, Awamori, and Craft Sake catalog data
items = [
    # --- 1. プレミア芋焼酎 ---
    ("森伊蔵", "有限会社森伊蔵酒造", "森伊蔵", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "ロック・湯割り"),
    ("魔王", "白玉醸造合名会社", "魔王", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "ロック・水割り"),
    ("村尾", "村尾酒造合資会社", "村尾", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "湯割り・ロック"),
    ("伊佐美", "甲斐商店", "伊佐美", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "湯割り"),
    ("佐藤 黒麹仕込", "佐藤酒造有限会社", "佐藤", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "ロック・湯割り"),
    ("佐藤 白麹仕込", "佐藤酒造有限会社", "佐藤", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "水割り・ロック"),
    ("富乃宝山", "西酒造株式会社", "富乃宝山", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "ロック・ハイボール"),
    ("吉兆宝山", "西酒造株式会社", "吉兆宝山", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "湯割り"),
    ("DAIYAME (だいやめ)", "濵田酒造株式会社", "DAIYAME", "本格芋焼酎(ライチ香)", 25.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "強炭酸割り・ハイボール"),
    ("三岳", "三岳酒造株式会社", "三岳", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "湯割り・水割り"),
    ("黒霧島EX", "霧島酒造株式会社", "黒霧島", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "ロック・湯割り"),
    ("赤霧島", "霧島酒造株式会社", "赤霧島", "本格芋焼酎(紫芋)", 25.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "ロック・水割り"),
    ("晴耕雨読", "佐多宗二商店", "晴耕雨読", "本格芋焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "湯割り"),

    # --- 2. プレミアム麦焼酎 ---
    ("兼八", "四ツ谷酒造有限会社", "兼八", "本格麦焼酎(香ばし焦がし)", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "ロック・湯割り"),
    ("兼八 原酒", "四ツ谷酒造有限会社", "兼八", "本格麦焼酎原酒", 42.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "ストレート・ロック"),
    ("百年の孤独", "株式会社黒木本店", "百年の孤独", "長期樽貯蔵本格麦焼酎", 40.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "ハイボール・水割り"),
    ("中々", "株式会社黒木本店", "中々", "本格麦焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "ロック・水割り"),
    ("吉四六", "二階堂酒造有限会社", "吉四六", "本格麦焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "ロック・湯割り"),
    ("神の河", "薩摩酒造株式会社", "神の河", "長期樫樽貯蔵麦焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "ハイボール・ロック"),
    ("壱岐スーパーゴールド22", "玄海酒造株式会社", "壱岐", "樫樽貯蔵本格麦焼酎", 22.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "ロック・水割り"),

    # --- 3. 米焼酎 ＆ 黒糖 ＆ 泡盛 ---
    ("鳥飼", "株式会社鳥飼酒造", "鳥飼", "吟香本格米焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "ロック・オンザロック"),
    ("獺祭 焼酎", "旭酒造株式会社", "獺祭", "清酒粕本格焼酎", 39.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "ストレート・ロック"),
    ("よろしく千萬あるべし", "八海醸造株式会社", "八海山", "吟醸粕取本格米焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "水割り・ハイボール"),
    ("朝日", "朝日酒造株式会社", "朝日", "本格黒糖焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "湯割り・ロック"),
    ("れんと", "開運酒造株式会社", "れんと", "音響熟成黒糖焼酎", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "水割り"),
    ("残波 ホワイト", "比嘉酒造株式会社", "残波", "本格泡盛", 25.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "水割り・ソーダ割り"),
    ("残波 ブラック", "比嘉酒造株式会社", "残波", "本格泡盛", 30.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "ロック"),
    ("瑞泉 古酒43度", "瑞泉酒造株式会社", "瑞泉", "琉球泡盛古酒", 43.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "ストレート・ロック"),
    ("久米島の久米仙", "株式会社久米島の久米仙", "久米仙", "琉球泡盛", 30.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "水割り"),
    ("春雨 カリー", "宮里酒造所", "春雨", "琉球泡盛", 30.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "ストレート・ロック"),

    # --- 4. 新世代クラフトサケ (Craft Sake All-Stars) ---
    ("WAKAZE 三軒茶屋ボタニカルサケ", "株式会社WAKAZE", "WAKAZE", "クラフトサケ(ボタニカル)", 13.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "冷酒(10℃)"),
    ("WAKAZE FONTAINEBLEAU (Paris)", "WAKAZE PARIS", "WAKAZE", "クラフトサケ(フランス醸造)", 13.5, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "冷酒(10℃)・ワイングラス"),
    ("WAKAZE RED WINE BARREL", "株式会社WAKAZE", "WAKAZE", "赤ワイン樽熟成クラフトサケ", 14.0, "/cropped_images/placeholder_liqueur.jpg", "熟酒", "常温(15℃)"),
    ("稲とアガベ Craft", "稲とアガベ株式会社", "稲とアガベ", "クラフトサケ(アガベシロップ)", 14.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "冷酒(8℃)"),
    ("稲とホップ", "稲とアガベ株式会社", "稲とホップ", "クラフトサケ(ホップ醸造)", 13.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "冷酒(5℃)"),
    ("稲とリンゴ", "稲とアガベ株式会社", "稲とリンゴ", "クラフトサケ(シードル風)", 12.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "冷酒(8℃)"),
    ("haccoba 叙情のスパークリング", "株式会社haccoba", "haccoba", "発泡クラフトサケ", 12.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "雪冷え(5℃)"),
    ("haccoba 発酵ホップサケ", "株式会社haccoba", "haccoba", "クラフトサケ(Hop Sake)", 13.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "冷酒(10℃)"),
    ("LIBROM あまおう Craft Sake", "株式会社LIBROM", "LIBROM", "クラフトサケ(あまおう苺)", 11.0, "/cropped_images/placeholder_liqueur.jpg", "薫酒", "冷酒(8℃)"),
    ("LIBROM レモンバーベナ Craft", "株式会社LIBROM", "LIBROM", "ボタニカルクラフトサケ", 12.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "雪冷え(5℃)"),
    ("寺田本家 自然酒発泡どぶろく", "株式会社寺田本家", "寺田本家", "生酛無農薬どぶろく", 11.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "雪冷え(5℃)"),
    ("木戸泉 どぶろくクラフト", "木戸泉酒造株式会社", "木戸泉", "高温山廃仕込みどぶろく", 14.0, "/cropped_images/placeholder_liqueur.jpg", "醇酒", "冷酒(10℃)"),
    ("飛良泉 FLYING KANPAI", "株式会社飛良泉本舗", "飛良泉", "山廃クラフトサケ", 13.0, "/cropped_images/placeholder_liqueur.jpg", "爽酒", "涼冷え(15℃)")
]

added_count = 0
for spec, bw, brand, cat, alc, img, ssi, temp in items:
    # Check if exists
    cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name = ?", (spec, bw))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO products (spec_name, brewery_name, brand_name, category, alcohol, cropped_image_path_front, ssi_type, serving_temperature, status, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'verified', 0.98)
        """, (spec, bw, brand, cat, alc, img, ssi, temp))
        added_count += 1

conn.commit()

# Total Shochu & Craft Sake count
cur.execute("""
    SELECT COUNT(*) 
    FROM products 
    WHERE category LIKE '%焼酎%' 
       OR category LIKE '%クラフト%' 
       OR category LIKE '%泡盛%' 
       OR category LIKE '%その他の醸造酒%'
       OR spec_name LIKE '%焼酎%'
       OR spec_name LIKE '%クラフト%'
       OR spec_name LIKE '%泡盛%'
""")

total_sc = cur.fetchone()[0]

print("==========================================")
print("✨ 焼酎・泡盛 ＆ クラフトサケ 超大拡張完了！")
print(f" - 今回追加された新規プレミアム名醸品 : {added_count} 件")
print(f" - 焼酎・泡盛・クラフトサケ 総掲載数 : {total_sc} 件")
print("==========================================")

conn.close()
