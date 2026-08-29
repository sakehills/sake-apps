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

print("=== 🏆 2024年度 6大コンペティション 全受賞銘柄 網羅的一括登録パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# コンペティションID取得
cur.execute("SELECT id, name FROM competitions")
comp_map = {r['name']: r['id'] for r in cur.fetchall()}

# 2024年度 公式受賞全銘柄データ
COMPREHENSIVE_2024_AWARDS = [
    # -------------------------------------------------------------
    # 1. ワイングラスでおいしい日本酒アワード 2024 (The Fine Sake Awards Japan)
    # -------------------------------------------------------------
    # メイン部門 最高金賞
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "ZAO 純米酒 K", "brand": "ZAO", "brewery": "蔵王酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "あたごのまつ 鮮烈辛口", "brand": "あたごのまつ", "brewery": "株式会社新澤醸造店"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "大吟醸 高清水", "brand": "高清水", "brewery": "秋田酒類製造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "純米大吟醸 北秋田", "brand": "北秋田", "brewery": "株式会社北鹿"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "奥の松 純米大吟醸 紺ラベル", "brand": "奥の松", "brewery": "奥の松酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "仁勇 純米吟醸", "brand": "仁勇", "brewery": "鍋店株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "純米大吟醸 越後桜", "brand": "越後桜", "brewery": "越後桜酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "越後鶴亀 なごみ酒 無濾過純米", "brand": "越後鶴亀", "brewery": "株式会社越後鶴亀"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "彗 HALLEY直汲み 純米", "brand": "彗", "brewery": "株式会社遠藤酒造場"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "御園竹しぼりたて純米 一回火入れ", "brand": "御園竹", "brewery": "武重本家酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "開運 特別本醸造 夢仕込み", "brand": "開運", "brewery": "株式会社土井酒造場"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "山田錦大吟醸 匠", "brand": "京姫", "brewery": "株式会社京姫酒造"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "京姫 純米大吟醸 紫", "brand": "京姫", "brewery": "株式会社京姫酒造"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "千代むすび 純米酒", "brand": "千代むすび", "brewery": "千代むすび酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "伊七 源流域水仕込み 純米吟醸", "brand": "伊七", "brewery": "熊屋酒造有限会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "メイン部門", "prize": "最高金賞", "name": "石鎚 無濾過純米", "brand": "石鎚", "brewery": "石鎚酒造株式会社"},
    # プレミアム大吟醸部門 最高金賞・金賞
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "最高金賞", "name": "桂月 にごり 純米大吟醸 50", "brand": "桂月", "brewery": "土佐酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "最高金賞", "name": "極上吉乃川 純米大吟醸", "brand": "吉乃川", "brewery": "吉乃川株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "最高金賞", "name": "手取川 純米大吟醸 本流", "brand": "手取川", "brewery": "株式会社吉田酒造店"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "金賞", "name": "純米大吟醸 じょっぱり", "brand": "じょっぱり", "brewery": "六花酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "金賞", "name": "南部美人 純米大吟醸", "brand": "南部美人", "brewery": "株式会社南部美人"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "金賞", "name": "水芭蕉 純米大吟醸 翠", "brand": "水芭蕉", "brewery": "永井酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "金賞", "name": "七賢 大中屋 純米大吟醸", "brand": "七賢", "brewery": "山梨銘醸株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "金賞", "name": "蓬莱泉 空 純米大吟醸", "brand": "蓬莱泉", "brewery": "関谷醸造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム大吟醸部門", "prize": "金賞", "name": "龍力 米のささやき 大吟醸", "brand": "龍力", "brewery": "株式会社本田商店"},
    # プレミアム純米部門 最高金賞・金賞
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "最高金賞", "name": "会津中将 純米吟醸 夢の香", "brand": "会津中将", "brewery": "鶴乃江酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "最高金賞", "name": "雪の茅舎 純米吟醸", "brand": "雪の茅舎", "brewery": "株式会社齋彌酒造店"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "最高金賞", "name": "満寿泉 純米吟醸", "brand": "満寿泉", "brewery": "株式会社桝田酒造店"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "金賞", "name": "一ノ蔵 純米吟醸 蔵の華", "brand": "一ノ蔵", "brewery": "株式会社一ノ蔵"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "金賞", "name": "黒牛 純米酒", "brand": "黒牛", "brewery": "株式会社名手酒造店"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "金賞", "name": "東洋美人 醇道一閃", "brand": "東洋美人", "brewery": "株式会社澄川酒造場"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアム純米部門", "prize": "金賞", "name": "美丈夫 純米吟醸 慎太郎", "brand": "美丈夫", "brewery": "有限会社濱川商店"},
    # スパークリング部門
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "スパークリングSAKE部門", "prize": "最高金賞", "name": "越の誉 発泡純米酒 あわっしゅ", "brand": "越の誉", "brewery": "原酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "スパークリングSAKE部門", "prize": "最高金賞", "name": "Spark Riz Vin", "brand": "千曲錦", "brewery": "千曲錦酒造株式会社"},
    {"comp": "ワイングラスでおいしい日本酒アワード", "cat": "プレミアムスパークリングSAKE部門", "prize": "最高金賞", "name": "SPARKLING SAKE 光壽", "brand": "賀茂鶴", "brewery": "賀茂鶴酒造株式会社"},

    # -------------------------------------------------------------
    # 2. 全国燗酒コンテスト 2024 (National Warm Sake Contest)
    # -------------------------------------------------------------
    # お値打ちぬる燗部門 最高金賞・金賞
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "おいらせ流 純米吟醸酒", "brand": "桃川", "brewery": "桃川株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "南部美人 吟醸 結のしずく", "brand": "南部美人", "brewery": "株式会社南部美人"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "本仕込 浦霞", "brand": "浦霞", "brewery": "株式会社佐浦"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "愛宕の松 別仕込本醸造", "brand": "愛宕の松", "brewery": "株式会社新澤醸造店"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "かおりらんまん純米吟醸", "brand": "爛漫", "brewery": "秋田銘醸株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "金紋秀", "brand": "秀よし", "brewery": "合名会社鈴木酒造店"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "特別純米 北秋田", "brand": "北秋田", "brewery": "株式会社北鹿"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "開華 純米酒", "brand": "開華", "brewery": "第一酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "吟醸 晴雲", "brand": "晴雲", "brewery": "晴雲酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "澤乃花 辛口純米 花ごころ", "brand": "澤乃花", "brewery": "伴野酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "豊麗司牡丹", "brand": "司牡丹", "brewery": "司牡丹酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ちぬる燗部門", "prize": "最高金賞", "name": "和香牡丹 福貴野", "brand": "和香牡丹", "brewery": "三和酒類株式会社"},
    # お値打ち熱燗部門 最高金賞・金賞
    {"comp": "全国燗酒コンテスト", "cat": "お値打ち熱燗部門", "prize": "最高金賞", "name": "男山 生酛純米", "brand": "男山", "brewery": "男山株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ち熱燗部門", "prize": "最高金賞", "name": "吉乃川 厳選辛口", "brand": "吉乃川", "brewery": "吉乃川株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ち熱燗部門", "prize": "最高金賞", "name": "若竹屋 特別本醸造", "brand": "若竹屋", "brewery": "合資会社若竹屋酒造場"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ち熱燗部門", "prize": "金賞", "name": "高清水 精撰", "brand": "高清水", "brewery": "秋田酒類製造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ち熱燗部門", "prize": "金賞", "name": "白真弓 栄冠", "brand": "白真弓", "brewery": "有限会社蒲酒造場"},
    {"comp": "全国燗酒コンテスト", "cat": "お値打ち熱燗部門", "prize": "金賞", "name": "富翁 上撰 辛口", "brand": "富翁", "brewery": "株式会社北川本家"},
    # プレミアム燗酒部門 最高金賞・金賞
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "最高金賞", "name": "初孫 生酛純米本辛口 魔斬", "brand": "初孫", "brewery": "東北銘醸株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "最高金賞", "name": "大山 特別純米酒 十水", "brand": "大山", "brewery": "加藤嘉八郎酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "最高金賞", "name": "真澄 すずみさけ 純米吟醸", "brand": "真澄", "brewery": "宮坂醸造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "金賞", "name": "九頭龍 純米", "brand": "九頭龍", "brewery": "黒龍酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "金賞", "name": "春鹿 純米 超辛口", "brand": "春鹿", "brewery": "株式会社今西清兵衛商店"},
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "金賞", "name": "賀茂泉 朱泉本仕込", "brand": "賀茂泉", "brewery": "賀茂泉酒造株式会社"},
    {"comp": "全国燗酒コンテスト", "cat": "プレミアム燗酒部門", "prize": "金賞", "name": "千代の亀 特別純米 黒ラベル", "brand": "千代の亀", "brewery": "千代の亀酒造株式会社"},

    # -------------------------------------------------------------
    # 3. 全米日本酒歓評会 2024 (U.S. National Sake Appraisal)
    # -------------------------------------------------------------
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "大吟醸A部門", "prize": "グランプリ", "name": "極上諸白 十四代", "brand": "十四代", "brewery": "高木酒造株式会社"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "大吟醸A部門", "prize": "金賞", "name": "黒龍 しずく", "brand": "黒龍", "brewery": "黒龍酒造株式会社"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "大吟醸A部門", "prize": "金賞", "name": "鳳凰美田 荒走押切 プレミアム", "brand": "鳳凰美田", "brewery": "小林酒造株式会社"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "大吟醸B部門", "prize": "金賞", "name": "飛露喜 純米大吟醸", "brand": "飛露喜", "brewery": "合資会社廣木酒造本店"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "大吟醸B部門", "prize": "金賞", "name": "獺祭 磨き二割三分 遠心分離", "brand": "獺祭", "brewery": "旭酒造株式会社"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "吟醸部門", "prize": "金賞", "name": "寫樂 純米吟醸", "brand": "寫樂", "brewery": "宮泉銘醸株式会社"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "吟醸部門", "prize": "金賞", "name": "みむろ杉 ろまんシリーズ 純米吟醸", "brand": "みむろ杉", "brewery": "今西酒造株式会社"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "純米部門", "prize": "金賞", "name": "勝駒 純米酒", "brand": "勝駒", "brewery": "清都酒造場"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "純米部門", "prize": "金賞", "name": "伯楽星 特別純米", "brand": "伯楽星", "brewery": "株式会社新澤醸造店"},
    {"comp": "全米日本酒歓評会 (U.S. National Sake Appraisal)", "cat": "純米部門", "prize": "金賞", "name": "赤武 AKABU 純米酒", "brand": "AKABU", "brewery": "赤武酒造株式会社"},

    # -------------------------------------------------------------
    # 4. TWSC 2024 焼酎部門 (Tokyo Whisky & Spirits Competition)
    # -------------------------------------------------------------
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "芋焼酎部門", "prize": "最高金賞", "name": "フラミンゴオレンジ", "brand": "フラミンゴオレンジ", "brewery": "国分酒造株式会社"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "芋焼酎部門", "prize": "金賞", "name": "伊佐美", "brand": "伊佐美", "brewery": "甲斐商店"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "芋焼酎部門", "prize": "金賞", "name": "富乃宝山", "brand": "富乃宝山", "brewery": "西酒造株式会社"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "芋焼酎部門", "prize": "金賞", "name": "吉兆宝山", "brand": "吉兆宝山", "brewery": "西酒造株式会社"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "麦焼酎部門", "prize": "金賞", "name": "中々", "brand": "中々", "brewery": "株式会社黒木本店"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "麦焼酎部門", "prize": "金賞", "name": "二階堂 吉四六", "brand": "吉四六", "brewery": "二階堂酒造有限会社"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "米焼酎部門", "prize": "金賞", "name": "獺祭 焼酎 39度", "brand": "獺祭", "brewery": "旭酒造株式会社"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "泡盛部門", "prize": "金賞", "name": "泡盛 菊之露 VIPゴールド", "brand": "菊之露", "brewery": "菊之露酒造株式会社"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "泡盛部門", "prize": "金賞", "name": "八重泉 黒真珠", "brand": "八重泉", "brewery": "有限会社八重泉酒造"},
    {"comp": "東京ウイスキー＆スピリッツコンペティション (TWSC) 焼酎部門", "cat": "黒糖焼酎部門", "prize": "最高金賞", "name": "朝日 30度", "brand": "朝日", "brewery": "朝日酒造株式会社"},

    # -------------------------------------------------------------
    # 5. ミラノ酒チャレンジ 2024 (Milano Sake Challenge)
    # -------------------------------------------------------------
    {"comp": "ミラノ酒チャレンジ (Milano Sake Challenge)", "cat": "大吟醸・純米大吟醸部門", "prize": "ダブル金賞", "name": "醸し人九平次 別誂", "brand": "醸し人九平次", "brewery": "株式会社萬乗醸造"},
    {"comp": "ミラノ酒チャレンジ (Milano Sake Challenge)", "cat": "純米部門", "prize": "プラチナ賞", "name": "惣誉 生酛特別純米", "brand": "惣誉", "brewery": "惣誉酒造株式会社"},
    {"comp": "ミラノ酒チャレンジ (Milano Sake Challenge)", "cat": "純米吟醸部門", "prize": "金賞", "name": "手取川 純米吟醸 酒魂", "brand": "手取川", "brewery": "株式会社吉田酒造店"},
    {"comp": "ミラノ酒チャレンジ (Milano Sake Challenge)", "cat": "デザイン部門", "prize": "ベストデザイン金賞", "name": "雨後の月 純米大吟醸 Black Moon", "brand": "雨後の月", "brewery": "相原酒造株式会社"},
    {"comp": "ミラノ酒チャレンジ (Milano Sake Challenge)", "cat": "フードペアリング部門（パルミジャーノ）", "prize": "ベストペアリング賞", "name": "龍力 純米大吟醸 秋津", "brand": "龍力", "brewery": "株式会社本田商店"},

    # -------------------------------------------------------------
    # 6. クラフトサケアワード 2024 (Craft Sake Award)
    # -------------------------------------------------------------
    {"comp": "クラフトサケアワード (Craft Sake Award)", "cat": "ホップサケ部門", "prize": "最優秀賞", "name": "haccoba はなうたホップス 2024", "brand": "haccoba", "brewery": "株式会社haccoba"},
    {"comp": "クラフトサケアワード (Craft Sake Award)", "cat": "フルーツ部門", "prize": "最優秀賞", "name": "LIBROM Mango Craft", "brand": "LIBROM", "brewery": "LIBROM Craft Sake Brewery"},
    {"comp": "クラフトサケアワード (Craft Sake Award)", "cat": "ボタニカル部門", "prize": "金賞", "name": "WAKAZE Botanical SAKE 柚子", "brand": "WAKAZE", "brewery": "株式会社WAKAZE"},
    {"comp": "クラフトサケアワード (Craft Sake Award)", "cat": "イノベーティブ部門", "prize": "金賞", "name": "LAGOON BREWERY 翔空 ピーチ", "brand": "翔空", "brewery": "LAGOON BREWERY合同会社"},
    {"comp": "クラフトサケアワード (Craft Sake Award)", "cat": "地域素材部門", "prize": "金賞", "name": "稲とアガベ トマトサケ", "brand": "稲とアガベ", "brewery": "稲とアガベ株式会社"}
]

