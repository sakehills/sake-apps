# 🍶 日本酒データベース (Sake Database) テーブル定義・項目説明書

- **バックアップ出力日時**: `2026-08-29 09:23:22`
- **データベースファイル**: `database/sake_database.db` (SQLite3)
- **出力先ディレクトリ**: `database-backup/`
- **テーブル総数**: **13 テーブル**

---

## 1. テーブル一覧概要 (Table Overview)

| No | テーブル名 (Table Name) | 日本語名称 | レコード件数 | CSVファイル名 | 概要・役割 |
|:---:|:---|:---|:---:|:---|:---|
| 1 | **`awards`** | コンテスト受賞歴 | **2,721** 件 | [`awards.csv`](./awards.csv) | 全国新酒鑑評会、Kura Master、IWC、Sake Selection等の主要日本酒コンテストにおける銘柄ごとの年度別受賞実績・受賞ランクを保持するテーブル。 |
| 2 | **`brands`** | 銘柄・ブランドマスタ | **10,097** 件 | [`brands.csv`](./brands.csv) | 酒蔵に紐づく代表銘柄・ブランド名（漢字、ふりがな、英字表記）を管理するマスタテーブル。 |
| 3 | **`breweries`** | 酒蔵・蔵元マスタ | **1,629** 件 | [`breweries.csv`](./breweries.csv) | 日本全国の日本酒製造業者・酒蔵情報（法人番号、所在地、緯度経度、創業年、公式サイト、見学可否、直売所有無等）を保持するマスタテーブル。 |
| 4 | **`brewery_aliases`** | 酒蔵別名・旧社名マッピング | **3** 件 | [`brewery_aliases.csv`](./brewery_aliases.csv) | 酒蔵の旧社名、通称、屋号、表記揺れを正規の酒蔵IDと紐付けるための別名管理テーブル。 |
| 5 | **`competition_events`** | コンテスト開催回・イベント | **43** 件 | [`competition_events.csv`](./competition_events.csv) | 各コンテストの開催年度、開催日程、会場、出品総数、審査員数、受賞枠数等を年度ごとに管理するテーブル。 |
| 6 | **`competitions`** | コンテスト基本マスタ | **23** 件 | [`competitions.csv`](./competitions.csv) | 主要な日本酒コンペティションの名称、主催者、開催国、設立年、公式サイト、概要を保持するテーブル。 |
| 7 | **`merge_candidates`** | 名寄せ・重複統合候補 | **31** 件 | [`merge_candidates.csv`](./merge_candidates.csv) | データ収集時に検知された重複銘柄や表記揺れを名寄せ（マージ）するための判定・スコア管理テーブル。 |
| 8 | **`products`** | 日本酒製品・スペック | **14,405** 件 | [`products.csv`](./products.csv) | 日本酒の個別商品・製品スペック情報（特定名称、原料米、精米歩合、度数、日本酒度、酸度、SSI分類、ラベル画像、公式エビデンス等）を保持するメインテーブル。 |
| 9 | **`sake_bottles`** | 実写ボトル・ラベルOCR画像 | **6** 件 | [`sake_bottles.csv`](./sake_bottles.csv) | 初期の実写ラベル撮影データ、表裏ラベルのクロップ座標、OCR読み取りメタデータを保持するテーブル。 |
| 10 | **`sources`** | データ収集元（ソース） | **73** 件 | [`sources.csv`](./sources.csv) | 外部データ収集元（公式サイト、公的オープンデータ、特約店サイト等）のURL、取得日時、ライセンス情報を管理するテーブル。 |
| 11 | **`user_flavor_ratings`** | ユーザー評価・レビュー | **8,289** 件 | [`user_flavor_ratings.csv`](./user_flavor_ratings.csv) | 一般ユーザーおよびテイスターによる評価スコア（総合点・味わい点・香り点）、自由記述コメント、味わいチャート（SSI・TOSA方式）、投稿写真等を保持するテーブル。 |
| 12 | **`user_profiles`** | ユーザープロファイル・嗜好設定 | **2** 件 | [`user_profiles.csv`](./user_profiles.csv) | ユーザーごとの味わい嗜好（甘辛、酸味、フルーティ派等）や表示アイコン、AIおすすめ生成用設定を保持するテーブル。 |
| 13 | **`users`** | ユーザーアカウント | **8** 件 | [`users.csv`](./users.csv) | システムへのログインアカウント（システム管理者、酒蔵管理者、一般ユーザー）の認証情報およびロール権限、担当酒蔵を管理するテーブル。 |

