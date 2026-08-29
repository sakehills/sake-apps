import os
import sys
import sqlite3
import csv
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
BACKUP_DIR = os.path.join(ROOT_DIR, "database-backup")

# テーブルごとの日本語名称・概要
TABLE_METADATA = {
    "products": {
        "jp_name": "日本酒製品・スペック",
        "description": "日本酒の個別商品・製品スペック情報（特定名称、原料米、精米歩合、度数、日本酒度、酸度、SSI分類、ラベル画像、公式エビデンス等）を保持するメインテーブル。"
    },
    "breweries": {
        "jp_name": "酒蔵・蔵元マスタ",
        "description": "日本全国の日本酒製造業者・酒蔵情報（法人番号、所在地、緯度経度、創業年、公式サイト、見学可否、直売所有無等）を保持するマスタテーブル。"
    },
    "brands": {
        "jp_name": "銘柄・ブランドマスタ",
        "description": "酒蔵に紐づく代表銘柄・ブランド名（漢字、ふりがな、英字表記）を管理するマスタテーブル。"
    },
    "user_flavor_ratings": {
        "jp_name": "ユーザー評価・レビュー",
        "description": "一般ユーザーおよびテイスターによる評価スコア（総合点・味わい点・香り点）、自由記述コメント、味わいチャート（SSI・TOSA方式）、投稿写真等を保持するテーブル。"
    },
    "awards": {
        "jp_name": "コンテスト受賞歴",
        "description": "全国新酒鑑評会、Kura Master、IWC、Sake Selection等の主要日本酒コンテストにおける銘柄ごとの年度別受賞実績・受賞ランクを保持するテーブル。"
    },
    "competitions": {
        "jp_name": "コンテスト基本マスタ",
        "description": "主要な日本酒コンペティションの名称、主催者、開催国、設立年、公式サイト、概要を保持するテーブル。"
    },
    "competition_events": {
        "jp_name": "コンテスト開催回・イベント",
        "description": "各コンテストの開催年度、開催日程、会場、出品総数、審査員数、受賞枠数等を年度ごとに管理するテーブル。"
    },
    "users": {
        "jp_name": "ユーザーアカウント",
        "description": "システムへのログインアカウント（システム管理者、酒蔵管理者、一般ユーザー）の認証情報およびロール権限、担当酒蔵を管理するテーブル。"
    },
    "user_profiles": {
        "jp_name": "ユーザープロファイル・嗜好設定",
        "description": "ユーザーごとの味わい嗜好（甘辛、酸味、フルーティ派等）や表示アイコン、AIおすすめ生成用設定を保持するテーブル。"
    },
    "sources": {
        "jp_name": "データ収集元（ソース）",
        "description": "外部データ収集元（公式サイト、公的オープンデータ、特約店サイト等）のURL、取得日時、ライセンス情報を管理するテーブル。"
    },
    "brewery_aliases": {
        "jp_name": "酒蔵別名・旧社名マッピング",
        "description": "酒蔵の旧社名、通称、屋号、表記揺れを正規の酒蔵IDと紐付けるための別名管理テーブル。"
    },
    "merge_candidates": {
        "jp_name": "名寄せ・重複統合候補",
        "description": "データ収集時に検知された重複銘柄や表記揺れを名寄せ（マージ）するための判定・スコア管理テーブル。"
    },
    "sake_bottles": {
        "jp_name": "実写ボトル・ラベルOCR画像",
        "description": "初期の実写ラベル撮影データ、表裏ラベルのクロップ座標、OCR読み取りメタデータを保持するテーブル。"
    }
}

