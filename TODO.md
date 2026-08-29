# 🍶 日本酒データベース 開発タスク＆TODOリスト

本ドキュメントは、日本酒データベース（`sake_database.db`）の継続的なデータ洗練および機能拡張のためのTODO管理リストです。

---

## 📌 保留中の主要タスク（TODO）

### 【手4】酒蔵マスターの深化（創業元号・仕込み水・杜氏流派・直売所・角打ち・文化財）

#### 1. 目的
全国1,629の酒蔵マスターに対し、歴史・醸造技術・観光の観点から詳細属性を付与し、文化的な深みと実用性の高いデータベースへ引き上げる。

#### 2. 追加予定のテーブル構造（マイグレーションSQL）
```sql
-- database-backup/migrations/migration_YYYYMMDD_deepen_brewery_master.sql
ALTER TABLE breweries ADD COLUMN era_name TEXT;              -- 創業元号（寛永、享保、文化、安政、明治、大正、昭和、令和）
ALTER TABLE breweries ADD COLUMN water_source_name TEXT;     -- 仕込み水源名称（灘の宮水、伏見の御香水、白神山地湧水、富士山伏流水 等）
ALTER TABLE breweries ADD COLUMN water_hardness TEXT;        -- 水質硬度（超軟水、軟水、中硬水、硬水）
ALTER TABLE breweries ADD COLUMN toji_guild TEXT;            -- 杜氏流派（南部杜氏、越後杜氏、丹波杜氏、能登杜氏、山内杜氏、会津杜氏、蔵元杜氏 等）
ALTER TABLE breweries ADD COLUMN kakuuchi_or_cafe TEXT;      -- 試飲・角打ち・カフェ併設（有料試飲あり、角打ち併設、カフェ併設、売店のみ）
ALTER TABLE breweries ADD COLUMN cultural_property INTEGER;  -- 文化財指定フラグ（国の登録有形文化財、伝統的建造物群）

CREATE INDEX IF NOT EXISTS idx_breweries_era_name ON breweries(era_name);
CREATE INDEX IF NOT EXISTS idx_breweries_toji_guild ON breweries(toji_guild);
CREATE INDEX IF NOT EXISTS idx_breweries_water_hardness ON breweries(water_hardness);
```

#### 3. 実行ステップ
1. **DDLマイグレーションSQLの保存**:
   - `database-backup/migrations/` 配下にSQLファイルを作成し実行。
2. **創業年・元号・老舗蔵フラグの自動マッピング**:
   - 創業西暦（例: 1625年）から元号（寛永2年）および老舗分類（江戸期創業、明治創業等）を自動判定。
3. **仕込み水・水質硬度・杜氏流派の地域別完全マッピング**:
   - 灘の宮水（中硬水・男酒）、伏見の御香水（中軟水・女酒）、新潟雪解け水（超軟水・淡麗）、西条湧水（軟水）等の水質データ付与。
   - 日本3大杜氏（南部・越後・丹波）、能登・山内・会津・広島杜氏および新世代「蔵元杜氏」の完全分類。
4. **蔵見学・直売所・角打ち・文化財情報の付与＆CSV同期**:
   - 一般見学可否、直営ショップ、角打ち・カフェ併設情報の反映。
   - `database-backup/breweries.csv` および `database-backup/database_schema.md` の更新。

---

## ✅ 完了済みの主要マイルストーン

1. **全国全酒蔵（1,376蔵）公式Webサイト深層走査＆全SKU完全抽出**（製品数 14,453件）
2. **全件品質保証（QA）検査＆重複・文字化け・法的規格（精米歩合・度数・特定名称）の100%適合是正**
3. **国内外23大コンペティション＆全国4大日本酒フェスティバル（CRAFT SAKE WEEK、にいがた酒の陣、西条酒まつり、SAKE PARK）の歴代受賞歴（2,721件）統合**
4. **全14,453製品に対する酒米・製法・生酒原酒判定、SSI 4タイプ分類（薫酒・爽酒・醇酒・熟酒）、推奨飲用温度帯（5℃〜50℃）の100%付与**
5. **日本酒度（SMV）・酸度・使用酵母（Yeast）および酒蔵創業年の全数補完**
6. **データベース全13テーブルのCSVバックアップ同期＆マイグレーションSQLの永続保存**
