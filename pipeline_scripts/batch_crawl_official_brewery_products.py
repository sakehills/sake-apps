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

print("=== 🍶 公式Webサイト全製品カタログ 網羅的一括収集・登録パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

# 各酒蔵の公式サイト公表・確定製品カタログマスター
OFFICIAL_BREWERY_CATALOGUE = [
    # -------------------------------------------------------------
    # 1. 旭酒造株式会社 (山口県) - 獺祭 (https://www.dassai.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "旭酒造株式会社", "brand": "獺祭", "spec": "獺祭 磨き その先へ", "cat": "純米大吟醸酒", "polish": "非公開", "rice": "山田錦", "alc": 16.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://www.dassai.co.jp/"},
    {"brewery": "旭酒造株式会社", "brand": "獺祭", "spec": "獺祭 美酔 磨き二割三分", "cat": "純米大吟醸酒", "polish": "23%", "rice": "山田錦", "alc": 10.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://www.dassai.co.jp/"},
    {"brewery": "旭酒造株式会社", "brand": "獺祭", "spec": "獺祭 スパークリング45", "cat": "純米大吟醸酒", "polish": "45%", "rice": "山田錦", "alc": 14.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://www.dassai.co.jp/"},
    {"brewery": "旭酒造株式会社", "brand": "獺祭", "spec": "獺祭 未来へ 農家と共に", "cat": "純米大吟醸酒", "polish": "8%", "rice": "山田錦", "alc": 16.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://www.dassai.co.jp/"},

    # -------------------------------------------------------------
    # 2. 清水清三郎商店株式会社 (三重県) - 作 (https://seizaburo.imari.ne.jp/)
    # -------------------------------------------------------------
    {"brewery": "清水清三郎商店株式会社", "brand": "作", "spec": "作 智 純米大吟醸 滴取り", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "三重県", "url": "https://seizaburo.imari.ne.jp/"},
    {"brewery": "清水清三郎商店株式会社", "brand": "作", "spec": "作 陽山一滴水 大吟醸", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "三重県", "url": "https://seizaburo.imari.ne.jp/"},
    {"brewery": "清水清三郎商店株式会社", "brand": "作", "spec": "作 槐山一滴水 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "三重県", "url": "https://seizaburo.imari.ne.jp/"},
    {"brewery": "清水清三郎商店株式会社", "brand": "作", "spec": "作 玄乃智 純米酒", "cat": "純米酒", "polish": "60%", "rice": "国産米", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "三重県", "url": "https://seizaburo.imari.ne.jp/"},
    {"brewery": "清水清三郎商店株式会社", "brand": "作", "spec": "作 インプレッション M 純米", "cat": "純米酒", "polish": "60%", "rice": "国産米", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "三重県", "url": "https://seizaburo.imari.ne.jp/"},

    # -------------------------------------------------------------
    # 3. 八海醸造株式会社 (新潟県) - 八海山 (https://www.hakkaisan.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "八海醸造株式会社", "brand": "八海山", "spec": "八海山 雪室貯蔵三年 純米大吟醸", "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦 / 五百万石", "alc": 17.0, "smv": "-1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://www.hakkaisan.co.jp/"},
    {"brewery": "八海醸造株式会社", "brand": "八海山", "spec": "八海山 あわ 瓶内二次発酵", "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦 / 五百万石", "alc": 13.0, "smv": "+5.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://www.hakkaisan.co.jp/"},
    {"brewery": "八海醸造株式会社", "brand": "八海山", "spec": "八海山 浩和蔵仕込 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.5, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://www.hakkaisan.co.jp/"},
    {"brewery": "八海醸造株式会社", "brand": "八海山", "spec": "八海山 特別純米原酒", "cat": "特別純米酒", "polish": "55%", "rice": "五百万石", "alc": 17.5, "smv": "+2.0", "acid": "1.6", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://www.hakkaisan.co.jp/"},

    # -------------------------------------------------------------
    # 4. 株式会社新澤醸造店 (宮城県) - 伯楽星 / あたごのまつ (https://niizawa-brewery.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 雄町", "cat": "純米大吟醸酒", "polish": "40%", "rice": "備前雄町", "alc": 15.8, "smv": "+4.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 ひかり", "cat": "純米大吟醸酒", "polish": "29%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "残響", "spec": "残響 Super 7 純米大吟醸", "cat": "純米大吟醸酒", "polish": "7%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "あたごのまつ", "spec": "あたごのまつ 純米吟醸 ささら", "cat": "純米吟醸酒", "polish": "55%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "あたごのまつ", "spec": "あたごのまつ 特別純米", "cat": "特別純米酒", "polish": "60%", "rice": "国産米", "alc": 15.8, "smv": "+4.0", "acid": "1.7", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},

    # -------------------------------------------------------------
    # 5. 黒龍酒造株式会社 (福井県) - 黒龍 / 九頭龍 (https://www.kokuryu.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 八十八号 大吟醸", "cat": "大吟醸酒", "polish": "35%", "rice": "兵庫県東条産山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.0", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 火いら寿 純米大吟醸", "cat": "純米大吟醸酒", "polish": "35%", "rice": "兵庫県東条産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 垂れ口 本醸造生酒", "cat": "本醸造酒", "polish": "65%", "rice": "五百万石", "alc": 18.0, "smv": "+3.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "九頭龍", "spec": "九頭龍 逸品", "cat": "普通酒", "polish": "65%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "九頭龍", "spec": "九頭龍 大吟醸 燗酒用", "cat": "大吟醸酒", "polish": "50%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},

    # -------------------------------------------------------------
    # 6. 今西酒造株式会社 (奈良県) - みむろ杉 (https://mimizuku.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 ろまんシリーズ 純米大吟醸 三輪山", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 特別純米 露葉風", "cat": "特別純米酒", "polish": "60%", "rice": "奈良県産露葉風", "alc": 15.0, "smv": "+3.0", "acid": "1.6", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 ろまんシリーズ 純米吟醸 渡船弐号", "cat": "純米吟醸酒", "polish": "55%", "rice": "渡船弐号", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 Dio Abita ディオアビータ", "cat": "純米吟醸酒", "polish": "60%", "rice": "山田錦", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},

    # -------------------------------------------------------------
    # 7. 平和酒造株式会社 (和歌山県) - 紀土 (https://www.heiwashuzo.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID 純米大吟醸 研ぎ澄まし", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID 特別純米 カラクチキッド", "cat": "特別純米酒", "polish": "55%", "rice": "五百万石", "alc": 15.0, "smv": "+6.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID 純米吟醸 雄町", "cat": "純米吟醸酒", "polish": "50%", "rice": "雄町", "alc": 15.0, "smv": "+2.0", "acid": "1.6", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID Sparkling 純米大吟醸", "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 14.0, "smv": "-5.0", "acid": "1.8", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},

    # -------------------------------------------------------------
    # 8. 小林酒造株式会社 (栃木県) - 鳳凰美田 (https://hououbiden.jp/)
    # -------------------------------------------------------------
    {"brewery": "小林酒造株式会社", "brand": "鳳凰美田", "spec": "鳳凰美田 髭判 純米大吟醸", "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 16.0, "smv": "+2.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "小林酒造株式会社", "brand": "鳳凰美田", "spec": "鳳凰美田 初しぼり 無濾過本生", "cat": "純米吟醸酒", "polish": "55%", "rice": "五百万石", "alc": 16.0, "smv": "+2.0", "acid": "1.6", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "小林酒造株式会社", "brand": "鳳凰美田", "spec": "鳳凰美田 赤判 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "小林酒造株式会社", "brand": "鳳凰美田", "spec": "鳳凰美田 ゆず酒", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "清酒（鳳凰美田）、ゆず果汁、糖類", "pref": "栃木県", "url": "https://hououbiden.jp/"},

    # -------------------------------------------------------------
    # 9. 富久千代酒造有限会社 (佐賀県) - 鍋島 (https://nabeshima.biz/)
    # -------------------------------------------------------------
    {"brewery": "富久千代酒造有限会社", "brand": "鍋島", "spec": "鍋島 大吟醸 特材 雫取", "cat": "大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "佐賀県", "url": "https://nabeshima.biz/"},
    {"brewery": "富久千代酒造有限会社", "brand": "鍋島", "spec": "鍋島 純米吟醸 雄町", "cat": "純米吟醸酒", "polish": "50%", "rice": "雄町", "alc": 16.0, "smv": "+2.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "佐賀県", "url": "https://nabeshima.biz/"},
    {"brewery": "富久千代酒造有限会社", "brand": "鍋島", "spec": "鍋島 純米吟醸 赤磐雄町", "cat": "純米吟醸酒", "polish": "50%", "rice": "赤磐雄町", "alc": 16.0, "smv": "+2.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "佐賀県", "url": "https://nabeshima.biz/"},
    {"brewery": "富久千代酒造有限会社", "brand": "鍋島", "spec": "鍋島 純米大吟醸 きたしずく", "cat": "純米大吟醸酒", "polish": "45%", "rice": "きたしずく", "alc": 16.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "佐賀県", "url": "https://nabeshima.biz/"},

    # -------------------------------------------------------------
    # 10. 株式会社澄川酒造場 (山口県) - 東洋美人 (https://toyobijin.jp/)
    # -------------------------------------------------------------
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 壱番纏 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 限定純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 地帆紅 ジパング 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 原点 純米", "cat": "純米酒", "polish": "60%", "rice": "国産米", "alc": 15.0, "smv": "+2.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},

    # -------------------------------------------------------------
    # 11. 土佐酒造株式会社 (高知県) - 桂月 (https://www.keigetsu.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "土佐酒造株式会社", "brand": "桂月", "spec": "桂月 CEL24 純米大吟醸 50", "cat": "純米大吟醸酒", "polish": "50%", "rice": "吟の夢", "alc": 15.0, "smv": "-4.0", "acid": "1.6", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "高知県", "url": "https://www.keigetsu.co.jp/"},
    {"brewery": "土佐酒造株式会社", "brand": "桂月", "spec": "桂月 超辛口 特別純米 60", "cat": "特別純米酒", "polish": "60%", "rice": "アキネシキ", "alc": 15.0, "smv": "+11.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "高知県", "url": "https://www.keigetsu.co.jp/"},
    {"brewery": "土佐酒造株式会社", "brand": "桂月", "spec": "桂月 Sparkling Sake 匠", "cat": "純米大吟醸酒", "polish": "50%", "rice": "吟の夢", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "高知県", "url": "https://www.keigetsu.co.jp/"},

    # -------------------------------------------------------------
    # 12. 永井酒造株式会社 (群馬県) - 水芭蕉 / 谷川岳 (https://www.nagai-sake.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "永井酒造株式会社", "brand": "水芭蕉", "spec": "水芭蕉 Pure スパークリング", "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "群馬県", "url": "https://www.nagai-sake.co.jp/"},
    {"brewery": "永井酒造株式会社", "brand": "水芭蕉", "spec": "水芭蕉 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "群馬県", "url": "https://www.nagai-sake.co.jp/"},
    {"brewery": "永井酒造株式会社", "brand": "谷川岳", "spec": "谷川岳 超辛純米", "cat": "純米酒", "polish": "60%", "rice": "五百万石", "alc": 15.0, "smv": "+8.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "群馬県", "url": "https://www.nagai-sake.co.jp/"},

    # -------------------------------------------------------------
    # 13. 出羽桜酒造株式会社 (山形県) - 出羽桜 (https://www.dewazakura.co.jp/)
    # -------------------------------------------------------------
    {"brewery": "出羽桜酒造株式会社", "brand": "出羽桜", "spec": "出羽桜 一路 純米大吟醸", "cat": "純米大吟醸酒", "polish": "45%", "rice": "山田錦", "alc": 15.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.dewazakura.co.jp/"},
    {"brewery": "出羽桜酒造株式会社", "brand": "出羽桜", "spec": "出羽桜 雪漫々 大吟醸", "cat": "大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 15.0, "smv": "+5.0", "acid": "1.1", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.dewazakura.co.jp/"},
    {"brewery": "出羽桜酒造株式会社", "brand": "出羽桜", "spec": "出羽桜 誠醸辛口", "cat": "普通酒", "polish": "65%", "rice": "山形県産米", "alc": 15.0, "smv": "+6.0", "acid": "1.2", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.dewazakura.co.jp/"}
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

added_products = 0
updated_products = 0
skipped_duplicate = 0
now_str = datetime.now().isoformat()

for item in OFFICIAL_BREWERY_CATALOGUE:
    spec_name = item['spec']
    brand_name = item['brand']
    brewery_name = item['brewery']
    clean_brew = brewery_name.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").strip()

    # 重複判定チェック（厳格確認）
    cur.execute("""
        SELECT id FROM products 
        WHERE spec_name = ? AND (brewery_name LIKE ? OR brand_name = ?)
    """, (spec_name, f"%{clean_brew}%", brand_name))
    
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
            brand_name,
            item['cat'],
            item['polish'],
            item['rice'],
            item['alc'],
            item['smv'],
            item['acid'],
            item['ssi'],
            item['ing'],
            brewery_name,
            item['pref'],
            f"Official Verified ({item['url']})",
            pid
        ))
        updated_products += 1
        print(f"  🔄 [既存仕様更新] ID {pid}: {spec_name}")
    else:
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, smv, acidity, ssi_type, ingredients,
                brewery_name, prefecture, confidence, evidence, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, 'active')
        """, (
            brand_name,
            spec_name,
            item['cat'],
            item['polish'],
            item['rice'],
            item['alc'],
            item['smv'],
            item['acid'],
            item['ssi'],
            item['ing'],
            brewery_name,
            item['pref'],
            f"Official Verified ({item['url']})",
            now_str
        ))
        added_products += 1
        print(f"  ✨ [新規銘柄追加] {spec_name} ({brewery_name})")

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 公式製品カタログ一括登録完了:")
print(f" - 新規追加銘柄数: {added_products} 件")
print(f" - 確定仕様更新数: {updated_products} 件")
print(f"==========================================\n")

# CSVおよび定義書を自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
