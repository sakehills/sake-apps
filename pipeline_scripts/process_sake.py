import os
import cv2
import numpy as np
import sqlite3
import json
import shutil
from datetime import datetime
from PIL import Image

# ディレクトリの設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "サンプル画像")
CROPPED_DIR = os.path.join(BASE_DIR, "cropped_images")
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database", os.path.join("..", "database", "sake_database.db"))
JS_DATA_PATH = os.path.join(BASE_DIR, "sake_data.js")

os.makedirs(CROPPED_DIR, exist_ok=True)

# サンプルデータごとのメタデータ定義とクロップ調整オプション
SAKE_METADATA_TEMPLATES = {
    "1": {
        "english_name": "Beau_Michelle",
        "brand_name": "Beau Michelle",
        "sub_name": "Beau Michelle Snow fantasy in Summer",
        "brewery": "伴野酒造株式会社",
        "brewery_address": "長野県佐久市野沢123",
        "sake_type": "うすにごり生原酒",
        "alcohol_content": 9.0,
        "raw_materials": "米(国産)、米麹(国産米) ※酒造好適米100%使用",
        "polishing_rate": "60%",
        "volume": "500ml",
        "manufactured_date": "2026.05",
        "rice_variety": "米(国産)",
        "yeast": "非公開",
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "crop_options": {
            "top_crop_ratio": 0.0,
            "bottom_crop_ratio": 0.0,
            "left_crop_ratio": 0.0,
            "right_crop_ratio": 0.0,
            "margin_w_ratio": 0.04
        }
    },
    "2": {
        "english_name": "Leiro",
        "brand_name": "浪の音",
        "sub_name": "浪の音 玲瓏 -レイロウ- Leiro",
        "brewery": "有限会社佐々木酒造店",
        "brewery_address": "宮城県名取市閖上中央一丁目12番地の3",
        "sake_type": "純米吟醸",
        "alcohol_content": 15.0,
        "raw_materials": "米(国産)、米麹(国産米)",
        "polishing_rate": "55%",
        "volume": "720ml",
        "manufactured_date": "2026.06",
        "rice_variety": "非公開",
        "yeast": "非公開",
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "crop_options": {
            "top_crop_ratio": 0.0,
            "bottom_crop_ratio": 0.0,
            "left_crop_ratio": 0.0,
            "right_crop_ratio": 0.0,
            "margin_w_ratio": 0.04
        }
    },
    "３": {
        "english_name": "Koshi_no_Hatsume",
        "brand_name": "越の初梅",
        "sub_name": "越の初梅 元祖 雪中貯蔵酒",
        "brewery": "高の井酒造株式会社",
        "brewery_address": "新潟県小千谷市東栄三丁目7番6号",
        "sake_type": "純米吟醸",
        "alcohol_content": 15.0,
        "raw_materials": "米（国産）、米麹（国産米）",
        "polishing_rate": "55%",
        "volume": "720ml",
        "manufactured_date": "不明",
        "rice_variety": "非公開",
        "yeast": "非公開",
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "crop_options": {
            "top_crop_ratio": 0.02,
            "bottom_crop_ratio": 0.02,
            "left_crop_ratio": 0.0,
            "right_crop_ratio": 0.0,
            "margin_w_ratio": 0.04
        }
    },
    "４": {
        "english_name": "Ikekame",
        "brand_name": "池亀",
        "sub_name": "け・せら・せら Ikekame",
        "brewery": "池亀酒造株式会社",
        "brewery_address": "福岡県久留米市三潴町田川",
        "sake_type": "非公開",
        "alcohol_content": 13.0,
        "raw_materials": "米(国産)、米麹(国産米)",
        "polishing_rate": "非公開",
        "volume": "720ml",
        "manufactured_date": "2026.04",
        "rice_variety": "非公開",
        "yeast": "非公開",
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "crop_options": {
            "top_crop_ratio": 0.0,
            "bottom_crop_ratio": 0.0,
            "left_crop_ratio": 0.0,
            "right_crop_ratio": 0.0,
            "margin_w_ratio": 0.04
        }
    },
    "５": {
        "english_name": "Hirotogawa",
        "brand_name": "廣戸川",
        "sub_name": "廣戸川 特別純米",
        "brewery": "松崎酒造株式会社",
        "brewery_address": "福島県岩瀬郡天栄村大字下松本字要谷47-1",
        "sake_type": "特別純米",
        "alcohol_content": 15.0,
        "raw_materials": "米(国産)、米麹(国産米)",
        "polishing_rate": "55%",
        "volume": "720ml",
        "manufactured_date": "2026.05",
        "rice_variety": "米(国産)",
        "yeast": "非公開",
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "crop_options": {
            "top_crop_ratio": 0.0,
            "bottom_crop_ratio": 0.0,
            "left_crop_ratio": 0.0,
            "right_crop_ratio": 0.0,
            "margin_w_ratio": 0.04
        }
    },
    "６": {
        "english_name": "Shosetsu",
        "brand_name": "正雪",
        "sub_name": "正雪 これだれ TASHINAMI",
        "brewery": "株式会社神沢川酒造場",
        "brewery_address": "静岡県静岡市清水区由比181",
        "sake_type": "純米吟醸",
        "alcohol_content": 15.5,
        "raw_materials": "米(国産)、米麹(国産米)",
        "polishing_rate": "50%",
        "volume": "1.8L",
        "manufactured_date": "2026.06",
        "rice_variety": "米(国産)",
        "yeast": "非公開",
        "smv": "非公開",
        "acidity": "非公開",
        "amino_acidity": "非公開",
        "crop_options": {
            "top_crop_ratio": 0.38,
            "bottom_crop_ratio": 0.04,
            "left_crop_ratio": 0.0,
            "right_crop_ratio": 0.0,
            "margin_w_ratio": 0.05
        }
    },
    "7": {
        "is_multi_split": True,
        "brewery": "油長酒造株式会社",
        "brewery_address": "奈良県御所市本町1160",
        "brand_name": "風の森",
        "sake_list": [
            {
                "english_name": "Kazemonori_Omachi_807",
                "sub_name": "風の森 雄町 807",
                "sake_type": "純米酒",
                "alcohol_content": 16.0,
                "raw_materials": "米(国産)、米麹(国産米) ※奈良県産雄町100%使用",
                "polishing_rate": "80%",
                "volume": "720ml",
                "manufactured_date": "2026.05",
                "rice_variety": "奈良県産雄町",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 0
            },
            {
                "english_name": "Kazemonori_Challenge_Edition",
                "sub_name": "風の森 CHALLENGE EDITION TYPE 2",
                "sake_type": "試験醸造酒",
                "alcohol_content": 16.0,
                "raw_materials": "米(国産)、米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "2026.04",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 1
            },
            {
                "english_name": "Kazemonori_Tsuyuyakaze_807",
                "sub_name": "風の森 露葉風 807",
                "sake_type": "純米酒",
                "alcohol_content": 16.0,
                "raw_materials": "米(国産)、米麹(国産米) ※奈良県産露葉風100%使用",
                "polishing_rate": "80%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "奈良県産露葉風",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 2
            },
            {
                "english_name": "Kazemonori_Akitsubo_657",
                "sub_name": "風の森 秋津穂 657",
                "sake_type": "純米酒",
                "alcohol_content": 16.0,
                "raw_materials": "米(国産)、米麹(国産米) ※奈良県産秋津穂100%使用",
                "polishing_rate": "65%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "奈良県産秋津穂",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 3
            },
            {
                "english_name": "Kazemonori_Akitsubo_507",
                "sub_name": "風の森 秋津穂 507",
                "sake_type": "純米大吟醸",
                "alcohol_content": 16.0,
                "raw_materials": "米(国産), 米麹(国産米) ※奈良県産秋津穂100%使用",
                "polishing_rate": "50%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "奈良県産秋津穂",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 4
            }
        ]
    },
    "８": {
        "is_multi_split_vertical": True,
        "brewery": "阿部酒造",
        "brewery_address": "新潟県柏崎市大字安田3500",
        "brand_name": "あべ",
        "sake_list": [
            {
                "english_name": "Abe_Blue",
                "sub_name": "あべ 青文字",
                "sake_type": "純米酒",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 0
            },
            {
                "english_name": "Abe_Regulus_2025",
                "sub_name": "あべ REGULUS 2025",
                "sake_type": "純米酒",
                "alcohol_content": 13.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "2026.05",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 1
            },
            {
                "english_name": "Abe_Regulus_2024",
                "sub_name": "あべ REGULUS 2024",
                "sake_type": "純米酒",
                "alcohol_content": 13.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "2025.05",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 2
            },
            {
                "english_name": "Abe_Regulus_2023",
                "sub_name": "あべ REGULUS 2023",
                "sake_type": "純米酒",
                "alcohol_content": 13.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "2024.05",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 3
            }
        ]
    },
    "９": {
        "is_multi_split_horizontal_2": True,
        "sake_list": [
            {
                "english_name": "Hamamusume_Seimoto",
                "brand_name": "浜娘",
                "sub_name": "浜娘 岩手限定生酛純米酒",
                "brewery": "株式会社赤武酒造",
                "brewery_address": "岩手県盛岡市北飯岡1-8-15",
                "sake_type": "生酛純米",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "1.8L",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 0
            },
            {
                "english_name": "Mimuro_Sugi_Minna_no_Saganou",
                "brand_name": "みむろ杉",
                "sub_name": "みむろ杉 みんなのさがのう",
                "brewery": "今西酒造株式会社",
                "brewery_address": "奈良県桜井市大字三輪310番地",
                "sake_type": "純米酒",
                "alcohol_content": 13.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 1
            }
        ]
    },
    "１０": {
        "is_multi_split_no_rotation_6": True,
        "crop_y_ratio": 0.30,
        "crop_h_ratio": 0.65,
        "start_x_ratio": 0.20,
        "end_x_ratio": 0.84,
        "sake_list": [
            {
                "english_name": "U Tashiro",
                "brand_name": "雅楽代",
                "sub_name": "雅楽代 薄緑",
                "brewery": "天領盃酒造株式会社",
                "brewery_address": "新潟県佐渡市加茂歌代61",
                "sake_type": "非公開",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "非公開",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 0
            },
            {
                "english_name": "Miyasaka_Miyama",
                "brand_name": "MIYASAKA",
                "sub_name": "MIYASAKA 美山錦",
                "brewery": "宮坂醸造株式会社",
                "brewery_address": "長野県諏訪市元町3-16",
                "sake_type": "純米吟醸",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "55%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "美山錦",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 1
            },
            {
                "english_name": "Suehiro_Yamahai",
                "brand_name": "末廣",
                "sub_name": "末廣 伝承山廃純米",
                "brewery": "末廣酒造株式会社",
                "brewery_address": "福島県会津若松市日新町12-38",
                "sake_type": "山廃純米",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "60%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 2
            },
            {
                "english_name": "Toko_Genshu",
                "brand_name": "東光",
                "sub_name": "東光 純米吟醸 原酒",
                "brewery": "株式会社小嶋総本店",
                "brewery_address": "山形県米沢市本町2-2-3",
                "sake_type": "純米吟醸",
                "alcohol_content": 16.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "55%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 3
            },
            {
                "english_name": "Akinota_Ginjyo",
                "brand_name": "秋の田",
                "sub_name": "秋の田 純米吟醸",
                "brewery": "合資会社高橋庄作商店",
                "brewery_address": "福島県会津若松市門田町大字一ノ堰字村東755",
                "sake_type": "純米吟醸",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "50%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 4
            },
            {
                "english_name": "Yamawa_Tokubetsu",
                "brand_name": "山和",
                "sub_name": "山和 特別純米 60",
                "brewery": "株式会社山和酒造店",
                "brewery_address": "宮城県加美郡加美町字南町11",
                "sake_type": "特別純米",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "60%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 5
            }
        ]
    },
    "１１": {
        "is_multi_split_no_rotation_6": True,
        "crop_y_ratio": 0.20,
        "crop_h_ratio": 0.78,
        "start_x_ratio": 0.06,
        "end_x_ratio": 0.96,
        "sake_list": [
            {
                "english_name": "Ichinokura_Hogin",
                "brand_name": "一ノ蔵",
                "sub_name": "一ノ蔵 芳吟",
                "brewery": "株式会社一ノ蔵",
                "brewery_address": "宮城県大崎市松山千石字大欅14",
                "sake_type": "純米吟醸",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "50%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 0
            },
            {
                "english_name": "Koganesawa_Iroha",
                "brand_name": "黄金澤",
                "sub_name": "黄金澤 吟のいろは 純米吟醸",
                "brewery": "合名会社川敬商店",
                "brewery_address": "宮城県美里町二郷字上前八号1",
                "sake_type": "純米吟醸",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "50%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "吟のいろは",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 1
            },
            {
                "english_name": "Masumi_Yusuijikomi",
                "brand_name": "真澄",
                "sub_name": "真澄 湧水仕込 純米酒",
                "brewery": "宮坂醸造株式会社",
                "brewery_address": "長野県諏訪市元町3-16",
                "sake_type": "純米酒",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "65%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 2
            },
            {
                "english_name": "Toshimori_Akaiwa_Omachi",
                "brand_name": "赤磐雄町",
                "sub_name": "利守 赤磐雄町 特別純米酒",
                "brewery": "利守酒造株式会社",
                "brewery_address": "岡山県赤磐市西中1342-1",
                "sake_type": "特別純米",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "60%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 3
            },
            {
                "english_name": "Kaiun_Ginjyo",
                "brand_name": "開運",
                "sub_name": "開運 純米吟醸",
                "brewery": "株式会社土井酒造場",
                "brewery_address": "静岡県掛川市小貫633",
                "sake_type": "純米吟醸",
                "alcohol_content": 15.5,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "50%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 4
            },
            {
                "english_name": "Sekimusume_Yamahai",
                "brand_name": "関娘",
                "sub_name": "関娘 山廃仕込 純米酒",
                "brewery": "下関酒造株式会社",
                "brewery_address": "山口県下関市幡生宮の下町8-23",
                "sake_type": "純米酒",
                "alcohol_content": 15.0,
                "raw_materials": "米(国産), 米麹(国産米)",
                "polishing_rate": "65%",
                "volume": "720ml",
                "manufactured_date": "不明",
                "rice_variety": "非公開",
                "yeast": "非公開",
                "smv": "非公開",
                "acidity": "非公開",
                "amino_acidity": "非公開",
                "split_index": 5
            }
        ]
    }
}

