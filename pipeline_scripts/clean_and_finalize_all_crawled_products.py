import os
import sys
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== 🧹 全酒蔵 深層クローリングデータの徹底クレンジング＆品質保証 ===")

# クローリングで取得したノイズ（グッズ、ブログ記事タイトル、解説文、注文操作用語など）を削除
cur.execute("""
    DELETE FROM products
    WHERE (
        spec_name LIKE '%ガイド%' OR
        spec_name LIKE '%徹底解説%' OR
        spec_name LIKE '%前掛%' OR
        spec_name LIKE '%腹巻%' OR
        spec_name LIKE '%平盃%' OR
        spec_name LIKE '%石鹸%' OR
        spec_name LIKE '%チョコ%' OR
        spec_name LIKE '%グラス%' OR
        spec_name LIKE '%Tシャツ%' OR
        spec_name LIKE '%タオル%' OR
        spec_name LIKE '%数量を増やす%' OR
        spec_name LIKE '%数量を減らす%' OR
        spec_name LIKE '%無料%' OR
        spec_name LIKE '%税込%' OR
        spec_name LIKE '%円%' OR
        spec_name LIKE '%参加！！%' OR
        spec_name LIKE '%予約開始%' OR
        spec_name LIKE '%発売中！%' OR
        spec_name LIKE '%掲載いただきました%' OR
        spec_name LIKE '%取り上げていただきました%' OR
        spec_name LIKE '%受賞いたしました%' OR
        spec_name LIKE '%選出されました%' OR
        spec_name LIKE '%登場！%' OR
        spec_name LIKE '%のお知らせ%' OR
        spec_name LIKE '%製造断念%' OR
        spec_name LIKE '%紹介されました%' OR
        spec_name LIKE '%ご案内%' OR
        spec_name LIKE '%おすすめの%' OR
        spec_name LIKE '%ですか？%' OR
        spec_name LIKE '%お悩み%' OR
        spec_name LIKE '%常識を覆す%' OR
        spec_name LIKE '%とは？%' OR
        spec_name LIKE '%見る%' OR
        spec_name LIKE '%検索結果%' OR
        spec_name LIKE '%の部%' OR
        spec_name LIKE '%部門%' OR
        spec_name LIKE '%賞%' OR
        spec_name LIKE '%トロフィー%' OR
        spec_name LIKE '%チャレンジ%' OR
        spec_name LIKE '%大会%' OR
        spec_name LIKE '%コンテスト%' OR
        spec_name LIKE '%コンクール%' OR
        spec_name LIKE '%鑑評会%' OR
        spec_name LIKE '%開催%' OR
        spec_name LIKE '%仕込み中%' OR
        spec_name LIKE '%上槽%' OR
        spec_name LIKE '%出荷開始%' OR
        spec_name LIKE '%販売開始%' OR
        spec_name LIKE '%登場%' OR
        spec_name LIKE '%新発売%' OR
        spec_name LIKE '%新登場%' OR
        spec_name LIKE '%NEWS%' OR
        spec_name LIKE '%ニュース%' OR
        spec_name LIKE '%ブログ%' OR
        spec_name LIKE '%イベント%' OR
        spec_name LIKE '%概要%' OR
        spec_name LIKE '%ヒミツ%' OR
        spec_name LIKE '%祭り%' OR
        spec_name LIKE '%休売%' OR
        spec_name LIKE '%おすすめ%' OR
        spec_name LIKE '%ぜひ%' OR
        spec_name LIKE '%お楽しみ%' OR
        spec_name LIKE '%特徴的%' OR
        spec_name LIKE '%素晴らしい%' OR
        spec_name LIKE '%極上%' AND LENGTH(spec_name) > 30 OR
        spec_name LIKE '%こだわり%' OR
        spec_name LIKE '%丁寧%' OR
        spec_name LIKE '%味わい%' AND LENGTH(spec_name) > 25 OR
        spec_name LIKE '%仕込み水を加え%' OR
        spec_name LIKE '%アルコール度数を抑えた%' OR
        spec_name LIKE '%酒粕%' OR
        spec_name LIKE '%粕%' OR
        spec_name = '純米大吟醸' OR
        spec_name = '純米吟醸' OR
        spec_name = '純米酒' OR
        spec_name = '大吟醸' OR
        spec_name = '吟醸' OR
        spec_name = '特別純米' OR
        spec_name = '特別純米酒' OR
        spec_name = '本醸造' OR
        spec_name = '本醸造酒' OR
        spec_name = '普通酒' OR
        spec_name = 'リキュール' OR
        spec_name = 'スパークリング' OR
        spec_name = '本格焼酎' OR
        spec_name = '泡盛' OR
        spec_name = 'クラフトサケ' OR
        spec_name = 'どぶろく' OR
        spec_name = 'しぼりたて' OR
        spec_name = 'ひやおろし' OR
        spec_name = '生原酒' OR
        spec_name = '無濾過生原酒' OR
        spec_name = 'にごり酒'
    ) AND confidence = 1.0 AND evidence LIKE '%Web Crawler%'
""")

cleaned = cur.rowcount
print(f"🧹 ノイズおよび非銘柄テキスト除去件数: {cleaned} 件")

# HTMLエンティティや改行タグのクレンジング (重複安全処理)
cur.execute("SELECT id, spec_name, brewery_name FROM products WHERE spec_name LIKE '%<br%' OR spec_name LIKE '%&nbsp;%' OR spec_name LIKE '%　%'")
rows = cur.fetchall()

for r in rows:
    p_id = r['id']
    old_name = r['spec_name']
    b_name = r['brewery_name']
    clean_name = old_name.replace('<br />', ' ').replace('<br>', ' ').replace('&nbsp;', ' ').replace('　', ' ')
    clean_name = " ".join(clean_name.split()).strip()

    if clean_name != old_name:
        cur.execute("SELECT id FROM products WHERE spec_name = ? AND brewery_name = ? AND id != ?", (clean_name, b_name, p_id))
        dup = cur.fetchone()
        if dup:
            cur.execute("DELETE FROM products WHERE id = ?", (p_id,))
        else:
            cur.execute("UPDATE products SET spec_name = ? WHERE id = ?", (clean_name, p_id))

conn.commit()

cur.execute("SELECT COUNT(*) FROM products")
total_products = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT brewery_name) FROM products")
total_breweries = cur.fetchone()[0]

conn.close()

print(f"\n==========================================")
print(f"🍶 最終クリーン後 登録製品総数: {total_products} 件")
print(f"🏭 紐付け酒蔵総数            : {total_breweries} 蔵")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