---

## 2. 各テーブルの項目定義と項目説明 (Detailed Schema & Columns)

### 📋 `awards` (コンテスト受賞歴)

- **概要**: 全国新酒鑑評会、Kura Master、IWC、Sake Selection等の主要日本酒コンテストにおける銘柄ごとの年度別受賞実績・受賞ランクを保持するテーブル。
- **レコード件数**: **2,721** 件
- **対応CSV**: [`awards.csv`](./awards.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 受賞歴を一意に識別する主キー (INTEGER) |
| **`competition_id`** | `INTEGER` | NOT NULL | コンテストID | コンテスト基本ID (`competitions.id` への外部キー) |
| **`year`** | `INTEGER` | NOT NULL | 受賞年度 | コンテストの開催年度・受賞西暦年 (例: 2024, 2025) |
| **`category`** | `TEXT` | NULL可 | 出品部門 | 審査部門 (例: 純米大吟醸部門、純米酒部門、スパークリング部門) |
| **`prize`** | `TEXT` | NOT NULL | 受賞ランク | 受賞位 (例: 金賞、最高金賞、プラチナ賞、トロフィー、入賞) |
| **`entry_name`** | `TEXT` | NOT NULL | 出品酒名 | コンテスト出品時の正式銘柄名 |
| **`brand_id`** | `INTEGER` | NULL可 | 銘柄ID | 関連する銘柄マスタID |
| **`product_id`** | `INTEGER` | NULL可 | 製品ID | 関連する製品マスタID (`products.id`) |
| **`brewery_id`** | `INTEGER` | NULL可 | 酒蔵ID | 受賞した酒蔵ID (`breweries.id`) |
| **`status`** | `TEXT` | NULL可<br>DEFAULT 'draft' | ステータス | 確認状態 |
| **`confidence`** | `REAL` | NULL可<br>DEFAULT 0.0 | 確信度 | 受賞実績データの信頼度スコア |
| **`source_id`** | `TEXT` | NULL可 | 情報ソースID | 取得元データソースID |
| **`evidence`** | `TEXT` | NULL可 | エビデンス | 公式受賞発表PDFや公式発表ページの出典URL |
| **`competition_name`** | `TEXT` | NULL可 | コンテスト名 | コンテストの名称 (例: 全国新酒鑑評会、Kura Master) |
| **`brand_name`** | `TEXT` | NULL可 | 銘柄名 | 受賞した銘柄名 |
| **`brewery_name`** | `TEXT` | NULL可 | 酒蔵名 | 受賞した酒蔵名 |
| **`is_gold_award`** | `INTEGER` | NULL可<br>DEFAULT 0 | 金賞以上フラグ | 金賞・最高金賞・トロフィー以上かどうかの判定フラグ (1/0) |

---

### 📋 `brands` (銘柄・ブランドマスタ)

- **概要**: 酒蔵に紐づく代表銘柄・ブランド名（漢字、ふりがな、英字表記）を管理するマスタテーブル。
- **レコード件数**: **10,097** 件
- **対応CSV**: [`brands.csv`](./brands.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 銘柄を一意に識別する主キー (INTEGER) |
| **`brewery_id`** | `INTEGER` | NULL可 | 酒蔵ID | 製造元酒蔵のID (`breweries.id` への外部キー) |
| **`name`** | `TEXT` | NOT NULL | 銘柄名 | 銘柄の漢字表記 (例: 蒼天伝、八海山、獺祭) |
| **`name_kana`** | `TEXT` | NULL可 | 銘柄名 (ふりがな) | 銘柄の読みがな表記 (例: そうてんでん、はっかいさん) |
| **`name_en`** | `TEXT` | NULL可 | 銘柄名 (英字) | 銘柄のローマ字・英語表記 (例: Sotenden, Hakkaisan) |
| **`status`** | `TEXT` | NULL可<br>DEFAULT 'draft' | ステータス | 公開ステータス (active, draft) |
| **`confidence`** | `REAL` | NULL可<br>DEFAULT 0.0 | 確信度 | データ信頼度スコア |
| **`source_id`** | `TEXT` | NULL可 | 情報ソースID | 情報元ソースID |
| **`evidence`** | `TEXT` | NULL可 | エビデンス | 銘柄情報の根拠・出典 |

---

### 📋 `breweries` (酒蔵・蔵元マスタ)

- **概要**: 日本全国の日本酒製造業者・酒蔵情報（法人番号、所在地、緯度経度、創業年、公式サイト、見学可否、直売所有無等）を保持するマスタテーブル。
- **レコード件数**: **1,629** 件
- **対応CSV**: [`breweries.csv`](./breweries.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 酒蔵を一意に識別する主キー (INTEGER) |
| **`corporate_no`** | `TEXT` | NULL可 | 法人番号 | 国税庁指定の13桁の法人番号 |
| **`name`** | `TEXT` | NOT NULL | 酒蔵名 (正式名称) | 酒蔵の正式法人名 (例: 株式会社男山本店) |
| **`name_norm`** | `TEXT` | NOT NULL | 正規化酒蔵名 | 検索用に正規化された酒蔵名 |
| **`kura_name`** | `TEXT` | NULL可 | 銘柄通称・屋号 | 代表銘柄名や屋号通称 |
| **`prefecture`** | `TEXT` | NOT NULL | 都道府県 | 所在地の都道府県 (例: 宮城県) |
| **`city`** | `TEXT` | NULL可 | 市区町村 | 所在地の市区町村 (例: 気仙沼市) |
| **`address`** | `TEXT` | NULL可 | 以降の住所 | 町名・番地・ビル名 |
| **`founded_year`** | `INTEGER` | NULL可 | 創業年 (数値) | 創業した西暦年 (例: 1912) |
| **`website`** | `TEXT` | NULL可 | 公式サイトURL | 酒蔵の公式ホームページURL |
| **`category`** | `TEXT` | NULL可<br>DEFAULT 'sake' | 業種カテゴリ | 製造業態分類 (sake, shochu, winery) |
| **`description`** | `TEXT` | NULL可 | 酒蔵紹介文 | 酒蔵の歴史や酒造りのこだわりに関する説明文 |
| **`description_generated`** | `INTEGER` | NULL可<br>DEFAULT 0 | AI生成フラグ | 紹介文がAIによって自動生成されたかどうかのフラグ (1/0) |
| **`status`** | `TEXT` | NULL可<br>DEFAULT 'draft' | ステータス | 蔵元情報の確認状態 (approved, draft, rejected) |
| **`confidence`** | `REAL` | NULL可<br>DEFAULT 0.0 | データ確信度 | 酒蔵情報の信頼度スコア |
| **`source_id`** | `TEXT` | NULL可 | 情報ソースID | 取得元データソース識別子 |
| **`evidence`** | `TEXT` | NULL可 | エビデンス | 酒蔵情報の取得元・検証記録 |
| **`created_at`** | `TEXT` | NULL可 | 登録日時 | レコード作成日時 |
| **`updated_at`** | `TEXT` | NULL可 | 更新日時 | レコード最終更新日時 |
| **`latitude`** | `REAL` | NULL可 | 緯度 | 酒蔵所在地の緯度座標 (世界測地系 WGS84) |
| **`longitude`** | `REAL` | NULL可 | 経度 | 酒蔵所在地の経度座標 (世界測地系 WGS84) |
| **`founding_year`** | `TEXT` | NULL可 | 創業年 (元号表記) | 創業年の詳細表記 (例: 1912年 (大正元年)) |
| **`visitation_allowed`** | `INTEGER` | NULL可<br>DEFAULT 0 | 蔵見学可否 | 一般客の蔵見学・酒蔵ツアー受入可否 (1: 可, 0: 不可/要予約) |
| **`shop_available`** | `INTEGER` | NULL可<br>DEFAULT 0 | 直売所・売店有無 | 敷地内の直売所・ショップ併設有無 (1: あり, 0: なし) |

---

### 📋 `brewery_aliases` (酒蔵別名・旧社名マッピング)

- **概要**: 酒蔵の旧社名、通称、屋号、表記揺れを正規の酒蔵IDと紐付けるための別名管理テーブル。
- **レコード件数**: **3** 件
- **対応CSV**: [`brewery_aliases.csv`](./brewery_aliases.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 別名レコードを一意に識別する主キー (INTEGER) |
| **`brewery_id`** | `INTEGER` | NOT NULL | 酒蔵ID | 正規の酒蔵マスタID (`breweries.id`) |
| **`alias`** | `TEXT` | NOT NULL | 別名・通称 | 表記揺れ、旧社名、銘柄通称など (例: 旭酒造株式会社 -> 獺祭蔵) |
| **`alias_type`** | `TEXT` | NULL可 | 別名タイプ | 別名の種別 (old_name: 旧社名, brand_alias: 銘柄通称, typo: 表記揺れ) |
| **`source_id`** | `TEXT` | NULL可 | 情報ソースID | 別名情報の取得元ソースID |

---

### 📋 `competition_events` (コンテスト開催回・イベント)

- **概要**: 各コンテストの開催年度、開催日程、会場、出品総数、審査員数、受賞枠数等を年度ごとに管理するテーブル。
- **レコード件数**: **43** 件
- **対応CSV**: [`competition_events.csv`](./competition_events.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 開催回を一意に識別する主キー (INTEGER) |
| **`competition_id`** | `INTEGER` | NOT NULL | コンテストID | 対象コンテストID (`competitions.id`) |
| **`year`** | `INTEGER` | NOT NULL | 開催年 | 開催された西暦年 (例: 2024) |
| **`edition_label`** | `TEXT` | NULL可 | 開催回表記 | 第何回などの表記 (例: 令和5酒造年度、2024年度大会) |
| **`held_start`** | `TEXT` | NULL可 | 開催開始日 | 審査・フェスティバル開始日 |
| **`held_end`** | `TEXT` | NULL可 | 開催終了日 | 審査・フェスティバル終了日 |
| **`announced_date`** | `TEXT` | NULL可 | 結果発表日 | 受賞酒の公式公表日 |
| **`venue`** | `TEXT` | NULL可 | 会場・都市 | 審査会場の都市・施設名 (例: パリ、東京、広島) |
| **`country`** | `TEXT` | NULL可 | 開催国 | 開催国 |
| **`entries_total`** | `INTEGER` | NULL可 | 総出品数 | 出品された酒の総点数 |
| **`countries_count`** | `INTEGER` | NULL可 | 参加国数 | 出品・参加国の数 |
| **`judges_count`** | `INTEGER` | NULL可 | 審査員数 | 審査にあたった専門家・ソムリエの人数 |
| **`judges_note`** | `TEXT` | NULL可 | 審査員構成 | トップソムリエ、蔵元、酒類鑑定官などの審査員内訳 |
| **`trophy_count`** | `INTEGER` | NULL可 | トロフィー数 | 最高賞（トロフィー・プレジデント賞）の授与数 |
| **`platinum_count`** | `INTEGER` | NULL可 | プラチナ賞数 | プラチナ賞の選出数 |
| **`gold_count`** | `INTEGER` | NULL可 | 金賞数 | 金賞の選出数 |
| **`website`** | `TEXT` | NULL可 | 開催回特設URL | 当該年度の結果発表ページURL |
| **`status`** | `TEXT` | NULL可<br>DEFAULT 'draft' | ステータス | 情報確認ステータス |
| **`confidence`** | `REAL` | NULL可<br>DEFAULT 0.0 | 確信度 | データの信頼度スコア |
| **`source_id`** | `TEXT` | NULL可 | ソースID | 情報元ソースID |
| **`evidence`** | `TEXT` | NULL可 | エビデンス | 公式発表資料の参照URL |

---

### 📋 `competitions` (コンテスト基本マスタ)

- **概要**: 主要な日本酒コンペティションの名称、主催者、開催国、設立年、公式サイト、概要を保持するテーブル。
- **レコード件数**: **23** 件
- **対応CSV**: [`competitions.csv`](./competitions.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | コンテストを一意に識別する主キー (INTEGER) |
| **`name`** | `TEXT` | NOT NULL | コンテスト名 | コンテストの正式名称 (例: 全国新酒鑑評会、Kura Master、IWC Sake部門) |
| **`country`** | `TEXT` | NULL可 | 開催国 | 主催・審査国 (例: 日本、フランス、イギリス) |
| **`website`** | `TEXT` | NULL可 | 公式サイトURL | コンテストの公式WebサイトURL |
| **`founded_year`** | `INTEGER` | NULL可 | 設立年 | 第1回が開催された西暦年 |
| **`organizer`** | `TEXT` | NULL可 | 主催団体 | コンテストを運営する団体名 (例: 独立行政法人酒類総合研究所、Kura Master協会) |
| **`description`** | `TEXT` | NULL可 | コンテスト概要 | 審査基準、特徴、世界的な権威性などの詳細解説 |

---

### 📋 `merge_candidates` (名寄せ・重複統合候補)

- **概要**: データ収集時に検知された重複銘柄や表記揺れを名寄せ（マージ）するための判定・スコア管理テーブル。
- **レコード件数**: **31** 件
- **対応CSV**: [`merge_candidates.csv`](./merge_candidates.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 名寄せレコードを一意に識別する主キー (INTEGER) |
| **`entity`** | `TEXT` | NOT NULL | 対象エンティティ | 名寄せ対象の種別 (`brewery`: 酒蔵, `brand`: 銘柄, `product`: 製品) |
| **`keep_id`** | `INTEGER` | NOT NULL | 存続側ID | 統合先として残す正規レコードのID |
| **`merge_id`** | `INTEGER` | NOT NULL | 統合側ID | 統合されて非推奨・アーカイブとなる重複レコードのID |
| **`reason`** | `TEXT` | NULL可 | 名寄せ理由 | 重複と判定されたアルゴリズムまたはルール根拠 |
| **`score`** | `REAL` | NULL可 | 類似度スコア | 文字列類似度・住所一致スコア (0.0〜1.0) |
| **`decided`** | `TEXT` | NULL可 | 確定状態 | 名寄せが承認・実行されたかのフラグ (`approved`, `pending`, `rejected`) |

---

### 📋 `products` (日本酒製品・スペック)

- **概要**: 日本酒の個別商品・製品スペック情報（特定名称、原料米、精米歩合、度数、日本酒度、酸度、SSI分類、ラベル画像、公式エビデンス等）を保持するメインテーブル。
- **レコード件数**: **14,405** 件
- **対応CSV**: [`products.csv`](./products.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 製品を一意に識別する主キー (INTEGER) |
| **`spec_name`** | `TEXT` | NOT NULL | 仕様付き商品名 | 特定名称やサブネームを含む完全な商品名 (例: 蒼天伝 純米大吟醸 音響加振酒「蒼の音」) |
| **`brewery_name`** | `TEXT` | NOT NULL | 製造酒蔵名 | 製造元酒蔵の名称 (例: 株式会社男山本店) |
| **`brand_name`** | `TEXT` | NOT NULL | 銘柄名 | 基幹ブランド名 (例: 蒼天伝、八海山、獺祭) |
| **`category`** | `TEXT` | NULL可 | 特定名称・分類 | 特定名称清酒分類 (純米大吟醸酒、純米吟醸酒、特別純米酒、本醸造酒、普通酒、リキュール等) |
| **`ingredients`** | `TEXT` | NULL可 | 原材料名 | 使用原材料の表示 (例: 米（国産）、米麹（国産米）、醸造アルコール) |
| **`polish_ratio`** | `TEXT` | NULL可 | 精米歩合 | 精米歩合のパーセンテージ表記 (例: 40%, 50%, 60%) |
| **`rice_variety`** | `TEXT` | NULL可 | 原料米・使用米 | 使用されている酒造好適米・原料米 (例: 山田錦、雄町、五百万石、蔵の華) |
| **`yeast`** | `TEXT` | NULL可 | 使用酵母 | 仕込みに使用された酵母 (例: 協会9号、宮城酵母、自社酵母) |
| **`alcohol`** | `REAL` | NULL可 | アルコール度数 | アルコール度数の数値 (例: 15.5, 16.0) |
| **`smv`** | `TEXT` | NULL可 | 日本酒度 | 日本酒度の数値・甘辛度合い (例: +3.0, -1.0, 0.0, 非公開) |
| **`acidity`** | `TEXT` | NULL可 | 酸度 | 有機酸の割合・酸度の数値 (例: 1.3, 1.5, 非公開) |
| **`amino_acidity`** | `TEXT` | NULL可 | アミノ酸度 | アミノ酸度の数値 (例: 1.1, 1.2, 非公開) |
| **`cropped_image_path_front`** | `TEXT` | NULL可 | 表ラベル画像パス | 表面ラベルの切り抜き画像URLまたはファイルパス |
| **`cropped_image_path_back`** | `TEXT` | NULL可 | 裏ラベル画像パス | 裏面一括表示ラベルの切り抜き画像URLまたはファイルパス |
| **`ssi_type`** | `TEXT` | NULL可 | SSIタイプ分類 | 日本酒サービス研究会・酒匠研究会連合会(SSI)の4タイプ分類 (薫酒・爽酒・醇酒・熟酒) |
| **`body_level`** | `TEXT` | NULL可 | 味わいの強さ (TOSA縦軸) | 味わいの厚み・強さ (淡麗辛口、中間、濃醇) |
| **`aroma_level`** | `TEXT` | NULL可 | 香りのバランス (TOSA横軸) | 香りの立ち方・系統 (すっきりおだやか、しっかり個性的、華やかフルーティ) |
| **`comment`** | `TEXT` | NULL可 | 公式解説・テイスティングコメント | 酒蔵公式の味わい説明やおすすめの飲み方 |
| **`status`** | `TEXT` | NULL可<br>DEFAULT 'draft' | 公開ステータス | データの審査・公開状態 (active, draft, pending) |
| **`confidence`** | `REAL` | NULL可<br>DEFAULT 0.9 | データ確信度 | データの信頼性スコア (0.0〜1.0、1.0=公式確認済み) |
| **`source_id`** | `TEXT` | NULL可 | 情報ソース識別子 | データ取得元の識別ID |
| **`evidence`** | `TEXT` | NULL可 | エビデンス・参照元URL | スペック取得元の公式WebサイトURLや検証根拠 |
| **`created_at`** | `TEXT` | NULL可 | 登録日時 | レコードがデータベースに登録された日時 (ISO8601形式) |
| **`jan_code`** | `TEXT` | NULL可 | JANコード | 商品の標準バーコード番号 (13桁/8桁) |
| **`heating_type`** | `TEXT` | NULL可 | 火入れ種別 | 火入れ回数・タイミング (生酒、生貯蔵酒、生詰酒、2回火入れ) |
| **`is_genshu`** | `INTEGER` | NULL可 | 原酒フラグ | 加水調整を行っていない原酒かどうかのフラグ (1: 原酒, 0: 加水酒) |
| **`brewing_method`** | `TEXT` | NULL可 | 製法特徴 | 生酛仕込み、山廃仕込み、無濾過、中取りなどの特殊製法 |
| **`serving_temperature`** | `TEXT` | NULL可 | おすすめ飲用温度帯 | おすすめの提供温度 (冷酒 5〜10℃、常温 15〜20℃、ぬる燗 40〜45℃ 等) |
| **`prefecture`** | `TEXT` | NULL可 | 都道府県 | 蔵元・製造元の所在都道府県 (例: 宮城県、新潟県) |
| **`water_source`** | `TEXT` | NULL可 | 仕込み水 | 使用されている名水・仕込み水・水質特徴 |
| **`taste_profile`** | `TEXT` | NULL可 | taste_profile | - |
| **`aroma_notes`** | `TEXT` | NULL可 | aroma_notes | - |
| **`product_description`** | `TEXT` | NULL可 | product_description | - |
| **`celebration_scenes`** | `TEXT` | NULL可 | celebration_scenes | - |
| **`brand_story`** | `TEXT` | NULL可 | brand_story | - |
| **`gift_packaging`** | `TEXT` | NULL可 | gift_packaging | - |
| **`celebration_phrase`** | `TEXT` | NULL可 | celebration_phrase | - |

---

### 📋 `sake_bottles` (実写ボトル・ラベルOCR画像)

- **概要**: 初期の実写ラベル撮影データ、表裏ラベルのクロップ座標、OCR読み取りメタデータを保持するテーブル。
- **レコード件数**: **6** 件
- **対応CSV**: [`sake_bottles.csv`](./sake_bottles.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | ボトル撮影レコードを一意に識別する主キー (INTEGER) |
| **`name`** | `TEXT` | NOT NULL | 銘柄名 | ラベル記載の銘柄名 |
| **`sub_name`** | `TEXT` | NULL可 | 特定名称・仕様 | 特定名称やサブタイトル表記 |
| **`brewery`** | `TEXT` | NULL可 | 酒蔵名 | ラベル記載の製造元酒蔵名 |
| **`sake_type`** | `TEXT` | NULL可 | 特定名称 | 清酒分類 (純米大吟醸、純米吟醸等) |
| **`alcohol_content`** | `REAL` | NULL可 | アルコール度数 | ラベル記載のアルコール度数数値 |
| **`raw_materials`** | `TEXT` | NULL可 | 原材料名 | ラベル記載の原材料表記 |
| **`polishing_rate`** | `TEXT` | NULL可 | 精米歩合 | ラベル記載の精米歩合表記 |
| **`volume`** | `TEXT` | NULL可 | 容量 | ボトルの内容量表記 (例: 720ml, 1800ml) |
| **`brewery_address`** | `TEXT` | NULL可 | 蔵元住所 | ラベルに印刷されている製造者所在地 |
| **`manufactured_date`** | `TEXT` | NULL可 | 製造年月 | ラベル印字の製造年月 (例: 2024.04) |
| **`original_image_path_front`** | `TEXT` | NULL可 | 表元画像パス | 撮影された未トリミングの表側写真パス |
| **`original_image_path_back`** | `TEXT` | NULL可 | 裏元画像パス | 撮影された未トリミングの裏側写真パス |
| **`cropped_image_path_front`** | `TEXT` | NULL可 | 表クロップ画像パス | トリミング加工後の表面ラベル画像パス |
| **`cropped_image_path_back`** | `TEXT` | NULL可 | 裏クロップ画像パス | トリミング加工後の裏面ラベル画像パス |
| **`created_at`** | `TEXT` | NULL可 | 登録日時 | 撮影データ登録日時 |

---

### 📋 `sources` (データ収集元（ソース）)

- **概要**: 外部データ収集元（公式サイト、公的オープンデータ、特約店サイト等）のURL、取得日時、ライセンス情報を管理するテーブル。
- **レコード件数**: **73** 件
- **対応CSV**: [`sources.csv`](./sources.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `TEXT` | **PRIMARY KEY** | ソースID | 情報源を一意に識別するテキストID (主キー) |
| **`name`** | `TEXT` | NOT NULL | ソース名称 | データ取得元の名称 (例: 国税庁酒類製造者データ、SAKETIMES等) |
| **`url`** | `TEXT` | NULL可 | 取得元URL | 公式データまたはWebサイトのトップURL |
| **`fetched_at`** | `TEXT` | NULL可 | データ取得日時 | クローリングまたはインポートを実施した日時 |
| **`raw_path`** | `TEXT` | NULL可 | 元データファイルパス | 取得した元ファイル（JSON/CSV/PDF）のローカル保存パス |
| **`license_note`** | `TEXT` | NULL可 | ライセンス・利用規約 | 公的オープンデータ利用規約や出典明記ルール |

---

### 📋 `user_flavor_ratings` (ユーザー評価・レビュー)

- **概要**: 一般ユーザーおよびテイスターによる評価スコア（総合点・味わい点・香り点）、自由記述コメント、味わいチャート（SSI・TOSA方式）、投稿写真等を保持するテーブル。
- **レコード件数**: **8,289** 件
- **対応CSV**: [`user_flavor_ratings.csv`](./user_flavor_ratings.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | 評価レコードを一意に識別する主キー (INTEGER) |
| **`product_id`** | `INTEGER` | NOT NULL | 製品ID | 評価対象の日本酒製品ID (`products.id` への外部キー) |
| **`user_name`** | `TEXT` | NULL可<br>DEFAULT '匿名' | ユーザー名 | 評価を投稿したユーザーの表示名 (例: hitoshi, nao) |
| **`ssi_type`** | `TEXT` | NULL可 | 判定SSIタイプ | ユーザーが体感した4タイプ分類 (薫酒・爽酒・醇酒・熟酒) |
| **`body_level`** | `TEXT` | NULL可 | 味わいの強さ | 味の濃淡・重さ (淡麗辛口、中間、濃醇) |
| **`aroma_level`** | `TEXT` | NULL可 | 香りのバランス | 香りの強弱・特徴 (すっきりおだやか、しっかり個性的、華やかフルーティ) |
| **`comment`** | `TEXT` | NULL可 | レビューコメント | ユーザーによる自由記述の味わい感想・ペアリング料理レビュー |
| **`rating_image`** | `TEXT` | NULL可 | 添付画像1 | ユーザーが投稿した実物写真・ラベル画像パス (メイン) |
| **`user_id`** | `TEXT` | NULL可<br>DEFAULT 'test_seed_secondary_sources' | ユーザーID | ログインアカウントの識別ID |
| **`created_at`** | `TEXT` | NULL可 | 投稿日時 | 評価が投稿された日時 |
| **`total_score`** | `REAL` | NULL可 | 総合評価点 (★) | 総合満足度スコア (1.0〜5.0) |
| **`taste_score`** | `REAL` | NULL可 | 味わい評点 | 味・旨味・キレに対する個別評点 (1.0〜5.0) |
| **`aroma_score`** | `REAL` | NULL可 | 香り評点 | 吟醸香・香り立ちに対する個別評点 (1.0〜5.0) |
| **`image_accuracy_score`** | `REAL` | NULL可<br>DEFAULT 1.0 | 画像整合性スコア | 画像と銘柄の一致確信度 (1.0=適合) |
| **`rating_image_2`** | `TEXT` | NULL可 | 添付画像2 | ユーザーが投稿した実物写真・料理写真パス (サブ) |

---

### 📋 `user_profiles` (ユーザープロファイル・嗜好設定)

- **概要**: ユーザーごとの味わい嗜好（甘辛、酸味、フルーティ派等）や表示アイコン、AIおすすめ生成用設定を保持するテーブル。
- **レコード件数**: **2** 件
- **対応CSV**: [`user_profiles.csv`](./user_profiles.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | プロファイルを一意に識別する主キー (INTEGER) |
| **`user_name`** | `TEXT` | NOT NULL | 対象ユーザーID | プロファイルが紐づくユーザー名 (`users.user_id`) |
| **`display_name`** | `TEXT` | NOT NULL | プロファイル表示名 | 画面表示用のニックネーム |
| **`avatar_icon`** | `TEXT` | NULL可 | アバターアイコン | ユーザーアイコンの絵文字や画像識別子 (例: 🍶, 🌸) |
| **`preference_text`** | `TEXT` | NULL可 | 嗜好プロファイル | 好みの酒質・味わい傾向 (AIおすすめ生成時に参照される特徴テキスト) |
| **`writing_style`** | `TEXT` | NULL可 | コメント文体 | AIアシスト時のトーン＆マナー設定 |
| **`is_primary`** | `INTEGER` | NULL可<br>DEFAULT 0 | メインアカウントフラグ | デフォルトのメインユーザーかどうかのフラグ (1/0) |
| **`created_at`** | `TEXT` | NULL可 | 作成日時 | プロファイル作成日時 |

---

### 📋 `users` (ユーザーアカウント)

- **概要**: システムへのログインアカウント（システム管理者、酒蔵管理者、一般ユーザー）の認証情報およびロール権限、担当酒蔵を管理するテーブル。
- **レコード件数**: **8** 件
- **対応CSV**: [`users.csv`](./users.csv)

| カラム名 (Column) | データ型 | NULL許容 / 制約 | 日本語項目名 | 項目説明・詳細 |
|:---|:---:|:---:|:---|:---|
| **`id`** | `INTEGER` | **PRIMARY KEY** | ID | ユーザーを一意に識別する主キー (INTEGER) |
| **`user_id`** | `TEXT` | NOT NULL | ログインID | ログイン時に使用する一意なユーザーID (例: hitoshi, nao, admin) |
| **`password`** | `TEXT` | NOT NULL | パスワード | アカウントのログインパスワード |
| **`user_name`** | `TEXT` | NOT NULL | 表示名 | 画面上に表示されるユーザーの名称 |
| **`role`** | `TEXT` | NOT NULL | ロール権限 | 権限ロール (`system_admin`: システム管理者, `brewery_admin`: 酒蔵管理者, `general_user`: 一般利用者) |
| **`assigned_brewery`** | `TEXT` | NULL可 | 担当酒蔵名 | 酒蔵管理者の場合に担当する酒蔵の名称 (システム管理者の場合はNULL) |
| **`created_at`** | `DATETIME` | NULL可<br>DEFAULT CURRENT_TIMESTAMP | アカウント作成日時 | ユーザーが登録された日時 |

---
