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

BIJOFU_MORE = [
    {"spec": "美丈夫 慎太郎 特別純米酒", "brand": "美丈夫", "cat": "特別純米酒", "polish": "60%", "rice": "松山三井", "alc": 15.0, "smv": "+4.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "高知県", "url": "https://bijofu.jp/"},
    {"spec": "美丈夫 舞 しずく媛 純米大吟醸", "brand": "美丈夫", "cat": "純米大吟醸酒", "polish": "50%", "rice": "しずく媛", "alc": 15.0, "smv": "+3.0", "acid": "1.3", "ssi": "薫酒", "ing": "米（国産）、米麹（国産米）", "pref": "高知県", "url": "https://bijofu.jp/"},
    {"spec": "美丈夫 ぽんかんリキュール", "brand": "美丈夫", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 7.0, "smv": "非公開", "acid": "非公開", "ssi": "薫酒", "ing": "本格焼酎、ぽんかん果汁（高知県産）、糖類", "pref": "高知県", "url": "https://bijofu.jp/"},
    {"spec": "美丈夫 ゆずしゅわ スパークリング", "brand": "美丈夫", "cat": "リキュール", "polish": "非公開", "rice": "国産米", "alc": 6.0, "smv": "非公開", "acid": "非公開", "ssi": "爽酒", "ing": "清酒（美丈夫）、ゆず果汁、糖類、炭酸", "pref": "高知県", "url": "https://bijofu.jp/"},
    {"spec": "美丈夫 純米吟醸 純麗 TAMA", "brand": "美丈夫", "cat": "純米吟醸酒", "polish": "55%", "rice": "松山三井", "alc": 15.0, "smv": "+3.0", "acid": "1.4", "ssi": "爽酒", "ing": "米（国産）、米麹（国産米）", "pref": "高知県", "url": "https://bijofu.jp/"}
]

for p in BIJOFU_MORE:
    cur.execute("SELECT id FROM products WHERE spec_name = ?", (p['spec'],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO products (
                brand_name, spec_name, category, polish_ratio, rice_variety,
                alcohol, smv, acidity, ssi_type, ingredients,
                brewery_name, prefecture, confidence, evidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '有限会社濱川商店', ?, 1.0, ?, 'active')
        """, (p['brand'], p['spec'], p['cat'], p['polish'], p['rice'], p['alc'], p['smv'], p['acid'], p['ssi'], p['ing'], p['pref'], f"Official Verified ({p['url']})"))

conn.commit()
conn.close()

subprocess.run([sys.executable, os.path.join(ROOT_DIR, "export_database_backup.py")])
