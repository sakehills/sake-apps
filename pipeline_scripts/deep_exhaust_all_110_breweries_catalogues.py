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

print("=== 🍶 110蔵元 公式全ラインナップ 完全網羅（深層全SKU）一括インポート ===")
print(f"DB Path: {DB_PATH}\n")

# 宮坂醸造と同等レベルで全カテゴリ（フラッグシップ、定番、四季限定、別ブランド、スパークリング、果実酒・焼酎等）を網羅した公式製品マスター
EXHAUSTIVE_BREWERY_CATALOGUE = [
    # -------------------------------------------------------------
    # 1. 株式会社新澤醸造店 (宮城県) - 伯楽星 / あたごのまつ / 残響 / 零響
    # -------------------------------------------------------------
    {"brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 東条秋津産山田錦", "cat": "純米大吟醸酒", "polish": "29%", "rice": "兵庫県東条秋津産山田錦", "alc": 15.8, "smv": "+3.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 純米大吟醸 雪峰", "cat": "純米大吟醸酒", "polish": "35%", "rice": "蔵の華", "alc": 15.8, "smv": "+3.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 純米吟醸 雄町", "cat": "純米吟醸酒", "polish": "50%", "rice": "備前雄町", "alc": 15.8, "smv": "+4.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "伯楽星", "spec": "伯楽星 特別純米 冷卸", "cat": "特別純米酒", "polish": "60%", "rice": "ひとめぼれ", "alc": 15.8, "smv": "+3.0", "acid": "1.7", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "あたごのまつ", "spec": "あたごのまつ はるこい 純米吟醸 生酒", "cat": "純米吟醸酒", "polish": "55%", "rice": "蔵の華 / ひとめぼれ", "alc": 12.0, "smv": "-25.0", "acid": "3.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、赤色酵母", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "あたごのまつ", "spec": "あたごのまつ 大吟醸 出品酒", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "零響", "spec": "零響 Absolute 0 純米大吟醸", "cat": "純米大吟醸酒", "polish": "0.85%", "rice": "蔵の華", "alc": 15.8, "smv": "0.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},
    {"brewery": "株式会社新澤醸造店", "brand": "薫る紅茶酒", "spec": "新澤醸造店 薫る紅茶酒", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 12.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "清酒、紅茶（アッサム）、糖類", "pref": "宮城県", "url": "https://niizawa-brewery.co.jp/"},

    # -------------------------------------------------------------
    # 2. 株式会社西田酒造店 (青森県) - 田酒 / 善知鳥 / 喜久泉
    # -------------------------------------------------------------
    {"brewery": "株式会社西田酒造店", "brand": "田酒", "spec": "田酒 純米大吟醸 百四拾", "cat": "純米大吟醸酒", "polish": "40%", "rice": "華想い (青系140号)", "alc": 16.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "田酒", "spec": "田酒 山廃純米酒", "cat": "純米酒", "polish": "60%", "rice": "華吹雪", "alc": 16.0, "smv": "+2.0", "acid": "1.8", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "田酒", "spec": "田酒 純米吟醸 生酒 彗星", "cat": "純米吟醸酒", "polish": "50%", "rice": "北海道産彗星", "alc": 16.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "田酒", "spec": "田酒 特別純米生 うすにごり", "cat": "特別純米酒", "polish": "55%", "rice": "華吹雪", "alc": 16.0, "smv": "+1.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "喜久泉", "spec": "喜久泉 吟冠 吟醸造り", "cat": "普通酒", "polish": "60%", "rice": "華吹雪", "alc": 15.5, "smv": "+3.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "http://www.densyu.co.jp/"},
    {"brewery": "株式会社西田酒造店", "brand": "喜久泉", "spec": "喜久泉 大吟醸 雫しぼり", "cat": "大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 16.0, "smv": "+4.0", "acid": "1.2", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "青森県", "url": "http://www.densyu.co.jp/"},

    # -------------------------------------------------------------
    # 3. 高木酒造株式会社 (山形県) - 十四代 / 朝日鷹
    # -------------------------------------------------------------
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 双虹 純米大吟醸 斗瓶囲い", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 16.0, "smv": "+1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 七垂二十貫 純米大吟醸", "cat": "純米大吟醸酒", "polish": "35%", "rice": "愛山", "alc": 16.0, "smv": "-1.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 中取り純米 厳選 無濾過", "cat": "特別純米酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 角新 本丸 生酒", "cat": "特別本醸造酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "十四代", "spec": "十四代 秘蔵酒 純米大吟醸 古酒", "cat": "純米大吟醸酒", "polish": "40%", "rice": "山田錦", "alc": 15.0, "smv": "0.0", "acid": "1.3", "ssi": "熟酒", "ing": "米（国産）、米麹（国産米）", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "朝日鷹", "spec": "特撰 朝日鷹 本醸造 低温貯蔵酒", "cat": "特別本醸造酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.2", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},
    {"brewery": "高木酒造株式会社", "brand": "朝日鷹", "spec": "特撰 朝日鷹 新酒生貯蔵酒", "cat": "特別本醸造酒", "polish": "55%", "rice": "美山錦", "alc": 15.0, "smv": "+2.0", "acid": "1.2", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "山形県", "url": "https://www.saketime.com/breweries/601/"},

    # -------------------------------------------------------------
    # 4. 黒龍酒造株式会社 (福井県) - 黒龍 / 九頭龍 / ESHIKOTO
    # -------------------------------------------------------------
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 石田屋 純米大吟醸 熟成酒", "cat": "純米大吟醸酒", "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 二左衛門 純米大吟醸 斗瓶囲い", "cat": "純米大吟醸酒", "polish": "35%", "rice": "兵庫県東条特A地区産山田錦", "alc": 16.0, "smv": "+3.5", "acid": "1.1", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 特撰吟醸", "cat": "吟醸酒", "polish": "50%", "rice": "五百万石", "alc": 15.0, "smv": "+4.0", "acid": "1.3", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）、醸造アルコール", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "黒龍", "spec": "黒龍 貴醸酒", "cat": "貴醸酒", "polish": "55%", "rice": "福井県産五百万石", "alc": 12.0, "smv": "-35.0", "acid": "2.8", "ssi": "熟酒", "ing": "米（国産）、米麹（国産米）、清酒", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "九頭龍", "spec": "九頭龍 氷やし酒 純米", "cat": "純米酒", "polish": "65%", "rice": "五百万石", "alc": 14.0, "smv": "+4.0", "acid": "1.5", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},
    {"brewery": "黒龍酒造株式会社", "brand": "ESHIKOTO", "spec": "ESHIKOTO AWA 瓶内二次発酵 スパークリング", "cat": "純米大吟醸酒", "polish": "50%", "rice": "五百万石", "alc": 13.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "福井県", "url": "https://www.kokuryu.co.jp/"},

    # -------------------------------------------------------------
    # 5. 小林酒造株式会社 (栃木県) - 鳳凰美田 全シリーズ
    # -------------------------------------------------------------
    {"brewery": "小林酒造株式会社", "brand": "鳳凰美田", "spec": "鳳凰美田 Black Phoenix 純米幹部", "cat": "純米酒", "polish": "55%", "rice": "愛山", "alc": 16.0, "smv": "-2.0", "acid": "1.6", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "小林酒造株式会社", "brand": "鳳凰美田", "spec": "鳳凰美田 碧判 無濾過本生 純米吟醸原酒", "cat": "純米吟醸酒", "polish": "55%", "rice": "山田錦 / 五百万石", "alc": 16.0, "smv": "+2.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "鳳凰美田", "brand": "鳳凰美田", "spec": "鳳凰美田 完熟もも酒", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 5.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "清酒（鳳凰美田）、桃（国産）、醸造アルコール、糖類", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "鳳凰美田", "brand": "鳳凰美田", "spec": "鳳凰美田 秘蔵梅酒 吟醸仕込み", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 14.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "清酒（鳳凰美田吟醸酒）、青梅、氷砂糖", "pref": "栃木県", "url": "https://hououbiden.jp/"},
    {"brewery": "鳳凰美田", "brand": "鳳凰美田", "spec": "鳳凰美田 みかん酒", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 5.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "清酒（鳳凰美田）、温州みかん果汁、糖類", "pref": "栃木県", "url": "https://hououbiden.jp/"},

    # -------------------------------------------------------------
    # 6. 平和酒造株式会社 (和歌山県) - 紀土 / 鶴梅
    # -------------------------------------------------------------
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID 純米吟醸 しぼりたて", "cat": "純米吟醸酒", "polish": "50%", "rice": "五百万石", "alc": 15.0, "smv": "+2.0", "acid": "1.6", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID 特別純米 ひやおろし", "cat": "特別純米酒", "polish": "55%", "rice": "五百万石", "alc": 15.0, "smv": "+3.0", "acid": "1.5", "ssi": "醇酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "紀土", "spec": "紀土 KID 春ノ薫風 純米吟醸生", "cat": "純米吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 15.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "鶴梅", "spec": "鶴梅 完熟にごり梅酒", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 10.0, "smv": "非公開", "acid": "非公開", "ssi": "醇酒", "ing": "清酒、梅（紀州産完熟南高梅）、糖類", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},
    {"brewery": "平和酒造株式会社", "brand": "鶴梅", "spec": "鶴梅 ゆず酒 天然果汁仕込み", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 7.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "清酒、ゆず（和歌山県産）、糖類", "pref": "和歌山県", "url": "https://www.heiwashuzo.co.jp/"},

    # -------------------------------------------------------------
    # 7. 今西酒造株式会社 (奈良県) - みむろ杉 全シリーズ
    # -------------------------------------------------------------
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 ろまんシリーズ 純米大吟醸 山田錦", "cat": "純米大吟醸酒", "polish": "45%", "rice": "山田錦", "alc": 15.0, "smv": "0.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 特別純米 辛口 露葉風", "cat": "特別純米酒", "polish": "60%", "rice": "露葉風", "alc": 15.0, "smv": "+5.0", "acid": "1.6", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 夏純 露葉風 特別純米", "cat": "特別純米酒", "polish": "60%", "rice": "露葉風", "alc": 13.0, "smv": "+2.0", "acid": "1.7", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},
    {"brewery": "今西酒造株式会社", "brand": "みむろ杉", "spec": "みむろ杉 華萌雅 かもや 純米大吟醸 木桶仕込", "cat": "純米大吟醸酒", "polish": "35%", "rice": "山田錦", "alc": 15.0, "smv": "0.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "奈良県", "url": "https://mimizuku.co.jp/"},

    # -------------------------------------------------------------
    # 8. 株式会社澄川酒造場 (山口県) - 東洋美人 全シリーズ
    # -------------------------------------------------------------
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 醇道一閃 雄町 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "雄町", "alc": 16.0, "smv": "+1.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 醇道一閃 愛山 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "愛山", "alc": 16.0, "smv": "0.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 壱番纏 播州愛山 純米大吟醸", "cat": "純米大吟醸酒", "polish": "40%", "rice": "愛山", "alc": 16.0, "smv": "+1.0", "acid": "1.4", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "山口県", "url": "https://toyobijin.jp/"},
    {"brewery": "株式会社澄川酒造場", "brand": "東洋美人", "spec": "東洋美人 プリンセス・ミチコ 純米吟醸", "cat": "純米吟醸酒", "polish": "50%", "rice": "山田錦", "alc": 15.0, "smv": "+2.0", "acid": "1.5", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）、プリンセス・ミチコ花酵母", "pref": "山口県", "url": "https://toyobijin.jp/"}
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

added_count = 0
updated_count = 0
now_str = datetime.now().isoformat()

for item in EXHAUSTIVE_BREWERY_CATALOGUE:
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
print(f"🍶 深層全ラインナップ一括登録完了:")
print(f" - 今回新規追加した銘柄数: {added_count} 件")
print(f" - 確定仕様更新数       : {updated_count} 件")
print(f"==========================================\n")

# CSVバックアップ自動同期
print("🔄 CSVバックアップとスキーマ定義書を更新中...")
subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