def imread_unicode(path):
    with open(path, 'rb') as f:
        img_pil = Image.open(f)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    result, nparr = cv2.imencode(ext, img)
    if result:
        with open(path, 'wb') as f:
            f.write(nparr.tobytes())
        return True
    return False

def crop_bottle(image_path, output_path, crop_options=None):
    if crop_options is None:
        crop_options = {}

    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"画像を読み込めませんでした: {image_path}")

    rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    h, w, _ = rotated.shape

    gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    center_x_start = int(w * 0.25)
    center_x_end = int(w * 0.75)
    
    intersecting_boxes = []
    
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if cw < 20 or ch < 20:
            continue
        if not (x + cw < center_x_start or x > center_x_end):
            intersecting_boxes.append((x, y, x + cw, y + ch))
            
    if len(intersecting_boxes) > 0:
        min_x = min(box[0] for box in intersecting_boxes)
        min_y = min(box[1] for box in intersecting_boxes)
        max_x = max(box[2] for box in intersecting_boxes)
        max_y = max(box[3] for box in intersecting_boxes)
        
        detected_h = max_y - min_y
        if detected_h > (h * 0.3):
            margin_w_ratio = crop_options.get('margin_w_ratio', 0.04)
            margin_w = int((max_x - min_x) * margin_w_ratio)
            margin_h = 0
            
            crop_x = max(0, min_x - margin_w)
            crop_y = max(0, min_y - margin_h)
            crop_w = min(w - crop_x, (max_x - min_x) + (margin_w * 2))
            crop_h = min(h - crop_y, (max_y - min_y) + (margin_h * 2))
        else:
            intersecting_boxes = []
            
    if len(intersecting_boxes) == 0:
        crop_x = int(w * 0.25)
        crop_y = int(h * 0.02)
        crop_w = int(w * 0.50)
        crop_h = int(h * 0.96)
        
    top_crop_ratio = crop_options.get('top_crop_ratio', 0.0)
    bottom_crop_ratio = crop_options.get('bottom_crop_ratio', 0.0)
    
    if top_crop_ratio > 0.0 or bottom_crop_ratio > 0.0:
        original_h = crop_h
        crop_y = crop_y + int(original_h * top_crop_ratio)
        crop_h = original_h - int(original_h * top_crop_ratio) - int(original_h * bottom_crop_ratio)
        
    left_crop_ratio = crop_options.get('left_crop_ratio', 0.0)
    right_crop_ratio = crop_options.get('right_crop_ratio', 0.0)
    
    if left_crop_ratio > 0.0 or right_crop_ratio > 0.0:
        original_w = crop_w
        crop_x = crop_x + int(original_w * left_crop_ratio)
        crop_w = original_w - int(original_w * left_crop_ratio) - int(original_w * right_crop_ratio)
        
    cropped = rotated[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
    imwrite_unicode(output_path, cropped)
    return output_path

def crop_bottle_split(image_path, output_path, split_index):
    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"画像を読み込めませんでした: {image_path}")

    rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    h, w, _ = rotated.shape

    actual_index = 4 - split_index
    
    split_width_ratio = 0.20
    start_ratio = actual_index * 0.20
    
    crop_x = int(w * start_ratio)
    crop_w = int(w * split_width_ratio)
    
    crop_y = int(h * 0.12)
    crop_h = int(h * 0.76)
    
    cropped = rotated[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
    imwrite_unicode(output_path, cropped)
    return output_path

def crop_bottle_split_vertical(image_path, output_path, split_index):
    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"画像を読み込めませんでした: {image_path}")

    rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    h, w, _ = rotated.shape

    actual_index = 3 - split_index
    
    split_width_ratio = 0.115
    start_ratio = 0.50 + actual_index * 0.115
    
    crop_x = int(w * start_ratio)
    crop_w = int(w * split_width_ratio)
    
    crop_y = int(h * 0.45)
    crop_h = int(h * 0.42)
    
    cropped = rotated[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
    imwrite_unicode(output_path, cropped)
    return output_path

def crop_bottle_split_horizontal_2(image_path, output_path, split_index):
    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"画像を読み込めませんでした: {image_path}")

    rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    h, w, _ = rotated.shape

    if split_index == 0:
        crop_x = int(w * 0.03)
        crop_w = int(w * 0.48)
        crop_y = int(h * 0.06)
        crop_h = int(h * 0.90)
    else:
        crop_x = int(w * 0.52)
        crop_w = int(w * 0.44)
        crop_y = int(h * 0.08)
        crop_h = int(h * 0.88)
        
    cropped = rotated[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
    imwrite_unicode(output_path, cropped)
    return output_path

def crop_bottle_split_no_rotation_6(image_path, output_path, split_index, y_ratio, h_ratio, start_x, end_x):
    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"画像を読み込めませんでした: {image_path}")

    h, w, _ = img.shape
    
    effective_w = end_x - start_x
    split_w_ratio = effective_w / 6.0
    
    start_ratio = start_x + split_index * split_w_ratio
    
    crop_x = int(w * start_ratio)
    crop_w = int(w * split_w_ratio)
    
    crop_y = int(h * y_ratio)
    crop_h = int(h * h_ratio)
    
    cropped = img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
    imwrite_unicode(output_path, cropped)
    return output_path

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 既存コメントデータ（user_flavor_ratings）を退避
    existing_ratings = []
    try:
        cursor.execute("SELECT product_id, ssi_type, body_level, aroma_level, comment, user_id, user_name, created_at, rating_image, total_score, taste_score, aroma_score FROM user_flavor_ratings")
        existing_ratings = cursor.fetchall()
    except sqlite3.OperationalError:
        pass
        
    cursor.execute("DROP TABLE IF EXISTS user_flavor_ratings")
    cursor.execute("DROP TABLE IF EXISTS products")
    
    # 1. products (機械収集 ＋ 機械サマリー)
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spec_name TEXT NOT NULL,
            brewery_name TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            category TEXT,
            ingredients TEXT,
            polish_ratio TEXT,
            rice_variety TEXT,
            yeast TEXT,
            alcohol REAL,
            smv TEXT,
            acidity TEXT,
            amino_acidity TEXT,
            cropped_image_path_front TEXT,
            cropped_image_path_back TEXT,
            ssi_type TEXT,
            body_level TEXT,
            aroma_level TEXT,
            comment TEXT,
            status TEXT DEFAULT 'draft',
            confidence REAL DEFAULT 0.9,
            source_id TEXT,
            evidence TEXT,
            created_at TEXT
        )
    """)
    
    # 2. user_flavor_ratings (人間追加レビューのみ)
    cursor.execute("""
        CREATE TABLE user_flavor_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_name TEXT DEFAULT '匿名',
            ssi_type TEXT,
            body_level TEXT,
            aroma_level TEXT,
            comment TEXT,
            rating_image TEXT,
            user_id TEXT DEFAULT 'test_seed_secondary_sources',
            created_at TEXT,
            total_score REAL,
            taste_score REAL,
            aroma_score REAL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)
    
    # 退避したコメントを復元 (hitocieによる初期ダミーデータは、この後の collect_web_ratings で移行するので、ここではhitocie以外のデータのみ復元します)
    for r in existing_ratings:
        if r[6] != 'hitocie':
            cursor.execute("""
                INSERT INTO user_flavor_ratings (
                    product_id, ssi_type, body_level, aroma_level, comment, user_id, user_name, created_at, rating_image, total_score, taste_score, aroma_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, r)
        
    conn.commit()
    conn.close()

def insert_sake_data(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO products (
            spec_name, brewery_name, brand_name, category, ingredients,
            polish_ratio, rice_variety, yeast, alcohol, smv, acidity, amino_acidity,
            ssi_type, body_level, aroma_level, comment,
            status, confidence, source_id, evidence, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['spec_name'], data['brewery_name'], data['brand_name'], data['category'],
        data['ingredients'], data['polish_ratio'], data['rice_variety'], data['yeast'],
        data['alcohol'], data['smv'], data['acidity'], data['amino_acidity'],
        data.get('ssi_type'), data.get('body_level'), data.get('aroma_level'), data.get('comment'),
        data.get('status', 'draft'), data.get('confidence', 0.9), data.get('source_id', 'camera_raw'),
        data.get('evidence', 'labels'), datetime.now().isoformat()
    ))
    
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id

def update_cropped_paths(product_id, cropped_front, cropped_back):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET
            cropped_image_path_front = ?,
            cropped_image_path_back = ?
        WHERE id = ?
    """, (cropped_front, cropped_back, product_id))
    conn.commit()
    conn.close()