# カラムごとの日本語名・説明辞書
COLUMN_METADATA = {
    "products": {
        "id": ("ID", "製品を一意に識別する主キー (INTEGER)"),
        "spec_name": ("仕様付き商品名", "特定名称やサブネームを含む完全な商品名 (例: 蒼天伝 純米大吟醸 音響加振酒「蒼の音」)"),
        "brewery_name": ("製造酒蔵名", "製造元酒蔵の名称 (例: 株式会社男山本店)"),
        "brand_name": ("銘柄名", "基幹ブランド名 (例: 蒼天伝、八海山、獺祭)"),
        "category": ("特定名称・分類", "特定名称清酒分類 (純米大吟醸酒、純米吟醸酒、特別純米酒、本醸造酒、普通酒、リキュール等)"),
        "ingredients": ("原材料名", "使用原材料の表示 (例: 米（国産）、米麹（国産米）、醸造アルコール)"),
        "polish_ratio": ("精米歩合", "精米歩合のパーセンテージ表記 (例: 40%, 50%, 60%)"),
        "rice_variety": ("原料米・使用米", "使用されている酒造好適米・原料米 (例: 山田錦、雄町、五百万石、蔵の華)"),
        "yeast": ("使用酵母", "仕込みに使用された酵母 (例: 協会9号、宮城酵母、自社酵母)"),
        "alcohol": ("アルコール度数", "アルコール度数の数値 (例: 15.5, 16.0)"),
        "smv": ("日本酒度", "日本酒度の数値・甘辛度合い (例: +3.0, -1.0, 0.0, 非公開)"),
        "acidity": ("酸度", "有機酸の割合・酸度の数値 (例: 1.3, 1.5, 非公開)"),
        "amino_acidity": ("アミノ酸度", "アミノ酸度の数値 (例: 1.1, 1.2, 非公開)"),
        "cropped_image_path_front": ("表ラベル画像パス", "表面ラベルの切り抜き画像URLまたはファイルパス"),
        "cropped_image_path_back": ("裏ラベル画像パス", "裏面一括表示ラベルの切り抜き画像URLまたはファイルパス"),
        "ssi_type": ("SSIタイプ分類", "日本酒サービス研究会・酒匠研究会連合会(SSI)の4タイプ分類 (薫酒・爽酒・醇酒・熟酒)"),
        "body_level": ("味わいの強さ (TOSA縦軸)", "味わいの厚み・強さ (淡麗辛口、中間、濃醇)"),
        "aroma_level": ("香りのバランス (TOSA横軸)", "香りの立ち方・系統 (すっきりおだやか、しっかり個性的、華やかフルーティ)"),
        "comment": ("公式解説・テイスティングコメント", "酒蔵公式の味わい説明やおすすめの飲み方"),
        "status": ("公開ステータス", "データの審査・公開状態 (active, draft, pending)"),
        "confidence": ("データ確信度", "データの信頼性スコア (0.0〜1.0、1.0=公式確認済み)"),
        "source_id": ("情報ソース識別子", "データ取得元の識別ID"),
        "evidence": ("エビデンス・参照元URL", "スペック取得元の公式WebサイトURLや検証根拠"),
        "created_at": ("登録日時", "レコードがデータベースに登録された日時 (ISO8601形式)"),
        "jan_code": ("JANコード", "商品の標準バーコード番号 (13桁/8桁)"),
        "heating_type": ("火入れ種別", "火入れ回数・タイミング (生酒、生貯蔵酒、生詰酒、2回火入れ)"),
        "is_genshu": ("原酒フラグ", "加水調整を行っていない原酒かどうかのフラグ (1: 原酒, 0: 加水酒)"),
        "brewing_method": ("製法特徴", "生酛仕込み、山廃仕込み、無濾過、中取りなどの特殊製法"),
        "serving_temperature": ("おすすめ飲用温度帯", "おすすめの提供温度 (冷酒 5〜10℃、常温 15〜20℃、ぬる燗 40〜45℃ 等)"),
        "prefecture": ("都道府県", "蔵元・製造元の所在都道府県 (例: 宮城県、新潟県)"),
        "water_source": ("仕込み水", "使用されている名水・仕込み水・水質特徴")
    },
    "breweries": {
        "id": ("ID", "酒蔵を一意に識別する主キー (INTEGER)"),
        "corporate_no": ("法人番号", "国税庁指定の13桁の法人番号"),
        "name": ("酒蔵名 (正式名称)", "酒蔵の正式法人名 (例: 株式会社男山本店)"),
        "name_norm": ("正規化酒蔵名", "検索用に正規化された酒蔵名"),
        "kura_name": ("銘柄通称・屋号", "代表銘柄名や屋号通称"),
        "prefecture": ("都道府県", "所在地の都道府県 (例: 宮城県)"),
        "city": ("市区町村", "所在地の市区町村 (例: 気仙沼市)"),
        "address": ("以降の住所", "町名・番地・ビル名"),
        "founded_year": ("創業年 (数値)", "創業した西暦年 (例: 1912)"),
        "founding_year": ("創業年 (元号表記)", "創業年の詳細表記 (例: 1912年 (大正元年))"),
        "website": ("公式サイトURL", "酒蔵の公式ホームページURL"),
        "category": ("業種カテゴリ", "製造業態分類 (sake, shochu, winery)"),
        "description": ("酒蔵紹介文", "酒蔵の歴史や酒造りのこだわりに関する説明文"),
        "description_generated": ("AI生成フラグ", "紹介文がAIによって自動生成されたかどうかのフラグ (1/0)"),
        "status": ("ステータス", "蔵元情報の確認状態 (approved, draft, rejected)"),
        "confidence": ("データ確信度", "酒蔵情報の信頼度スコア"),
        "source_id": ("情報ソースID", "取得元データソース識別子"),
        "evidence": ("エビデンス", "酒蔵情報の取得元・検証記録"),
        "created_at": ("登録日時", "レコード作成日時"),
        "updated_at": ("更新日時", "レコード最終更新日時"),
        "latitude": ("緯度", "酒蔵所在地の緯度座標 (世界測地系 WGS84)"),
        "longitude": ("経度", "酒蔵所在地の経度座標 (世界測地系 WGS84)"),
        "visitation_allowed": ("蔵見学可否", "一般客の蔵見学・酒蔵ツアー受入可否 (1: 可, 0: 不可/要予約)"),
        "shop_available": ("直売所・売店有無", "敷地内の直売所・ショップ併設有無 (1: あり, 0: なし)")
    },
    "brands": {
        "id": ("ID", "銘柄を一意に識別する主キー (INTEGER)"),
        "brewery_id": ("酒蔵ID", "製造元酒蔵のID (`breweries.id` への外部キー)"),
        "name": ("銘柄名", "銘柄の漢字表記 (例: 蒼天伝、八海山、獺祭)"),
        "name_kana": ("銘柄名 (ふりがな)", "銘柄の読みがな表記 (例: そうてんでん、はっかいさん)"),
        "name_en": ("銘柄名 (英字)", "銘柄のローマ字・英語表記 (例: Sotenden, Hakkaisan)"),
        "status": ("ステータス", "公開ステータス (active, draft)"),
        "confidence": ("確信度", "データ信頼度スコア"),
        "source_id": ("情報ソースID", "情報元ソースID"),
        "evidence": ("エビデンス", "銘柄情報の根拠・出典")
    },
    "user_flavor_ratings": {
        "id": ("ID", "評価レコードを一意に識別する主キー (INTEGER)"),
        "product_id": ("製品ID", "評価対象の日本酒製品ID (`products.id` への外部キー)"),
        "user_name": ("ユーザー名", "評価を投稿したユーザーの表示名 (例: hitoshi, nao)"),
        "ssi_type": ("判定SSIタイプ", "ユーザーが体感した4タイプ分類 (薫酒・爽酒・醇酒・熟酒)"),
        "body_level": ("味わいの強さ", "味の濃淡・重さ (淡麗辛口、中間、濃醇)"),
        "aroma_level": ("香りのバランス", "香りの強弱・特徴 (すっきりおだやか、しっかり個性的、華やかフルーティ)"),
        "comment": ("レビューコメント", "ユーザーによる自由記述の味わい感想・ペアリング料理レビュー"),
        "rating_image": ("添付画像1", "ユーザーが投稿した実物写真・ラベル画像パス (メイン)"),
        "rating_image_2": ("添付画像2", "ユーザーが投稿した実物写真・料理写真パス (サブ)"),
        "user_id": ("ユーザーID", "ログインアカウントの識別ID"),
        "created_at": ("投稿日時", "評価が投稿された日時"),
        "total_score": ("総合評価点 (★)", "総合満足度スコア (1.0〜5.0)"),
        "taste_score": ("味わい評点", "味・旨味・キレに対する個別評点 (1.0〜5.0)"),
        "aroma_score": ("香り評点", "吟醸香・香り立ちに対する個別評点 (1.0〜5.0)"),
        "image_accuracy_score": ("画像整合性スコア", "画像と銘柄の一致確信度 (1.0=適合)")
    },
    "awards": {
        "id": ("ID", "受賞歴を一意に識別する主キー (INTEGER)"),
        "competition_id": ("コンテストID", "コンテスト基本ID (`competitions.id` への外部キー)"),
        "year": ("受賞年度", "コンテストの開催年度・受賞西暦年 (例: 2024, 2025)"),
        "category": ("出品部門", "審査部門 (例: 純米大吟醸部門、純米酒部門、スパークリング部門)"),
        "prize": ("受賞ランク", "受賞位 (例: 金賞、最高金賞、プラチナ賞、トロフィー、入賞)"),
        "entry_name": ("出品酒名", "コンテスト出品時の正式銘柄名"),
        "brand_id": ("銘柄ID", "関連する銘柄マスタID"),
        "product_id": ("製品ID", "関連する製品マスタID (`products.id`)"),
        "brewery_id": ("酒蔵ID", "受賞した酒蔵ID (`breweries.id`)"),
        "status": ("ステータス", "確認状態"),
        "confidence": ("確信度", "受賞実績データの信頼度スコア"),
        "source_id": ("情報ソースID", "取得元データソースID"),
        "evidence": ("エビデンス", "公式受賞発表PDFや公式発表ページの出典URL"),
        "competition_name": ("コンテスト名", "コンテストの名称 (例: 全国新酒鑑評会、Kura Master)"),
        "brand_name": ("銘柄名", "受賞した銘柄名"),
        "brewery_name": ("酒蔵名", "受賞した酒蔵名"),
        "is_gold_award": ("金賞以上フラグ", "金賞・最高金賞・トロフィー以上かどうかの判定フラグ (1/0)")
    },
    "competitions": {
        "id": ("ID", "コンテストを一意に識別する主キー (INTEGER)"),
        "name": ("コンテスト名", "コンテストの正式名称 (例: 全国新酒鑑評会、Kura Master、IWC Sake部門)"),
        "country": ("開催国", "主催・審査国 (例: 日本、フランス、イギリス)"),
        "website": ("公式サイトURL", "コンテストの公式WebサイトURL"),
        "founded_year": ("設立年", "第1回が開催された西暦年"),
        "organizer": ("主催団体", "コンテストを運営する団体名 (例: 独立行政法人酒類総合研究所、Kura Master協会)"),
        "description": ("コンテスト概要", "審査基準、特徴、世界的な権威性などの詳細解説")
    },
    "competition_events": {
        "id": ("ID", "開催回を一意に識別する主キー (INTEGER)"),
        "competition_id": ("コンテストID", "対象コンテストID (`competitions.id`)"),
        "year": ("開催年", "開催された西暦年 (例: 2024)"),
        "edition_label": ("開催回表記", "第何回などの表記 (例: 令和5酒造年度、2024年度大会)"),
        "held_start": ("開催開始日", "審査・フェスティバル開始日"),
        "held_end": ("開催終了日", "審査・フェスティバル終了日"),
        "announced_date": ("結果発表日", "受賞酒の公式公表日"),
        "venue": ("会場・都市", "審査会場の都市・施設名 (例: パリ、東京、広島)"),
        "country": ("開催国", "開催国"),
        "entries_total": ("総出品数", "出品された酒の総点数"),
        "countries_count": ("参加国数", "出品・参加国の数"),
        "judges_count": ("審査員数", "審査にあたった専門家・ソムリエの人数"),
        "judges_note": ("審査員構成", "トップソムリエ、蔵元、酒類鑑定官などの審査員内訳"),
        "trophy_count": ("トロフィー数", "最高賞（トロフィー・プレジデント賞）の授与数"),
        "platinum_count": ("プラチナ賞数", "プラチナ賞の選出数"),
        "gold_count": ("金賞数", "金賞の選出数"),
        "website": ("開催回特設URL", "当該年度の結果発表ページURL"),
        "status": ("ステータス", "情報確認ステータス"),
        "confidence": ("確信度", "データの信頼度スコア"),
        "source_id": ("ソースID", "情報元ソースID"),
        "evidence": ("エビデンス", "公式発表資料の参照URL")
    },
    "users": {
        "id": ("ID", "ユーザーを一意に識別する主キー (INTEGER)"),
        "user_id": ("ログインID", "ログイン時に使用する一意なユーザーID (例: hitoshi, nao, admin)"),
        "password": ("パスワード", "アカウントのログインパスワード"),
        "user_name": ("表示名", "画面上に表示されるユーザーの名称"),
        "role": ("ロール権限", "権限ロール (`system_admin`: システム管理者, `brewery_admin`: 酒蔵管理者, `general_user`: 一般利用者)"),
        "assigned_brewery": ("担当酒蔵名", "酒蔵管理者の場合に担当する酒蔵の名称 (システム管理者の場合はNULL)"),
        "created_at": ("アカウント作成日時", "ユーザーが登録された日時")
    },
    "user_profiles": {
        "id": ("ID", "プロファイルを一意に識別する主キー (INTEGER)"),
        "user_name": ("対象ユーザーID", "プロファイルが紐づくユーザー名 (`users.user_id`)"),
        "display_name": ("プロファイル表示名", "画面表示用のニックネーム"),
        "avatar_icon": ("アバターアイコン", "ユーザーアイコンの絵文字や画像識別子 (例: 🍶, 🌸)"),
        "preference_text": ("嗜好プロファイル", "好みの酒質・味わい傾向 (AIおすすめ生成時に参照される特徴テキスト)"),
        "writing_style": ("コメント文体", "AIアシスト時のトーン＆マナー設定"),
        "is_primary": ("メインアカウントフラグ", "デフォルトのメインユーザーかどうかのフラグ (1/0)"),
        "created_at": ("作成日時", "プロファイル作成日時")
    },
    "sources": {
        "id": ("ソースID", "情報源を一意に識別するテキストID (主キー)"),
        "name": ("ソース名称", "データ取得元の名称 (例: 国税庁酒類製造者データ、SAKETIMES等)"),
        "url": ("取得元URL", "公式データまたはWebサイトのトップURL"),
        "fetched_at": ("データ取得日時", "クローリングまたはインポートを実施した日時"),
        "raw_path": ("元データファイルパス", "取得した元ファイル（JSON/CSV/PDF）のローカル保存パス"),
        "license_note": ("ライセンス・利用規約", "公的オープンデータ利用規約や出典明記ルール")
    },
    "brewery_aliases": {
        "id": ("ID", "別名レコードを一意に識別する主キー (INTEGER)"),
        "brewery_id": ("酒蔵ID", "正規の酒蔵マスタID (`breweries.id`)"),
        "alias": ("別名・通称", "表記揺れ、旧社名、銘柄通称など (例: 旭酒造株式会社 -> 獺祭蔵)"),
        "alias_type": ("別名タイプ", "別名の種別 (old_name: 旧社名, brand_alias: 銘柄通称, typo: 表記揺れ)"),
        "source_id": ("情報ソースID", "別名情報の取得元ソースID")
    },
    "merge_candidates": {
        "id": ("ID", "名寄せレコードを一意に識別する主キー (INTEGER)"),
        "entity": ("対象エンティティ", "名寄せ対象の種別 (`brewery`: 酒蔵, `brand`: 銘柄, `product`: 製品)"),
        "keep_id": ("存続側ID", "統合先として残す正規レコードのID"),
        "merge_id": ("統合側ID", "統合されて非推奨・アーカイブとなる重複レコードのID"),
        "reason": ("名寄せ理由", "重複と判定されたアルゴリズムまたはルール根拠"),
        "score": ("類似度スコア", "文字列類似度・住所一致スコア (0.0〜1.0)"),
        "decided": ("確定状態", "名寄せが承認・実行されたかのフラグ (`approved`, `pending`, `rejected`)")
    },
    "sake_bottles": {
        "id": ("ID", "ボトル撮影レコードを一意に識別する主キー (INTEGER)"),
        "name": ("銘柄名", "ラベル記載の銘柄名"),
        "sub_name": ("特定名称・仕様", "特定名称やサブタイトル表記"),
        "brewery": ("酒蔵名", "ラベル記載の製造元酒蔵名"),
        "sake_type": ("特定名称", "清酒分類 (純米大吟醸、純米吟醸等)"),
        "alcohol_content": ("アルコール度数", "ラベル記載のアルコール度数数値"),
        "raw_materials": ("原材料名", "ラベル記載の原材料表記"),
        "polishing_rate": ("精米歩合", "ラベル記載の精米歩合表記"),
        "volume": ("容量", "ボトルの内容量表記 (例: 720ml, 1800ml)"),
        "brewery_address": ("蔵元住所", "ラベルに印刷されている製造者所在地"),
        "manufactured_date": ("製造年月", "ラベル印字の製造年月 (例: 2024.04)"),
        "original_image_path_front": ("表元画像パス", "撮影された未トリミングの表側写真パス"),
        "original_image_path_back": ("裏元画像パス", "撮影された未トリミングの裏側写真パス"),
        "cropped_image_path_front": ("表クロップ画像パス", "トリミング加工後の表面ラベル画像パス"),
        "cropped_image_path_back": ("裏クロップ画像パス", "トリミング加工後の裏面ラベル画像パス"),
        "created_at": ("登録日時", "撮影データ登録日時")
    }
}

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ データベースが見つかりません: {DB_PATH}")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"📁 バックアップ出力先ディレクトリ: {BACKUP_DIR}\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. ユーザーテーブル一覧を取得
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]

    exported_summary = []

    # 2. 各テーブルを個別のCSVファイルへ出力 (UTF-8 with BOM for Excel compatibility)
    for table_name in tables:
        csv_path = os.path.join(BACKUP_DIR, f"{table_name}.csv")
        
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        col_names = [description[0] for description in cur.description]
        
        with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(col_names)
            for row in rows:
                writer.writerow(list(row))
                
        row_count = len(rows)
        exported_summary.append((table_name, row_count, csv_path))
        print(f"  ✅ [CSVエクスポート] {table_name}.csv ({row_count} 件)")

    # 3. マークダウン形式の定義書 (database_schema.md) を生成
    md_path = os.path.join(BACKUP_DIR, "database_schema.md")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_lines = []
    md_lines.append("# 🍶 日本酒データベース (Sake Database) テーブル定義・項目説明書")
    md_lines.append("")
    md_lines.append(f"- **バックアップ出力日時**: `{now_str}`")
    md_lines.append(f"- **データベースファイル**: `database/sake_database.db` (SQLite3)")
    md_lines.append(f"- **出力先ディレクトリ**: `database-backup/`")
    md_lines.append(f"- **テーブル総数**: **{len(tables)} テーブル**")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 1. テーブル一覧概要 (Table Overview)")
    md_lines.append("")
    md_lines.append("| No | テーブル名 (Table Name) | 日本語名称 | レコード件数 | CSVファイル名 | 概要・役割 |")
    md_lines.append("|:---:|:---|:---|:---:|:---|:---|")

    for idx, (t_name, count, _) in enumerate(exported_summary, start=1):
        meta = TABLE_METADATA.get(t_name, {"jp_name": t_name, "description": "-"})
        md_lines.append(f"| {idx} | **`{t_name}`** | {meta['jp_name']} | **{count:,}** 件 | [`{t_name}.csv`](./{t_name}.csv) | {meta['description']} |")

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 2. 各テーブルの項目定義と項目説明 (Detailed Schema & Columns)")
    md_lines.append("")

    for t_name in tables:
        meta = TABLE_METADATA.get(t_name, {"jp_name": t_name, "description": "-"})
        cur.execute(f"PRAGMA table_info({t_name})")
        columns_info = cur.fetchall()
        cur.execute(f"SELECT COUNT(*) FROM {t_name}")
        t_count = cur.fetchone()[0]

        md_lines.append(f"### 📋 `{t_name}` ({meta['jp_name']})")
        md_lines.append("")
        md_lines.append(f"- **概要**: {meta['description']}")
        md_lines.append(f"- **レコード件数**: **{t_count:,}** 件")
        md_lines.append(f"- **対応CSV**: [`{t_name}.csv`](./{t_name}.csv)")
        md_lines.append("")
        md_lines.append("| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |")
        md_lines.append("|:---|:---:|:---:|:---|:---|")

        t_col_meta = COLUMN_METADATA.get(t_name, {})

        for col in columns_info:
            cid, cname, ctype, notnull, dflt_value, pk = col
            
            # 制約表示
            constraints = []
            if pk == 1:
                constraints.append("**PRIMARY KEY**")
            elif notnull == 1:
                constraints.append("NOT NULL")
            else:
                constraints.append("NULL可")
                
            if dflt_value is not None:
                constraints.append(f"DEFAULT {dflt_value}")
                
            const_str = "<br>".join(constraints)

            jp_title, jp_desc = t_col_meta.get(cname, (cname, "-"))
            
            md_lines.append(f"| **`{cname}`** | `{ctype}` | {const_str} | {jp_title} | {jp_desc} |")

        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    with open(md_path, mode='w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))

    print(f"\n  📄 [MD定義書生成] database_schema.md を作成しました。")
    print(f"\n==========================================")
    print(f"✨ データベース全 {len(tables)} テーブルのCSV出力＆定義書作成が完了しました！")
    print(f"==========================================")

    conn.close()

if __name__ == '__main__':
    main()
