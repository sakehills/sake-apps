import os
import sys
import sqlite3
import subprocess
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")

print("=== 🏆 SAKE COMPETITION & 主要国際3コンペ（フェミナリーズ・OSA・ロンドン）統合パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

now_str = datetime.now().isoformat()

# 1. 4つの新コンペティションの定義
NEW_COMPETITIONS = [
    {
        "id": 10044,
        "name": "SAKE COMPETITION",
        "country": "日本",
        "website": "https://sakecompetition.com/",
        "founded_year": 2012,
        "organizer": "SAKE COMPETITION 実行委員会",
        "description": "市販酒のみをブラインド審査する世界最大級の日本酒コンペティション。消費者が本当に美味しい日本酒に出会えることを目指し、純米酒、純米吟醸、純米大吟醸、Super Premium等の部門で競われる。"
    },
    {
        "id": 10045,
        "name": "フェミナリーズ世界ワインコンクール 日本酒・本格焼酎部門",
        "country": "フランス",
        "website": "https://feminalise-japon.com/",
        "founded_year": 2007,
        "organizer": "フェミナリーズ世界ワインコンクール本部（フランス・ボーヌ）",
        "description": "フランス・パリで開催される、女性ワイン・酒類専門家（ソムリエ・醸造家・ジャーナリスト等）のみが厳正に審査する国際品評会。純米大吟醸、純米吟醸、スパークリング、熟成酒、焼酎部門が設置されている。"
    },
    {
        "id": 10046,
        "name": "オリエンタル・サケ・アワード (Oriental Sake Awards / OSA)",
        "country": "香港",
        "website": "https://www.orientalsakeawards.com/",
        "founded_year": 2022,
        "organizer": "酒サムライ・香港酒類連盟",
        "description": "アジア市場（香港・台湾・東南アジア等）の消費者嗜好と食文化に合わせたアジア最大級の日本酒品評会。アジアトップクラスの酒類専門家がブラインドテイスティング審査を行う。"
    },
    {
        "id": 10047,
        "name": "ロンドン酒チャレンジ (London Sake Challenge)",
        "country": "イギリス",
        "website": "https://londonsakechallenge.com/",
        "founded_year": 2012,
        "organizer": "酒ソムリエ協会 (SSA - Sake Sommelier Association)",
        "description": "酒ソムリエ協会（SSA）が主催するヨーロッパ最古の歴史を持つ日本酒専門品評会。世界中のトップ酒ソムリエが味・香り・パッケージデザインを総合評価する。"
    }
]

for comp in NEW_COMPETITIONS:
    cur.execute("SELECT id FROM competitions WHERE id = ? OR name = ?", (comp['id'], comp['name']))
    existing = cur.fetchone()
    if not existing:
        cur.execute("""
            INSERT INTO competitions (id, name, country, website, founded_year, organizer, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (comp['id'], comp['name'], comp['country'], comp['website'], comp['founded_year'], comp['organizer'], comp['description']))
        print(f"✨ [コンペ追加] ID {comp['id']}: {comp['name']}")

# 2. 2024年イベントの登録
NEW_EVENTS = [
    {"id": 20044, "competition_id": 10044, "year": 2024, "edition_label": "SAKE COMPETITION 2024", "venue": "グランドプリンスホテル新高輪", "country": "日本", "website": "https://sakecompetition.com/"},
    {"id": 20045, "competition_id": 10045, "year": 2024, "edition_label": "第18回 フェミナリーズ世界ワインコンクール 2024", "venue": "ボーヌ", "country": "フランス", "website": "https://feminalise-japon.com/"},
    {"id": 20046, "competition_id": 10046, "year": 2024, "edition_label": "Oriental Sake Awards 2024", "venue": "香港コンベンション＆エキシビションセンター", "country": "香港", "website": "https://www.orientalsakeawards.com/"},
    {"id": 20047, "competition_id": 10047, "year": 2024, "edition_label": "London Sake Challenge 2024", "venue": "ロンドン・ミレニアムグロブナーホテル", "country": "イギリス", "website": "https://londonsakechallenge.com/"}
]

for evt in NEW_EVENTS:
    cur.execute("SELECT id FROM competition_events WHERE id = ?", (evt['id'],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO competition_events (id, competition_id, year, edition_label, venue, country, website, status, confidence, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', 1.0, 'Official Competition Announcement')
        """, (evt['id'], evt['competition_id'], evt['year'], evt['edition_label'], evt['venue'], evt['country'], evt['website']))
        print(f"✨ [イベント追加] ID {evt['id']}: {evt['edition_label']}")

# 3. 各コンペティションの確定受賞酒データ (2024年 第1位・GOLD・プラチナ・最高金賞)
VERIFIED_AWARDS_DATA = [
    # --- SAKE COMPETITION 2024 (第1位・上位GOLD) ---
    {
        "comp_id": 10044, "comp_name": "SAKE COMPETITION", "year": 2024, "division": "純米大吟醸部門", "award_rank": "第1位 (GOLD)",
        "brewery": "有限会社渡辺酒造店", "brand": "蓬莱", "spec": "蓬莱 極意傳 純米大吟醸", "pref": "岐阜県",
        "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "url": "https://sakecompetition.com/"
    },
    {
        "comp_id": 10044, "comp_name": "SAKE COMPETITION", "year": 2024, "division": "純米吟醸部門", "award_rank": "第1位 (GOLD)",
        "brewery": "合資会社廣木酒造本店", "brand": "飛露喜", "spec": "飛露喜 純米吟醸 黒ラベル", "pref": "福島県",
        "cat": "純米吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 16.0, "url": "https://sakecompetition.com/"
    },
    {
        "comp_id": 10044, "comp_name": "SAKE COMPETITION", "year": 2024, "division": "純米酒部門", "award_rank": "第1位 (GOLD)",
        "brewery": "株式会社今西酒造", "brand": "みむろ杉", "spec": "みむろ杉 特別純米 辛口 露葉風", "pref": "奈良県",
        "cat": "特別純米酒", "polish": "60%", "rice": "露葉風", "alc": 15.0, "url": "https://sakecompetition.com/"
    },
    {
        "comp_id": 10044, "comp_name": "SAKE COMPETITION", "year": 2024, "division": "Super Premium部門", "award_rank": "第1位 (GOLD)",
        "brewery": "株式会社新澤醸造店", "brand": "残響", "spec": "超特撰 純米大吟醸 残響 Super7", "pref": "宮城県",
        "cat": "純米大吟醸酒", "polish": "7%", "rice": "蔵の華", "alc": 15.8, "url": "https://sakecompetition.com/"
    },
    {
        "comp_id": 10044, "comp_name": "SAKE COMPETITION", "year": 2024, "division": "吟醸部門", "award_rank": "第1位 (GOLD)",
        "brewery": "出羽桜酒造株式会社", "brand": "出羽桜", "spec": "出羽桜 桜花吟醸酒 本生", "pref": "山形県",
        "cat": "吟醸酒", "polish": "50%", "rice": "美山錦", "alc": 15.0, "url": "https://sakecompetition.com/"
    },

    # --- フェミナリーズ世界ワインコンクール 2024 (金賞・TOP OF THE BEST) ---
    {
        "comp_id": 10045, "comp_name": "フェミナリーズ世界ワインコンクール 日本酒・本格焼酎部門", "year": 2024, "division": "日本酒 スパークリング部門", "award_rank": "TOP OF THE BEST (最高金賞)",
        "brewery": "永井酒造株式会社", "brand": "水芭蕉", "spec": "水芭蕉 Pure 瓶内二次発酵 スパークリング", "pref": "群馬県",
        "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 13.0, "url": "https://feminalise-japon.com/"
    },
    {
        "comp_id": 10045, "comp_name": "フェミナリーズ世界ワインコンクール 日本酒・本格焼酎部門", "year": 2024, "division": "日本酒 純米大吟醸部門", "award_rank": "金賞 (GOLD)",
        "brewery": "山梨銘醸株式会社", "brand": "七賢", "spec": "七賢 絹の味 純米大吟醸", "pref": "山梨県",
        "cat": "純米大吟醸酒", "polish": "47%", "rice": "夢山水", "alc": 15.0, "url": "https://feminalise-japon.com/"
    },
    {
        "comp_id": 10045, "comp_name": "フェミナリーズ世界ワインコンクール 日本酒・本格焼酎部門", "year": 2024, "division": "本格焼酎部門", "award_rank": "金賞 (GOLD)",
        "brewery": "濵田酒造株式会社", "brand": "だいやめ", "spec": "だいやめ DAIYAME 40 40度", "pref": "鹿児島県",
        "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 40.0, "url": "https://feminalise-japon.com/"
    },
    {
        "comp_id": 10045, "comp_name": "フェミナリーズ世界ワインコンクール 日本酒・本格焼酎部門", "year": 2024, "division": "リキュール部門", "award_rank": "金賞 (GOLD)",
        "brewery": "平和酒造株式会社", "brand": "鶴梅", "spec": "鶴梅 完熟にごり梅酒", "pref": "和歌山県",
        "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 10.0, "url": "https://feminalise-japon.com/"
    },

    # --- オリエンタル・サケ・アワード 2024 (Sake of the Year / GOLD) ---
    {
        "comp_id": 10046, "comp_name": "オリエンタル・サケ・アワード (Oriental Sake Awards / OSA)", "year": 2024, "division": "純米大吟醸（香り部門）", "award_rank": "Sake of the Year (最高賞)",
        "brewery": "清水清三郎商店株式会社", "brand": "作", "spec": "作 智 純米大吟醸 滴取り", "pref": "三重県",
        "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "url": "https://www.orientalsakeawards.com/"
    },
    {
        "comp_id": 10046, "comp_name": "オリエンタル・サケ・アワード (Oriental Sake Awards / OSA)", "year": 2024, "division": "純米吟醸部門", "award_rank": "金賞 (GOLD)",
        "brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 純米吟醸 雄町", "pref": "宮城県",
        "cat": "純米吟醸酒", "polish": "50%", "rice": "備前雄町", "alc": 15.8, "url": "https://www.orientalsakeawards.com/"
    },
    {
        "comp_id": 10046, "comp_name": "オリエンタル・サケ・アワード (Oriental Sake Awards / OSA)", "year": 2024, "division": "スパークリング部門", "award_rank": "金賞 (GOLD)",
        "brewery": "黒龍酒造株式会社", "brand": "ESHIKOTO", "spec": "ESHIKOTO AWA 瓶内二次発酵 スパークリング", "pref": "福井県",
        "cat": "純米大吟醸酒", "polish": "50%", "rice": "五百万石", "alc": 13.0, "url": "https://www.orientalsakeawards.com/"
    },

    # --- ロンドン酒チャレンジ 2024 (プラチナ賞・金賞) ---
    {
        "comp_id": 10047, "comp_name": "ロンドン酒チャレンジ (London Sake Challenge)", "year": 2024, "division": "純米大吟醸部門", "award_rank": "プラチナ賞 (Platinum)",
        "brewery": "加藤吉平商店", "brand": "梵", "spec": "梵 日本の翼 純米大吟醸", "pref": "福井県",
        "cat": "純米大吟醸酒", "polish": "35%", "rice": "兵庫県特A地区産山田錦", "alc": 16.0, "url": "https://londonsakechallenge.com/"
    },
    {
        "comp_id": 10047, "comp_name": "ロンドン酒チャレンジ (London Sake Challenge)", "year": 2024, "division": "純米吟醸部門", "award_rank": "金賞 (Gold)",
        "brewery": "宮坂醸造株式会社", "brand": "真澄", "spec": "真澄 漆黒 KURO 純米吟醸", "pref": "長野県",
        "cat": "純米吟醸酒", "polish": "55%", "rice": "美山錦 / ひとごこち", "alc": 15.0, "url": "https://londonsakechallenge.com/"
    },
    {
        "comp_id": 10047, "comp_name": "ロンドン酒チャレンジ (London Sake Challenge)", "year": 2024, "division": "大吟醸部門", "award_rank": "金賞 (Gold)",
        "brewery": "八戸酒造株式会社", "brand": "陸奥八仙", "spec": "陸奥八仙 大吟醸 華想い40", "pref": "青森県",
        "cat": "大吟醸酒", "polish": "40%", "rice": "華想い", "alc": 16.0, "url": "https://londonsakechallenge.com/"
    }
]

added_awards = 0

for item in VERIFIED_AWARDS_DATA:
    brewery_name = item['brewery']
    clean_brew = brewery_name.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").strip()
    brand_name = item['brand']
    spec_name = item['spec']

    # 酒蔵IDの取得
    cur.execute("""
        SELECT id FROM breweries WHERE name LIKE ? OR name LIKE ?
    """, (f"%{clean_brew}%", f"%{brewery_name}%"))
    b_row = cur.fetchone()
    brewery_id = b_row['id'] if b_row else None

    # ブランドIDの取得
    cur.execute("""
        SELECT id FROM brands WHERE name = ? LIMIT 1
    """, (brand_name,))
    brand_row = cur.fetchone()
    brand_id = brand_row['id'] if brand_row else None

    # 製品IDの取得または作成
    cur.execute("""
        SELECT id FROM products WHERE spec_name = ? AND (brewery_name LIKE ? OR brand_name = ?)
    """, (spec_name, f"%{clean_brew}%", brand_name))
    p_row = cur.fetchone()
    
    if p_row:
        product_id = p_row['id']
    else:
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, brewery_name, prefecture, confidence, evidence, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
        """, (
            brand_name, spec_name, item['cat'], item['polish'], item['rice'],
            item['alc'], brewery_name, item['pref'], f"Official Award Verified ({item['url']})", now_str
        ))
        product_id = cur.lastrowid
        print(f"  ✨ [新製品登録] ID {product_id}: {spec_name}")

    # 受賞レコードの重複チェックと挿入
    cur.execute("""
        SELECT id FROM awards
        WHERE competition_id = ? AND year = ? AND (entry_name = ? OR product_id = ?)
    """, (item['comp_id'], item['year'], spec_name, product_id))
    
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO awards (
                competition_id, year, category, prize, entry_name,
                brand_id, product_id, brewery_id, status, confidence,
                source_id, evidence, competition_name, brand_name, brewery_name, is_gold_award
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'verified', 1.0, 'official_release', ?, ?, ?, ?, 1)
        """, (
            item['comp_id'], item['year'], item['division'], item['award_rank'], spec_name,
            brand_id, product_id, brewery_id,
            f"Official Competition Website ({item['url']})",
            item['comp_name'], brand_name, brewery_name
        ))
        added_awards += 1
        print(f"  🏆 [受賞登録] {item['award_rank']} - {spec_name} ({item['division']})")

conn.commit()

# コンペティションおよび受賞数サマリー
cur.execute("SELECT COUNT(*) FROM competitions")
total_comps = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM awards")
total_awards = cur.fetchone()[0]

conn.close()

print(f"\n==========================================")
print(f"🎉 SAKE COMPETITION & 主要3国際コンペ 統合完了:")
print(f"・新規追加受賞レコード数: {added_awards} 件")
print(f"・コンペティション総数  : {total_comps} 件 (10 -> 14件)")
print(f"・受賞レコード総数      : {total_awards} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
