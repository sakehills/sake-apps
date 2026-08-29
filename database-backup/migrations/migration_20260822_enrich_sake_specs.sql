-- マイグレーション: 日本酒データベース 専門スペック・SSI 4タイプ・推奨飲用温度帯の全件深化
-- 実行日: 2026-08-22

-- 1. インデックスの最適化
CREATE INDEX IF NOT EXISTS idx_products_ssi_type ON products(ssi_type);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_rice_variety ON products(rice_variety);
CREATE INDEX IF NOT EXISTS idx_products_brewing_method ON products(brewing_method);
CREATE INDEX IF NOT EXISTS idx_products_heating_type ON products(heating_type);
CREATE INDEX IF NOT EXISTS idx_products_is_genshu ON products(is_genshu);

-- 2. カラムデータの全数更新 (Pythonスクリプトより自動実行)