def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('cp932', errors='replace').decode('cp932'))

def export_to_js():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. products 全体を取得 (products直下の ssi_type, body_level, aroma_level, comment を含みます)
    cursor.execute("""
        SELECT 
            p.id as id,
            p.brand_name as name,
            p.spec_name as sub_name,
            p.brewery_name as brewery,
            p.category as sake_type,
            p.alcohol as alcohol_content,
            p.ingredients as raw_materials,
            p.polish_ratio as polishing_rate,
            p.rice_variety as rice_variety,
            p.yeast as yeast,
            p.smv as smv,
            p.acidity as acidity,
            p.amino_acidity as amino_acidity,
            p.cropped_image_path_front as cropped_image_path_front,
            p.cropped_image_path_back as cropped_image_path_back,
            p.ssi_type as ssi_type,
            p.body_level as body_level,
            p.aroma_level as aroma_level,
            p.comment as comment
        FROM products p
        ORDER BY p.id ASC
    """)
    products = [dict(row) for row in cursor.fetchall()]
    
    # 2. 各商品に関連するすべてのユーザー評価リスト(1対多)を抽出してネストする
    for p in products:
        cursor.execute("""
            SELECT ssi_type, body_level, aroma_level, comment, user_name, created_at, rating_image, total_score, taste_score, aroma_score
            FROM user_flavor_ratings
            WHERE product_id = ?
            ORDER BY id DESC
        """, (p['id'],))
        p['ratings'] = [dict(r) for r in cursor.fetchall()]
        
        # 相対パス変換
        if p['cropped_image_path_front']:
            p['cropped_image_path_front'] = os.path.relpath(p['cropped_image_path_front'], BASE_DIR).replace('\\', '/')
        if p['cropped_image_path_back']:
            p['cropped_image_path_back'] = os.path.relpath(p['cropped_image_path_back'], BASE_DIR).replace('\\', '/')
            
    conn.close()
    
    js_content = f"const sakeData = {json.dumps(products, ensure_ascii=False, indent=2)};"
    with open(JS_DATA_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)
    safe_print(f"JSデータを出力しました: {JS_DATA_PATH}")

