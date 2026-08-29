-- マイグレーション: 国内外主要コンペティション（鑑評会・IWC・SAKE COMP・Kura Master）歴代受賞歴の統合
-- 実行日: 2026-08-22

-- 1. インデックスの最適化
CREATE INDEX IF NOT EXISTS idx_awards_comp_year ON awards(competition_id, year);
CREATE INDEX IF NOT EXISTS idx_awards_prize ON awards(prize);
CREATE INDEX IF NOT EXISTS idx_awards_is_gold ON awards(is_gold_award);

-- 2. カラムデータの全数更新 (Pythonスクリプトより自動実行)
