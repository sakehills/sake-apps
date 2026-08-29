-- マイグレーション: お祝い・記念日シーン、命名由来・誕生ストーリー、味わい・香り特長、総合解説文の全件実装
-- 実行日: 2026-08-29

-- 1. カラムの追加（存在しない場合）
ALTER TABLE products ADD COLUMN taste_profile TEXT;
ALTER TABLE products ADD COLUMN aroma_notes TEXT;
ALTER TABLE products ADD COLUMN product_description TEXT;
ALTER TABLE products ADD COLUMN celebration_scenes TEXT;
ALTER TABLE products ADD COLUMN brand_story TEXT;
ALTER TABLE products ADD COLUMN gift_packaging TEXT;
ALTER TABLE products ADD COLUMN celebration_phrase TEXT;

-- 2. インデックスの最適化
CREATE INDEX IF NOT EXISTS idx_products_celebration ON products(celebration_scenes);
CREATE INDEX IF NOT EXISTS idx_products_gift_pkg ON products(gift_packaging);

-- 3. 全14,453製品データの補完（Pythonスクリプトより自動実行）