def main():
    safe_print("データベースを初期化します...")
    init_database()
    
    folders = sorted(os.listdir(SAMPLE_DIR))
    
    for folder in folders:
        folder_path = os.path.join(SAMPLE_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
            
        if folder not in SAKE_METADATA_TEMPLATES:
            continue
            
        safe_print(f"\n--- フォルダ '{folder}' の処理を開始します ---")
        folder_config = SAKE_METADATA_TEMPLATES[folder]
        
        images = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpeg', '.jpg', '.png'))])
        if not images:
            continue
            
        # 全てのフォルダは画像再切り出しをスキップ
        is_skipped = True
        
        if folder_config.get('is_multi_split_no_rotation_6', False):
            img_name = images[0]
            original_img_path = os.path.join(folder_path, img_name)
            sake_list = folder_config['sake_list']
            y_ratio = folder_config['crop_y_ratio']
            h_ratio = folder_config['crop_h_ratio']
            start_x = folder_config['start_x_ratio']
            end_x = folder_config['end_x_ratio']
            
            for item in sake_list:
                product_data = {
                    "spec_name": item["sub_name"],
                    "brewery_name": item["brewery"],
                    "brand_name": item["brand_name"],
                    "category": item["sake_type"],
                    "ingredients": item["raw_materials"],
                    "polish_ratio": item["polishing_rate"],
                    "rice_variety": item["rice_variety"],
                    "yeast": item["yeast"],
                    "alcohol": item["alcohol_content"],
                    "smv": item["smv"],
                    "acidity": item["acidity"],
                    "amino_acidity": item["amino_acidity"],
                    "status": "draft",
                    "confidence": 0.9,
                    "source_id": "camera_no_rotation_6split",
                    "evidence": "label snippet"
                }
                
                product_id = insert_sake_data(product_data)
                
                brewery_folder = os.path.join(CROPPED_DIR, product_data['brewery_name'])
                os.makedirs(brewery_folder, exist_ok=True)
                
                id_str = f"id_{product_id:03d}"
                eng_name = item['english_name']
                cropped_filename = f"{id_str}_{eng_name}_front.jpeg"
                cropped_dest = os.path.join(brewery_folder, cropped_filename)
                
                if not is_skipped:
                    crop_bottle_split_no_rotation_6(original_img_path, cropped_dest, item['split_index'], y_ratio, h_ratio, start_x, end_x)
                
                update_cropped_paths(product_id, cropped_dest, None)
                safe_print(f"DBに登録しました (採番ID: {product_id}, {item['sub_name']})")

        elif folder_config.get('is_multi_split', False):
            img_name = images[0]
            original_img_path = os.path.join(folder_path, img_name)
            sake_list = folder_config['sake_list']
            
            for item in sake_list:
                product_data = {
                    "spec_name": item["sub_name"],
                    "brewery_name": folder_config["brewery"],
                    "brand_name": folder_config["brand_name"],
                    "category": item["sake_type"],
                    "ingredients": item["raw_materials"],
                    "polish_ratio": item["polishing_rate"],
                    "rice_variety": item["rice_variety"],
                    "yeast": item["yeast"],
                    "alcohol": item["alcohol_content"],
                    "smv": item["smv"],
                    "acidity": item["acidity"],
                    "amino_acidity": item["amino_acidity"],
                    "status": "draft",
                    "confidence": 0.9,
                    "source_id": "camera_front_split",
                    "evidence": "label snippet"
                }
                
                product_id = insert_sake_data(product_data)
                
                brewery_folder = os.path.join(CROPPED_DIR, product_data['brewery_name'])
                os.makedirs(brewery_folder, exist_ok=True)
                
                id_str = f"id_{product_id:03d}"
                eng_name = item['english_name']
                cropped_filename = f"{id_str}_{eng_name}_front.jpeg"
                cropped_dest = os.path.join(brewery_folder, cropped_filename)
                
                if not is_skipped:
                    crop_bottle_split(original_img_path, cropped_dest, item['split_index'])
                
                update_cropped_paths(product_id, cropped_dest, None)
                safe_print(f"DBに登録しました (採番ID: {product_id}, {item['sub_name']})")
                
        elif folder_config.get('is_multi_split_vertical', False):
            img_name = images[0]
            original_img_path = os.path.join(folder_path, img_name)
            sake_list = folder_config['sake_list']
            
            for item in sake_list:
                product_data = {
                    "spec_name": item["sub_name"],
                    "brewery_name": folder_config["brewery"],
                    "brand_name": folder_config["brand_name"],
                    "category": item["sake_type"],
                    "ingredients": item["raw_materials"],
                    "polish_ratio": item["polishing_rate"],
                    "rice_variety": item["rice_variety"],
                    "yeast": item["yeast"],
                    "alcohol": item["alcohol_content"],
                    "smv": item["smv"],
                    "acidity": item["acidity"],
                    "amino_acidity": item["amino_acidity"],
                    "status": "draft",
                    "confidence": 0.9,
                    "source_id": "camera_vertical_split",
                    "evidence": "label snippet"
                }
                
                product_id = insert_sake_data(product_data)
                
                brewery_folder = os.path.join(CROPPED_DIR, product_data['brewery_name'])
                os.makedirs(brewery_folder, exist_ok=True)
                
                id_str = f"id_{product_id:03d}"
                eng_name = item['english_name']
                cropped_filename = f"{id_str}_{eng_name}_front.jpeg"
                cropped_dest = os.path.join(brewery_folder, cropped_filename)
                
                if not is_skipped:
                    crop_bottle_split_vertical(original_img_path, cropped_dest, item['split_index'])
                
                update_cropped_paths(product_id, cropped_dest, None)
                safe_print(f"DBに登録しました (採番ID: {product_id}, {item['sub_name']})")
                
        elif folder_config.get('is_multi_split_horizontal_2', False):
            img_name = images[0]
            original_img_path = os.path.join(folder_path, img_name)
            sake_list = folder_config['sake_list']
            
            for item in sake_list:
                product_data = {
                    "spec_name": item["sub_name"],
                    "brewery_name": item["brewery"],
                    "brand_name": item["brand_name"],
                    "category": item["sake_type"],
                    "ingredients": item["raw_materials"],
                    "polish_ratio": item["polishing_rate"],
                    "rice_variety": item["rice_variety"],
                    "yeast": item["yeast"],
                    "alcohol": item["alcohol_content"],
                    "smv": item["smv"],
                    "acidity": item["acidity"],
                    "amino_acidity": item["amino_acidity"],
                    "status": "draft",
                    "confidence": 0.9,
                    "source_id": "camera_2split",
                    "evidence": "label snippet"
                }
                
                product_id = insert_sake_data(product_data)
                
                brewery_folder = os.path.join(CROPPED_DIR, product_data['brewery_name'])
                os.makedirs(brewery_folder, exist_ok=True)
                
                id_str = f"id_{product_id:03d}"
                eng_name = item['english_name']
                cropped_filename = f"{id_str}_{eng_name}_front.jpeg"
                cropped_dest = os.path.join(brewery_folder, cropped_filename)
                
                if not is_skipped:
                    crop_bottle_split_horizontal_2(original_img_path, cropped_dest, item['split_index'])
                
                update_cropped_paths(product_id, cropped_dest, None)
                safe_print(f"DBに登録しました (採番ID: {product_id}, {item['sub_name']})")
                
        else:
            # 単一ボトル画像
            crop_opts = folder_config.get('crop_options', {})
            
            product_data = {
                "spec_name": folder_config["sub_name"],
                "brewery_name": folder_config["brewery"],
                "brand_name": folder_config["brand_name"],
                "category": folder_config["sake_type"],
                "ingredients": folder_config["raw_materials"],
                "polish_ratio": folder_config["polishing_rate"],
                "rice_variety": folder_config["rice_variety"],
                "yeast": folder_config["yeast"],
                "alcohol": folder_config["alcohol_content"],
                "smv": folder_config["smv"],
                "acidity": folder_config["acidity"],
                "amino_acidity": folder_config["amino_acidity"],
                "status": "draft",
                "confidence": 0.9,
                "source_id": "camera_single",
                "evidence": "label snippet"
            }
            
            product_id = insert_sake_data(product_data)
            
            brewery_folder = os.path.join(CROPPED_DIR, product_data['brewery_name'])
            os.makedirs(brewery_folder, exist_ok=True)
            
            id_str = f"id_{product_id:03d}"
            eng_name = folder_config['english_name']
            
            img_front_name = images[0]
            img_back_name = images[1] if len(images) > 1 else None
            
            cropped_front_filename = f"{id_str}_{eng_name}_front.jpeg"
            cropped_back_filename = f"{id_str}_{eng_name}_back.jpeg" if img_back_name else None
            
            cropped_front_dest = os.path.join(brewery_folder, cropped_front_filename)
            cropped_back_dest = os.path.join(brewery_folder, cropped_back_filename) if cropped_back_filename else None
            
            if not is_skipped:
                crop_bottle(os.path.join(folder_path, img_front_name), cropped_front_dest, crop_opts)
                if img_back_name:
                    crop_bottle(os.path.join(folder_path, img_back_name), cropped_back_dest, crop_opts)
                
            update_cropped_paths(product_id, cropped_front_dest, cropped_back_dest)
            safe_print(f"DBに登録しました (採番ID: {product_id}, {product_data['spec_name']})")
            
    export_to_js()
    safe_print("\nすべての処理が正常に完了しました。")

if __name__ == "__main__":
    main()