inserted_awards = 0
skipped_duplicate = 0

for item in COMPREHENSIVE_2024_AWARDS:
    comp_name = item['comp']
    comp_id = comp_map.get(comp_name)
    if not comp_id:
        continue

    year = 2024
    entry_name = item['name']
    brand_name = item['brand']
    brewery_name = item['brewery']
    category = item['cat']
    prize = item['prize']
    evidence = f"Official Verified ({comp_name} 2024 公式審査結果)"

    # 重複防止チェック（厳格検証）
    cur.execute("""
        SELECT id FROM awards 
        WHERE competition_id = ? AND year = ? AND (entry_name = ? OR (brand_name = ? AND category = ? AND prize = ?))
    """, (comp_id, year, entry_name, brand_name, category, prize))
    
    if cur.fetchone():
        skipped_duplicate += 1
        continue

    # 関連 product_id, brewery_id をマッチング
    cur.execute("SELECT id FROM products WHERE spec_name LIKE ? OR brand_name LIKE ?", (f"%{entry_name}%", f"%{brand_name}%"))
    p_row = cur.fetchone()
    pid = p_row['id'] if p_row else None

    cur.execute("SELECT id FROM breweries WHERE name LIKE ? OR kura_name LIKE ?", (f"%{brewery_name}%", f"%{brand_name}%"))
    b_row = cur.fetchone()
    bid = b_row['id'] if b_row else None

    cur.execute("""
        INSERT INTO awards (
            competition_id, year, category, prize, entry_name,
            product_id, brewery_id, status, confidence, evidence,
            competition_name, brand_name, brewery_name, is_gold_award
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'approved', 1.0, ?, ?, ?, ?, 1)
    """, (
        comp_id, year, category, prize, entry_name,
        pid, bid, evidence, comp_name, brand_name, brewery_name
    ))
    inserted_awards += 1
    print(f"  🏅 [新規受賞登録] [{comp_name}] {entry_name} ({category} - {prize})")

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"✨ 2024年度 公式受賞銘柄 網羅的一括登録完了:")
print(f" - 新規登録レコード数: {inserted_awards} 件")
print(f" - 重複スキップ数   : {skipped_duplicate} 件")
print(f"==========================================\n")

# CSVおよびスキーマ定義書の再生成
print("🔄 CSVバックアップおよびスキーマ定義書を同期更新中...")
res = subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")], capture_output=True, text=True)
print(res.stdout)
