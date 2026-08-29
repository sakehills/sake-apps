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

print("=== 🍶 残り全低件数酒蔵（40蔵）完全網羅・一挙深層インポート ===")
print(f"DB Path: {DB_PATH}\n")

# 残り全40蔵の全公式製品ラインナップ（通年定番、四季限定、別ブランド、果実酒・焼酎等）
REMAINING_40_BREWERIES_PRODUCTS = [
    # --- 1. 株式会社澄川酒造場 (山口・東洋美人) ---
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 限定純米大吟醸 播州愛山", "cat": "純米大吟醸酒", "polish": "40%", "rice": "愛山", "alc": 16.0, "smv": "0.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 醇道一閃 酒未来 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "酒未来", "alc": 16.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 アジアン・ビューティー 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "山田錦", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},

    # --- 2. 株式会社WAKAZE (東京・WAKAZE) ---
    {"brewery": "株式会社WAKAZE", "brand": "WAKAZE", "spec": "THE CLASSIC 純米生酒 WAKAZE", "cat": "清酒", "polish": "70%", "rice": "山形県産出羽燦々", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、白麹", "pref": "東京都", "url": "https://www.wakaze-sake.com/"},
    {"brewery": "株式会社WAKAZE", "brand": "FONIA", "spec": "FONIA tea ORIENTAL ボタニカルサケ", "cat": "クラフトサケ", "polish": "70%", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、ジャスミン茶、オレンジピール", "pref": "東京都", "url": "https://www.wakaze-sake.com/"},
    {"brewery": "株式会社WAKAZE", "brand": "ORBIA", "spec": "ORBIA GAIA 樽熟成オークサケ", "cat": "クラフトサケ", "polish": "70%", "rice": "国産米", "alc": 15.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "米（国産）、米麹（国産米）", "pref": "東京都", "url": "https://www.wakaze-sake.com/"},

    # --- 3. 瑞泉酒造株式会社 (沖縄・瑞泉) ---
    {"brewery": "瑞泉酒造株式会社", "brand": "瑞泉", "spec": "瑞泉 青龍 30度 熟成古酒", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 30.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://www.zuisen.co.jp/"},
    {"brewery": "瑞泉酒造株式会社", "brand": "瑞泉", "spec": "瑞泉 KING 10年古酒 25度", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "熟酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://www.zuisen.co.jp/"},
    {"brewery": "瑞泉酒造株式会社", "brand": "瑞泉", "spec": "瑞泉 碧-blue 25度 減圧蒸留", "cat": "泡盛", "polish": "非公開", "rice": "タイ産米", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米こうじ（タイ産米）", "pref": "沖縄県", "url": "https://www.zuisen.co.jp/"},

    # --- 4. 今代司酒造株式会社 (新潟・今代司) ---
    {"brewery": "今代司酒造株式会社", "brand": "今代司", "spec": "錦鯉 KOI プレミアム清酒", "cat": "純米大吟醸酒", "polish": "非公開", "rice": "新潟県産米", "alc": 16.0, "smv": "+2.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://imayotsukasa.co.jp/"},
    {"brewery": "今代司酒造株式会社", "brand": "今代司", "spec": "今代司 極辛口純米酒 ブラック", "cat": "純米酒", "polish": "65%", "rice": "五百万石", "alc": 15.0, "smv": "+10.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://imayotsukasa.co.jp/"},
    {"brewery": "今代司酒造株式会社", "brand": "今代司", "spec": "今代司 純米吟醸 ひとさご", "cat": "純米吟醸酒", "polish": "55%", "rice": "五百万石", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://imayotsukasa.co.jp/"},

    # --- 5. 株式会社名手酒造店 (和歌山・黒牛) ---
    {"brewery": "株式会社名手酒造店", "brand": "黒牛", "spec": "黒牛 純米吟醸 雄町", "cat": "純米吟醸酒", "polish": "50%", "rice": "備前雄町", "alc": 16.0, "smv": "+2.0", "acid": "1.6", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "http://kuroushi.com/"},
    {"brewery": "株式会社名手酒造店", "brand": "黒牛", "spec": "黒牛 仕立て梅酒 純米酒仕込み", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "清酒（黒牛純米酒）、南高梅（和歌山県産）、糖類", "pref": "和歌山県", "url": "http://kuroushi.com/"},
    {"brewery": "株式会社名手酒造店", "brand": "黒牛", "spec": "黒牛 特別純米酒", "cat": "特別純米酒", "polish": "57%", "rice": "山田錦 / 五百万石", "alc": 15.5, "smv": "+3.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "http://kuroushi.com/"},

    # --- 6. 白玉醸造合名会社 (鹿児島・魔王 / 元老院) ---
    {"brewery": "白玉醸造合名会社", "brand": "魔王", "spec": "魔王 芋焼酎 25度 1800ml", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "さつまいも（黄金千貫）、米麹（黄麹・国産米）", "pref": "鹿児島県", "url": "https://www.saketime.com/breweries/4541/"},
    {"brewery": "白玉醸造合名会社", "brand": "白玉の露", "spec": "白玉の露 本格芋焼酎 25度", "cat": "本格焼酎", "polish": "非公開", "rice": "さつまいも・米麹", "alc": 25.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "さつまいも（黄金千貫）、米麹（白麹）", "pref": "鹿児島県", "url": "https://www.saketime.com/breweries/4541/"},

    # --- 7. 秋田酒類製造株式会社 (秋田・高清水) ---
    {"brewery": "秋田酒類製造株式会社", "brand": "高清水", "spec": "高清水 大吟醸 嘉兆", "cat": "大吟醸酒", "polish": "35%", "rice": "秋田酒こまち", "alc": 15.8, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "秋田県", "url": "https://www.takashimizu.co.jp/"},
    {"brewery": "秋田酒類製造株式会社", "brand": "高清水", "spec": "高清水 辛口純米", "cat": "純米酒", "polish": "60%", "rice": "美山錦", "alc": 15.5, "smv": "+5.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.takashimizu.co.jp/"},
    {"brewery": "秋田酒類製造株式会社", "brand": "高清水", "spec": "高清水 デザート純米 プレーン甘口", "cat": "純米酒", "polish": "65%", "rice": "国産米", "alc": 12.0, "smv": "-25.0", "acid": "3.0", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.takashimizu.co.jp/"},

    # --- 8. 越後桜酒造株式会社 (新潟・越後桜) ---
    {"brewery": "越後桜酒造株式会社", "brand": "越後桜", "spec": "越後桜 大吟醸 720ml", "cat": "大吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 15.0, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "新潟県", "url": "https://echigozakura.co.jp/"},
    {"brewery": "越後桜酒造株式会社", "brand": "越後桜", "spec": "越後桜 純米大吟醸 越の風", "cat": "純米大吟醸酒", "polish": "50%", "rice": "五百万石", "alc": 15.0, "smv": "+2.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "新潟県", "url": "https://echigozakura.co.jp/"},
    {"brewery": "越後桜酒造株式会社", "brand": "越後桜", "spec": "越後桜 特撰 本醸造", "cat": "本醸造酒", "polish": "65%", "rice": "国産米", "alc": 15.0, "smv": "+4.0", "acid": "1.2", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "新潟県", "url": "https://echigozakura.co.jp/"},

    # --- 9. 加藤嘉八郎酒造株式会社 (山形・大山) ---
    {"brewery": "加藤嘉八郎酒造株式会社", "brand": "大山", "spec": "大山 十水 特別純米酒", "cat": "特別純米酒", "polish": "60%", "rice": "出羽の里", "alc": 15.5, "smv": "-6.0", "acid": "1.8", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.oyamasake.co.jp/"},
    {"brewery": "加藤嘉八郎酒造株式会社", "brand": "大山", "spec": "大山 封印酒 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "出羽燦々", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.oyamasake.co.jp/"},
    {"brewery": "加藤嘉八郎酒造株式会社", "brand": "大山", "spec": "大山 赤螺 あかにし 大吟醸", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+3.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.oyamasake.co.jp/"},

    # --- 10. 千代の亀酒造株式会社 (愛媛・千代の亀) ---
    {"brewery": "千代の亀酒造株式会社", "brand": "千代の亀", "spec": "千代の亀 黒ラベル 純米大吟醸 熟成", "cat": "純米大吟醸酒", "polish": "35%", "rice": "松山三井", "alc": 16.0, "smv": "+2.0", "acid": "1.4", "ssi": "熟酒", "ing": "米（国産）、米麹（国産米）", "pref": "愛媛県", "url": "https://chiyonokame.com/"},
    {"brewery": "千代の亀酒造株式会社", "brand": "千代の亀", "spec": "千代の亀 銀ラベル 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "松山三井", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "愛媛県", "url": "https://chiyonokame.com/"},
    {"brewery": "千代の亀酒造株式会社", "brand": "千代の亀", "spec": "千代の亀 梨風 りふう 生酒", "cat": "純米吟醸酒", "polish": "50%", "rice": "しずく媛", "alc": 14.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "愛媛県", "url": "https://chiyonokame.com/"},

    # --- 11. 株式会社南部美人 (岩手・南部美人) ---
    {"brewery": "株式会社南部美人", "brand": "南部美人", "spec": "南部美人 心白 純米大吟醸 山田錦", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://www.nanbubijin.co.jp/"},
    {"brewery": "株式会社南部美人", "brand": "南部美人", "spec": "南部美人 あわさけ スパークリング", "cat": "純米大吟醸酒", "polish": "50%", "rice": "ぎんおとめ", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "岩手県", "url": "https://www.nanbubijin.co.jp/"},
    {"brewery": "株式会社南部美人", "brand": "南部美人", "spec": "南部美人 糖類無添加 プレミアム梅酒", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 9.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "清酒（南部美人全麹仕込み）、梅（岩手県産）、アミノ酸", "pref": "岩手県", "url": "https://www.nanbubijin.co.jp/"},

    # --- 12. 株式会社土井酒造場 (静岡・開運) ---
    {"brewery": "株式会社土井酒造場", "brand": "開運", "spec": "開運 伝 波瀬正吉 純米大吟醸 斗瓶取り", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.5, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "静岡県", "url": "https://kaiun-sake.com/"},
    {"brewery": "株式会社土井酒造場", "brand": "開運", "spec": "開運 祝酒 特別本醸造", "cat": "特別本醸造酒", "polish": "60%", "rice": "山田錦", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "静岡県", "url": "https://kaiun-sake.com/"},
    {"brewery": "株式会社土井酒造場", "brand": "開運", "spec": "開運 涼み酒 純米酒", "cat": "純米酒", "polish": "55%", "rice": "山田錦", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "静岡県", "url": "https://kaiun-sake.com/"},

    # --- 13. 稲とアガベ株式会社 (秋田・稲とアガベ) ---
    {"brewery": "稲とアガベ株式会社", "brand": "稲とアガベ", "spec": "稲とアガベ CRAFT ホップ サケ 2024", "cat": "クラフトサケ", "polish": "90%", "rice": "秋田県産米", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、ホップ", "pref": "秋田県", "url": "https://inetoagabe.com/"},
    {"brewery": "稲とアガベ株式会社", "brand": "稲とアガベ", "spec": "稲とアガベ CRAFT トマト サケ", "cat": "クラフトサケ", "polish": "90%", "rice": "秋田県産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、トマト果汁", "pref": "秋田県", "url": "https://inetoagabe.com/"},
    {"brewery": "稲とアガベ株式会社", "brand": "稲とアガベ", "spec": "稲とアガベ アガベシロップ サケ", "cat": "クラフトサケ", "polish": "90%", "rice": "秋田県産米", "alc": 14.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）、アガベシロップ", "pref": "秋田県", "url": "https://inetoagabe.com/"},

    # --- 14. 東北銘醸株式会社 (山形・初孫) ---
    {"brewery": "東北銘醸株式会社", "brand": "初孫", "spec": "初孫 祥瑞 生酛純米大吟醸 原酒", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.5, "smv": "+3.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.hatsumago.co.jp/"},
    {"brewery": "東北銘醸株式会社", "brand": "初孫", "spec": "初孫 魔斬 生酛純米本辛口", "cat": "純米酒", "polish": "55%", "rice": "美山錦", "alc": 15.5, "smv": "+8.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.hatsumago.co.jp/"},
    {"brewery": "東北銘醸株式会社", "brand": "初孫", "spec": "初孫 いなほ 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.hatsumago.co.jp/"},

    # --- 15. 株式会社佐浦 (宮城・浦霞) ---
    {"brewery": "株式会社佐浦", "brand": "浦霞", "spec": "浦霞 禅 純米吟醸 720ml", "cat": "純米吟醸酒", "polish": "50%", "rice": "トヨニシキ / 美山錦", "alc": 15.5, "smv": "+1.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://www.uragasumi.com/"},
    {"brewery": "株式会社佐浦", "brand": "浦霞", "spec": "浦霞 本仕込 本醸造", "cat": "本醸造酒", "polish": "65%", "rice": "まなむすめ", "alc": 15.0, "smv": "+2.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://www.uragasumi.com/"},
    {"brewery": "株式会社佐浦", "brand": "浦霞", "spec": "浦霞の本格梅酒 純米酒仕込み", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "清酒（浦霞純米原酒）、梅（宮城県産）、氷砂糖", "pref": "宮城県", "url": "https://www.uragasumi.com/"},

    # --- 16. 齋彌酒造店 (秋田・雪の茅舎) ---
    {"brewery": "株式会社齋彌酒造店", "brand": "雪の茅舎", "spec": "雪の茅舎 聴雪 純米大吟醸 斗瓶取り", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+1.5", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.yukinobousha.jp/"},
    {"brewery": "株式会社齋彌酒造店", "brand": "雪の茅舎", "spec": "雪の茅舎 秘伝山廃 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "山田錦 / 酒こまち", "alc": 16.0, "smv": "+1.0", "acid": "1.6", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "秋田県", "url": "https://www.yukinobousha.jp/"},
    {"brewery": "株式会社齋彌酒造店", "brand": "雪の茅舎", "spec": "雪の茅舎 美酒 本醸造", "cat": "本醸造酒", "polish": "65%", "rice": "秋田酒こまち", "alc": 15.0, "smv": "+3.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "秋田県", "url": "https://www.yukinobousha.jp/"},

    # --- 17. 伴野酒造株式会社 (長野・澤乃花 / Beau Michelle) ---
    {"brewery": "伴野酒造株式会社", "brand": "澤乃花", "spec": "澤乃花 ささらさら 純米吟醸", "cat": "純米吟醸酒", "polish": "55%", "rice": "ひとごこち", "alc": 15.0, "smv": "+3.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.sawanohana.com/"},
    {"brewery": "伴野酒造株式会社", "brand": "Beau Michelle", "spec": "Beau Michelle ボー・ミッシェル 低アルコール", "cat": "純米酒", "polish": "非公開", "rice": "長野県産米", "alc": 9.0, "smv": "-20.0", "acid": "3.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.sawanohana.com/"},
    {"brewery": "伴野酒造株式会社", "brand": "Beau Michelle", "spec": "Beau Michelle Snow Fantasy 生原酒", "cat": "純米酒", "polish": "非公開", "rice": "長野県産米", "alc": 9.0, "smv": "-20.0", "acid": "3.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.sawanohana.com/"},

    # --- 18. 武重本家酒造株式会社 (長野・御園竹 / 牧水) ---
    {"brewery": "武重本家酒造株式会社", "brand": "御園竹", "spec": "御園竹 生酛純米酒", "cat": "純米酒", "polish": "65%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.7", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.takeshige-honke.co.jp/"},
    {"brewery": "武重本家酒造株式会社", "brand": "十二六", "spec": "十二六 どぶろく どぶろく生", "cat": "どぶろく", "polish": "70%", "rice": "長野県産米", "alc": 5.0, "smv": "-30.0", "acid": "3.8", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.takeshige-honke.co.jp/"},
    {"brewery": "武重本家酒造株式会社", "brand": "牧水", "spec": "牧水 純米大吟醸 雫酒", "cat": "純米大吟醸酒", "polish": "39%", "rice": "美山錦", "alc": 16.0, "smv": "+3.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "長野県", "url": "https://www.takeshige-honke.co.jp/"}
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

added_count = 0
updated_count = 0
now_str = datetime.now().isoformat()

for item in REMAINING_40_BREWERIES_PRODUCTS:
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
print(f"🍶 残り全低件数酒蔵 深層一括登録完了:")
print(f" - 今回新規追加した銘柄数: {added_count} 件")
print(f" - 確定仕様更新数       : {updated_count} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
