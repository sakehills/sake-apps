-- マイグレーション: 酒蔵マスター詳細情報（創業年・杜氏・仕込み水・直売所）＆ 日本酒度・酸度・使用酵母の全件補完
-- 実行日: 2026-08-22

-- 1. インデックスの最適化
CREATE INDEX IF NOT EXISTS idx_breweries_prefecture ON breweries(prefecture);
CREATE INDEX IF NOT EXISTS idx_breweries_founded_year ON breweries(founded_year);
CREATE INDEX IF NOT EXISTS idx_products_smv ON products(smv);
CREATE INDEX IF NOT EXISTS idx_products_acidity ON products(acidity);
CREATE INDEX IF NOT EXISTS idx_products_yeast ON products(yeast);

-- 2. カラムデータの全数更新 (Pythonスクリプトより自動実行)
