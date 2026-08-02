import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "sake_database.db")
README_PATH = os.path.join(ROOT_DIR, "README.txt")

# 1. Update Database
print(f"Connecting to DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("UPDATE users SET password = 'password'")
conn.commit()
print(f"Updated passwords for all {cursor.rowcount} users in DB to 'password'.")

# Display updated users list
cursor.execute("SELECT id, user_id, user_name, role, password FROM users ORDER BY id ASC")
users = cursor.fetchall()
print("\n--- 👤 最新登録アカウント＆パスワード一覧 ---")
for u in users:
    print(f" ID: {u[1]:<12} | パスワード: {u[4]:<10} | 名前: {u[2]:<20} | ロール: {u[3]}")
conn.close()

# 2. Update quick login buttons in HTML templates
NEW_QUICK_BUTTONS = """
        <!-- ワンクリック アカウント選択ボタン -->
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-bottom: 1.2rem;">
            <button type="button" onclick="selectQuickAccount('hitoshi', 'password')" style="background: rgba(212, 175, 55, 0.2); border: 1px solid rgba(212, 175, 55, 0.5); color: #f3e5ab; padding: 0.6rem 0.4rem; border-radius: 8px; font-size: 0.78rem; cursor: pointer; text-align: center;">
                <strong>👑 hitoshi</strong><br><small style="opacity:0.8">管理者権限</small>
            </button>
            <button type="button" onclick="selectQuickAccount('user2', 'password')" style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.4); color: #93c5fd; padding: 0.6rem 0.4rem; border-radius: 8px; font-size: 0.78rem; cursor: pointer; text-align: center;">
                <strong>👤 user2</strong><br><small style="opacity:0.8">一般利用者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('user3', 'password')" style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #6ee7b7; padding: 0.6rem 0.4rem; border-radius: 8px; font-size: 0.78rem; cursor: pointer; text-align: center;">
                <strong>👤 user3</strong><br><small style="opacity:0.8">一般利用者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('dassai_admin', 'password')" style="background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.4); color: #c4b5fd; padding: 0.6rem 0.4rem; border-radius: 8px; font-size: 0.78rem; cursor: pointer; text-align: center;">
                <strong>🍶 酒蔵 (獺祭)</strong><br><small style="opacity:0.8">旭酒造 管理</small>
            </button>
            <button type="button" onclick="selectQuickAccount('hakkai_admin', 'password')" style="background: rgba(236, 72, 153, 0.15); border: 1px solid rgba(236, 72, 153, 0.4); color: #fbcfe8; padding: 0.6rem 0.4rem; border-radius: 8px; font-size: 0.78rem; cursor: pointer; text-align: center;">
                <strong>🍶 酒蔵 (八海山)</strong><br><small style="opacity:0.8">八海醸造 管理</small>
            </button>
            <button type="button" onclick="selectQuickAccount('admin', 'password')" style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 0.6rem 0.4rem; border-radius: 8px; font-size: 0.78rem; cursor: pointer; text-align: center;">
                <strong>👑 admin</strong><br><small style="opacity:0.8">全権管理者</small>
            </button>
        </div>
"""

for fname in ['viewer.html', 'admin.html', 'brewery_admin.html']:
    p = os.path.join(ROOT_DIR, 'app', fname)
    if os.path.exists(p):
        txt = open(p, encoding='utf-8').read()
        if '<!-- ワンクリック アカウント選択ボタン -->' in txt:
            start_idx = txt.find('<!-- ワンクリック アカウント選択ボタン -->')
            end_idx = txt.find('</div>', start_idx) + 6
            txt = txt[:start_idx] + NEW_QUICK_BUTTONS.strip() + txt[end_idx:]
            with open(p, 'w', encoding='utf-8') as f:
                f.write(txt)
            print(f" Updated quick buttons in app/{fname}")

# 3. Update README.txt
README_CONTENT = """================================================================================
🍶 日本酒データベース App & 管理システム ガイド (README)
================================================================================

■ 1. サーバー起動・アクセス方法
--------------------------------------------------------------------------------
【サーバー起動コマンド】
  python server.py

【画面URL】
  ・日本酒Viewer (利用者画面)       : http://127.0.0.1:5000/
  ・酒蔵管理者専用ポータル画面      : http://127.0.0.1:5000/brewery_admin.html
  ・全システム管理者ダッシュボード : http://127.0.0.1:5000/admin.html


■ 2. 登録済みアカウント ＆ パスワード一覧 (全パスワード: password)
--------------------------------------------------------------------------------
※ 画面右上の「🔑 ログイン / アカウント切替」からワンクリックで切替可能です。

【システム管理者 (全権限・全画面・全データ編集可能)】
  ・ユーザーID: hitoshi   / パスワード: password  (名前: hitoshi)
  ・ユーザーID: admin     / パスワード: password  (名前: システム管理者)

【酒蔵管理者 (自社酒蔵基本情報の修正・自社銘柄の追加・修正・削除のみ可能)】
  ・ユーザーID: dassai_admin / パスワード: password (名前: 獺祭(旭酒造) 管理者 / 担当酒蔵: 旭酒造)
  ・ユーザーID: hakkai_admin / パスワード: password (名前: 八海山(八海醸造) 管理者 / 担当酒蔵: 八海醸造)

【一般利用者 (Viewer閲覧・口コミ投稿)】
  ・ユーザーID: user2     / パスワード: password  (名前: user2)
  ・ユーザーID: user3     / パスワード: password  (名前: user3)
  ・ユーザーID: user1     / パスワード: password  (名前: 日本酒ファン太郎)


■ 3. 酒蔵管理者専用機能概要 (http://127.0.0.1:5000/brewery_admin.html)
--------------------------------------------------------------------------------
  ・🏛️ 酒蔵プロフィールの編集 (酒蔵名、屋号、都道府県、住所、創業年、Webサイト、紹介文)
  ・🍶 自社銘柄の完全CRUD管理 (自社製品のみの一覧表示、新規銘柄追加、スペック編集、削除)


■ 4. フォルダ構造の構成
--------------------------------------------------------------------------------
  日本酒画像の切り取り/
  ├── server.py                        # HTTP Webサーバー (エントリーポイント)
  ├── README.txt                       # 本説明書ファイル
  │
  ├── app/                             # アプリ画面UI
  │   ├── viewer.html                  # 利用者画面 (日本酒Viewer)
  │   ├── brewery_admin.html           # 酒蔵管理者専用ポータル画面
  │   └── admin.html                   # 全システム管理者ダッシュボード
  │
  ├── database/                        # データベース領域
  │   └── sake_database.db             # メインSQLite DB (7,513件 + 酒蔵 + 口コミ)
  │
  ├── maps/                            # 精選国税庁・自治体日本酒マップ
  │   ├── 日本酒銘柄・特長マップ/      # 【都道府県名】日本酒銘柄ガイドPDF
  │   └── 酒蔵・アクセス位置マップ/    # 【都道府県名】酒蔵アクセスマップPDF
  │
  ├── cropped_images/                  # ボトル切り抜き画像
  ├── uploaded_images/                 # 口コミ添付写真
  ├── pipeline_scripts/                # データマイニング・自動補完スクリプト群
  └── legacy_data/                     # 開発初期・バックアップデータ

================================================================================
"""

with open(README_PATH, 'w', encoding='utf-8') as f:
    f.write(README_CONTENT)
print(" Updated README.txt with new password settings.")

print("\n==========================================")
print("✨ 全ユーザーのパスワードを 'password' に統一設定完了！")
print("==========================================")
