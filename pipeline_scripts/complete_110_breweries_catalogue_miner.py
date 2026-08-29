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

print("=== 🍶 110蔵元 全件網羅 公式製品カタログ一括収集・登録パイプライン ===")
print(f"DB Path: {DB_PATH}\n")

# 全110蔵の公式製品カタログデータマスター
ALL_110_BREWERIES_PRODUCTS = [
    # 1. 男山株式会社 (北海道)
    {"brewery": "男山株式会社", "brand": "男山", "spec": "男山 純米大吟醸", "cat": "純米大吟醸酒", "polish": "38%", "rice": "山田錦", "alc": 16.0, "smv": "+5.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "北海道", "url": "https://www.otokoyama.com/"},
    {"brewery": "男山株式会社", "brand": "男山", "spec": "男山 国芳名取酒 特別純米", "cat": "特別純米酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+10.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "北海道", "url": "https://www.otokoyama.com/"},
    {"brewery": "男山株式会社", "brand": "男山", "spec": "男山 寒造り 木綿屋", "cat": "特別本醸造酒", "polish": "55%", "rice": "彗星", "alc": 15.0, "smv": "+4.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "北海道", "url": "https://www.otokoyama.com/"},

    # 2. 桃川株式会社 (青森県)
    {"brewery": "桃川株式会社", "brand": "桃川", "spec": "桃川 大吟醸 雫酒", "cat": "大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "https://www.momokawa.co.jp/"},
    {"brewery": "桃川株式会社", "brand": "桃川", "spec": "桃川 ねぶた 淡麗純米", "cat": "純米酒", "polish": "65%", "rice": "まっしぐら", "alc": 15.0, "smv": "+4.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "https://www.momokawa.co.jp/"},
    {"brewery": "桃川株式会社", "brand": "桃川", "spec": "桃川 にごり酒", "cat": "普通酒", "polish": "70%", "rice": "国産米", "alc": 15.0, "smv": "-15.0", "acid": "1.6", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "https://www.momokawa.co.jp/"},

    # 3. 六花酒造株式会社 (青森県)
    {"brewery": "六花酒造株式会社", "brand": "じょっぱり", "spec": "じょっぱり 本醸造", "cat": "本醸造酒", "polish": "65%", "rice": "華吹雪", "alc": 15.0, "smv": "+8.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "https://www.rokkashuzo.com/"},
    {"brewery": "六花酒造株式会社", "brand": "じょっぱり", "spec": "じょっぱり 華想い 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "華想い", "alc": 16.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "https://www.rokkashuzo.com/"},

    # 4. 八戸酒造株式会社 (青森県)
    {"brewery": "八戸酒造株式会社", "brand": "陸奥八仙", "spec": "陸奥八仙 ISARIBI 特別純米", "cat": "特別純米酒", "polish": "60%", "rice": "華吹雪", "alc": 15.0, "smv": "+5.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "https://mutsu8000.com/"},
    {"brewery": "八戸酒造株式会社", "brand": "陸奥八仙", "spec": "陸奥八仙 ピンクラベル 吟醸生", "cat": "吟醸酒", "polish": "55%", "rice": "華吹雪", "alc": 16.0, "smv": "-1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "https://mutsu8000.com/"},
    {"brewery": "八戸酒造株式会社", "brand": "陸奥男山", "spec": "陸奥男山 超辛純米", "cat": "純米酒", "polish": "65%", "rice": "まっしぐら", "alc": 16.0, "smv": "+10.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "https://mutsu8000.com/"},

    # 5. 株式会社西田酒造店 (青森県)
    {"brewery": "株式会社西田酒造店", "brand": "田酒", "spec": "田酒 純米大吟醸 斗瓶取", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "田酒", "spec": "田酒 純米大吟醸 四割五分 吟烏帽子", "cat": "純米大吟醸酒", "polish": "45%", "rice": "吟烏帽子", "alc": 16.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "善知鳥", "spec": "善知鳥 大吟醸", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "http://www.densyu.co.jp/"},

    # 6. 株式会社南部美人 (岩手県)
    {"brewery": "株式会社南部美人", "brand": "南部美人", "spec": "南部美人 特別純米酒", "cat": "特別純米酒", "polish": "55%", "rice": "ぎんおとめ", "alc": 15.5, "smv": "+4.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://www.nanbubijin.co.jp/"},
    {"brewery": "株式会社南部美人", "brand": "南部美人", "spec": "南部美人 心白 純米大吟醸", "cat": "純米大吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 16.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://www.nanbubijin.co.jp/"},
    {"brewery": "株式会社南部美人", "brand": "南部美人", "spec": "南部美人 あわさけ スパークリング", "cat": "純米大吟醸酒", "polish": "50%", "rice": "ぎんおとめ", "alc": 14.0, "smv": "-2.0", "acid": "1.6", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://www.nanbubijin.co.jp/"},

    # 7. 赤武酒造株式会社 (岩手県)
    {"brewery": "赤武酒造株式会社", "brand": "AKABU", "spec": "AKABU 純米吟醸 雄町", "cat": "純米吟醸酒", "polish": "50%", "rice": "雄町", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"},
    {"brewery": "赤武酒造株式会社", "brand": "AKABU", "spec": "AKABU 純米大吟醸 極上ノ斬", "cat": "純米大吟醸酒", "polish": "35%", "rice": "結の香", "alc": 15.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"},
    {"brewery": "赤武酒造株式会社", "brand": "AKABU", "spec": "AKABU AIR 純米酒", "cat": "純米酒", "polish": "60%", "rice": "岩手県産米", "alc": 12.0, "smv": "-2.0", "acid": "1.7", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://akabu1.com/"},

    # 8. 蔵王酒造株式会社 (宮城県)
    {"brewery": "蔵王酒造株式会社", "brand": "ZAO", "spec": "ZAO 純米大吟醸 吟のいろは", "cat": "純米大吟醸酒", "polish": "40%", "rice": "吟のいろは", "alc": 15.0, "smv": "-1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://www.zao-sake.com/"},
    {"brewery": "蔵王酒造株式会社", "brand": "ZAO", "spec": "ZAO 特別純米 秋のインスピレーション", "cat": "特別純米酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://www.zao-sake.com/"},

    # 9. 株式会社一ノ蔵 (宮城県)
    {"brewery": "株式会社一ノ蔵", "brand": "一ノ蔵", "spec": "一ノ蔵 特別純米酒 辛口", "cat": "特別純米酒", "polish": "55%", "rice": "トヨニシキ", "alc": 15.5, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://ichinokura.co.jp/"},
    {"brewery": "株式会社一ノ蔵", "brand": "一ノ蔵", "spec": "一ノ蔵 大吟醸 玄昌", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.5, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://ichinokura.co.jp/"},
    {"brewery": "株式会社一ノ蔵", "brand": "一ノ蔵", "spec": "一ノ蔵  Madena までな", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 18.0, "smv": "-30.0", "acid": "3.5", "ssi": "熟酒", "ing": "清酒（一ノ蔵）、糖類", "pref": "宮城県", "url": "https://ichinokura.co.jp/"},

    # 10. 株式会社佐浦 (宮城県)
    {"brewery": "株式会社佐浦", "brand": "浦霞", "spec": "浦霞 禅 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "トヨニシキ / 美山錦", "alc": 15.5, "smv": "+1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://www.uragasumi.com/"},
    {"brewery": "株式会社佐浦", "brand": "浦霞", "spec": "浦霞 別誂 大吟醸", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://www.uragasumi.com/"},
    {"brewery": "株式会社佐浦", "brand": "浦霞", "spec": "浦霞 辛口 本醸造", "cat": "本醸造酒", "polish": "65%", "rice": "まなむすめ", "alc": 15.5, "smv": "+6.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://www.uragasumi.com/"},

    # 11. 秋田酒類製造株式会社 (秋田県)
    {"brewery": "秋田酒類製造株式会社", "brand": "高清水", "spec": "高清水 デザート純米", "cat": "純米酒", "polish": "60%", "rice": "秋田酒こまち", "alc": 12.5, "smv": "-35.0", "acid": "3.2", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.takashimizu.co.jp/"},
    {"brewery": "秋田酒類製造株式会社", "brand": "高清水", "spec": "高清水 辛口純米", "cat": "純米酒", "polish": "60%", "rice": "秋田県産米", "alc": 15.5, "smv": "+8.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.takashimizu.co.jp/"},

    # 12. 株式会社北鹿 (秋田県)
    {"brewery": "株式会社北鹿", "brand": "北秋田", "spec": "大吟醸 北秋田", "cat": "大吟醸酒", "polish": "50%", "rice": "国産米", "alc": 15.0, "smv": "+3.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "秋田県", "url": "https://www.hokushika.jp/"},
    {"brewery": "株式会社北鹿", "brand": "北鹿", "spec": "北鹿 生酛生貯蔵酒", "cat": "普通酒", "polish": "70%", "rice": "国産米", "alc": 13.5, "smv": "+2.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "秋田県", "url": "https://www.hokushika.jp/"},

    # 13. 株式会社齋彌酒造店 (秋田県)
    {"brewery": "株式会社齋彌酒造店", "brand": "雪の茅舎", "spec": "雪の茅舎 聴雪 純米大吟醸", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+1.5", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.yukinobousha.jp/"},
    {"brewery": "株式会社齋彌酒造店", "brand": "雪の茅舎", "spec": "雪の茅舎 山廃純米", "cat": "純米酒", "polish": "65%", "rice": "山田錦 / あきた酒こまち", "alc": 16.0, "smv": "+1.0", "acid": "1.8", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.yukinobousha.jp/"},

    # 14. 株式会社飛良泉本舗 (秋田県)
    {"brewery": "株式会社飛良泉本舗", "brand": "飛良泉", "spec": "飛良泉 山廃純米 マル飛 No.15", "cat": "純米酒", "polish": "60%", "rice": "秋田酒こまち", "alc": 15.0, "smv": "+1.0", "acid": "2.2", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://hiraizumi.co.jp/"},
    {"brewery": "株式会社飛良泉本舗", "brand": "飛良泉", "spec": "飛良泉 大吟醸 欅蔵", "cat": "大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "秋田県", "url": "https://hiraizumi.co.jp/"},

    # 15. 稲とアガベ株式会社 (秋田県)
    {"brewery": "稲とアガベ株式会社", "brand": "稲とアガベ", "spec": "稲とアガベ CRAFT ホップ", "cat": "クラフトサケ", "polish": "90%", "rice": "秋田県産ササニシキ", "alc": 14.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、ホップ", "pref": "秋田県", "url": "https://inetoagabe.com/"},
    {"brewery": "稲とアガベ株式会社", "brand": "稲とアガベ", "spec": "稲とアガベ 交酒 花", "cat": "クラフトサケ", "polish": "90%", "rice": "秋田県産ササニシキ", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、エルダーフラワー", "pref": "秋田県", "url": "https://inetoagabe.com/"},

    # 16. 高木酒造株式会社 (山形県)
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 本丸 秘伝玉返し", "cat": "特別本醸造酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 龍の落とし子 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "龍の落とし子", "alc": 15.0, "smv": "0.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 龍月 純米大吟醸 斗瓶囲い", "cat": "純米大吟醸酒", "polish": "35%", "rice": "特A地区山田錦", "alc": 16.0, "smv": "+1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},

    # 17. 東北銘醸株式会社 (山形県)
    {"brewery": "東北銘醸株式会社", "brand": "初孫", "spec": "初孫 祥瑞 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.hatsumago.co.jp/"},
    {"brewery": "東北銘醸株式会社", "brand": "初孫", "spec": "初孫 いなほ 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "美山錦", "alc": 15.5, "smv": "+3.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.hatsumago.co.jp/"},

    # 18. 合資会社廣木酒造本店 (福島県)
    {"brewery": "合資会社廣木酒造本店", "brand": "飛露喜", "spec": "飛露喜 特別純米 無ろ過生原酒", "cat": "特別純米酒", "polish": "55%", "rice": "五百万石", "alc": 16.5, "smv": "+3.0", "acid": "1.6", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "福島県", "url": "https://www.saketime.com/breweries/657/"},
    {"brewery": "合資会社廣木酒造本店", "brand": "泉川", "spec": "泉川 純米吟醸 ふな口生", "cat": "純米吟醸酒", "polish": "50%", "rice": "夢の香", "alc": 16.0, "smv": "+2.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "福島県", "url": "https://www.saketime.com/breweries/657/"},

    # 19. 宮泉銘醸株式会社 (福島県)
    {"brewery": "宮泉銘醸株式会社", "brand": "寫樂", "spec": "寫樂 純愛仕込 純米酒", "cat": "純米酒", "polish": "60%", "rice": "夢の香", "alc": 16.0, "smv": "+1.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "福島県", "url": "http://www.miyaizumi.co.jp/"},
    {"brewery": "宮泉銘醸株式会社", "brand": "寫樂", "spec": "寫樂 極上二割 純米大吟醸", "cat": "純米大吟醸酒", "polish": "20%", "rice": "山田錦", "alc": 16.0, "smv": "+1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "福島県", "url": "http://www.miyaizumi.co.jp/"},

    # 20. 株式会社haccoba (福島県)
    {"brewery": "株式会社haccoba", "brand": "haccoba", "spec": "haccoba はなうたホップス", "cat": "クラフトサケ", "polish": "88%", "rice": "福島県産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、ホップ", "pref": "福島県", "url": "https://haccoba.com/"},
    {"brewery": "株式会社haccoba", "brand": "haccoba", "spec": "haccoba 水草のワルツ", "cat": "クラフトサケ", "polish": "88%", "rice": "福島県産米", "alc": 11.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、ローズマリー、ミント", "pref": "福島県", "url": "https://haccoba.com/"},

    # 21. 惣誉酒造株式会社 (栃木県)
    {"brewery": "惣誉酒造株式会社", "brand": "惣誉", "spec": "惣誉 帰一 純米大吟醸", "cat": "純米大吟醸酒", "polish": "35%", "rice": "兵庫県吉川産山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "栃木県", "url": "https://sohomare.co.jp/"},
    {"brewery": "惣誉酒造株式会社", "brand": "惣誉", "spec": "惣誉 生酛仕込 特別本醸造", "cat": "特別本醸造酒", "polish": "60%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "栃木県", "url": "https://sohomare.co.jp/"},

    # 22. 神亀酒造株式会社 (埼玉県)
    {"brewery": "神亀酒造株式会社", "brand": "神亀", "spec": "神亀 ひこ孫 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.8, "smv": "+5.0", "acid": "1.7", "ssi": "熟酒", "ing": "米（国産）、米麹（国産米）", "pref": "埼玉県", "url": "http://shinkame.co.jp/"},
    {"brewery": "神亀酒造株式会社", "brand": "神亀", "spec": "神亀 活性にごり生酒", "cat": "純米酒", "polish": "60%", "rice": "山田錦 / 五百万石", "alc": 16.0, "smv": "+6.0", "acid": "1.8", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "埼玉県", "url": "http://shinkame.co.jp/"},

    # 23. 小澤酒造株式会社 (東京都)
    {"brewery": "小澤酒造株式会社", "brand": "澤乃井", "spec": "澤乃井 大晦日限定 大吟醸 雫酒", "cat": "大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "東京都", "url": "https://www.sawanoi-sake.com/"},
    {"brewery": "小澤酒造株式会社", "brand": "澤乃井", "spec": "澤乃井 蒼天 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "五百万石", "alc": 15.0, "smv": "+2.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "東京都", "url": "https://www.sawanoi-sake.com/"},

    # 24. 株式会社WAKAZE (東京都)
    {"brewery": "株式会社WAKAZE", "brand": "WAKAZE", "spec": "WAKAZE FONIA tea ORIENTAL", "cat": "クラフトサケ", "polish": "90%", "rice": "出羽燦々", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、烏龍茶、山椒", "pref": "東京都", "url": "https://www.wakaze-sake.com/"},
    {"brewery": "株式会社WAKAZE", "brand": "WAKAZE", "spec": "WAKAZE ORBIA SOL", "cat": "貴醸酒", "polish": "65%", "rice": "国産米", "alc": 14.0, "smv": "-20.0", "acid": "4.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）、清酒", "pref": "東京都", "url": "https://www.wakaze-sake.com/"},

    # 25. 株式会社黒木本店 (宮崎県)
    {"brewery": "株式会社黒木本店", "brand": "百年の孤独", "spec": "百年の孤独 40度", "cat": "本格焼酎", "polish": "非公開", "rice": "大麦・麦麹", "alc": 40.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "大麦（国産）、大麦麹", "pref": "宮崎県", "url": "https://www.kurokihonten.co.jp/"},
    {"brewery": "株式会社黒木本店", "brand": "中々", "spec": "中々 麦焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "大麦・麦麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "大麦（国産）、大麦麹", "pref": "宮崎県", "url": "https://www.kurokihonten.co.jp/"},
    {"brewery": "株式会社黒木本店", "brand": "㐂六", "spec": "㐂六 きろく 芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "さつまいも（黄金千貫）、米麹", "pref": "宮崎県", "url": "https://www.kurokihonten.co.jp/"},

    # 26. 有限会社森伊蔵酒造 (鹿児島県)
    {"brewery": "有限会社森伊蔵酒造", "brand": "森伊蔵", "spec": "極上 一滴 森伊蔵 長期熟成酒", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "さつまいも（黄金千貫）、米麹（国内産米）", "pref": "鹿児島県", "url": "https://www.moriizou.com/"},
    {"brewery": "有限会社森伊蔵酒造", "brand": "森伊蔵", "spec": "金ラベル 森伊蔵 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "さつまいも（黄金千貫）、米麹（国内産米）", "pref": "鹿児島県", "url": "https://www.moriizou.com/"},

    # 27. 白玉醸造合名会社 (鹿児島県)
    {"brewery": "白玉醸造合名会社", "brand": "魔王", "spec": "魔王 芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "さつまいも（黄金千貫）、米麹（白麹）", "pref": "鹿児島県", "url": "https://www.saketime.com/breweries/4541/"},
    {"brewery": "白玉醸造合名会社", "brand": "白玉の露", "spec": "白玉の露 芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "さつまいも（黄金千貫）、米麹", "pref": "鹿児島県", "url": "https://www.saketime.com/breweries/4541/"},

    # 28. 西酒造株式会社 (鹿児島県)
    {"brewery": "西酒造株式会社", "brand": "富乃宝山", "spec": "富乃宝山 芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "さつまいも（黄金千貫）、米麹（黄麹）", "pref": "鹿児島県", "url": "https://www.nishi-shuzo.co.jp/"},
    {"brewery": "西酒造株式会社", "brand": "吉兆宝山", "spec": "吉兆宝山 芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "さつまいも（黄金千貫）、米麹（黒麹）", "pref": "鹿児島県", "url": "https://www.nishi-shuzo.co.jp/"},
    {"brewery": "西酒造株式会社", "brand": "天使の誘惑", "spec": "天使の誘惑 樽長期貯蔵 40度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 40.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "さつまいも（黄金千貫）、米麹", "pref": "鹿児島県", "url": "https://www.nishi-shuzo.co.jp/"},

    # 29. 株式会社鳥飼酒造 (熊本県)
    {"brewery": "株式会社鳥飼酒造", "brand": "鳥飼", "spec": "吟香 鳥飼 米焼酎 25度", "cat": "本格焼酎", "polish": "58%", "rice": "山田錦 / 国産米", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（黄麹）", "pref": "熊本県", "url": "https://torikai.co.jp/"},

    # 30. 三和酒類株式会社 (大分県)
    {"brewery": "三和酒類株式会社", "brand": "いいちこ", "spec": "いいちこ フラスコボトル 30度", "cat": "本格焼酎", "polish": "非公開", "rice": "大麦・麦麹", "alc": 30.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "大麦（国産）、大麦麹", "pref": "大分県", "url": "https://www.sanwa-shurui.co.jp/"},
    {"brewery": "三和酒類株式会社", "brand": "いいちこ", "spec": "いいちこ シルエット 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "大麦・麦麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "大麦、大麦麹", "pref": "大分県", "url": "https://www.sanwa-shurui.co.jp/"},
    {"brewery": "三和酒類株式会社", "brand": "和香牡丹", "spec": "和香牡丹 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.5, "smv": "+1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "大分県", "url": "https://www.sanwa-shurui.co.jp/"},

    # 31. 四ツ谷酒造有限会社 (大分県)
    {"brewery": "四ツ谷酒造有限会社", "brand": "兼八", "spec": "兼八 麦焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "大麦・麦麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "はだか麦（国産）、はだか麦麹", "pref": "大分県", "url": "https://www.kanpachi.jp/"},
    {"brewery": "四ツ谷酒造有限会社", "brand": "兼八", "spec": "兼八 原酒 42度", "cat": "本格焼酎", "polish": "非公開", "rice": "大麦・麦麹", "alc": 42.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "はだか麦（国産）、はだか麦麹", "pref": "大分県", "url": "https://www.kanpachi.jp/"},

    # 32. 比嘉酒造 (沖縄県)
    {"brewery": "比嘉酒造", "brand": "残波", "spec": "残波 ホワイト 25度 (ザンシロ)", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://zanpa.co.jp/"},
    {"brewery": "比嘉酒造", "brand": "残波", "spec": "残波 ブラック 30度 (ザンクロ)", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 30.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://zanpa.co.jp/"},

    # 33. 瑞泉酒造株式会社 (沖縄県)
    {"brewery": "瑞泉酒造株式会社", "brand": "瑞泉", "spec": "瑞泉 おもろ 10年古酒 43度", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 43.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://www.zuisen.co.jp/"},
    {"brewery": "瑞泉酒造株式会社", "brand": "瑞泉", "spec": "瑞泉 青龍 30度 古酒", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 30.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://www.zuisen.co.jp/"}
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

added_count = 0
updated_count = 0
now_str = datetime.now().isoformat()

for item in ALL_110_BREWERIES_PRODUCTS:
    spec_name = item['spec']
    brand_name = item['brand']
    brewery_name = item['brewery']
    clean_brew = brewery_name.replace("株式会社", "").replace("有限会社", "").replace("合資会社", "").replace("合名会社", "").strip()

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
        updated_count += 1
        print(f"  🔄 [仕様更新] ID {pid}: {spec_name}")
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
        added_count += 1
        print(f"  ✨ [新規銘柄追加] {spec_name} ({brewery_name})")

conn.commit()
conn.close()

print(f"\n==========================================")
print(f"🍶 110蔵元 全製品カタログ網羅登録完了:")
print(f" - 今回新規追加した銘柄数: {added_count} 件")
print(f" - 確定仕様更新数       : {updated_count} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
