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

# Set hitoshi to 'user' role
cursor.execute("UPDATE users SET role = 'user' WHERE user_id = 'hitoshi'")

# Set admin to 'system_admin' role
cursor.execute("UPDATE users SET role = 'system_admin' WHERE user_id = 'admin'")

conn.commit()
print("Updated user roles: hitoshi => 'user', admin => 'system_admin'.")

# Print current users
cursor.execute("SELECT id, user_id, user_name, role, password FROM users ORDER BY id ASC")
users = cursor.fetchall()
print("\n--- 👤 最新登録アカウント＆ロール一覧 ---")
for u in users:
    print(f" ID: {u[1]:<12} | 名前: {u[2]:<20} | ロール: {u[3]:<15} | PW: {u[4]}")
conn.close()

# 2. Update quick login buttons across HTML templates
NEW_QUICK_BUTTONS = """
        <!-- ワンクリック アカウント選択ボタン -->
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0.5rem; margin-bottom: 1.2rem;">
            <button type="button" onclick="selectQuickAccount('hitoshi', 'password')" style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.5); color: #93c5fd; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>👤 hitoshi</strong><br><small style="opacity:0.8">一般利用者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('nao', 'password')" style="background: rgba(236, 72, 153, 0.2); border: 1px solid rgba(236, 72, 153, 0.5); color: #fbcfe8; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>🌸 nao</strong><br><small style="opacity:0.8">一般利用者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('user2', 'password')" style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #6ee7b7; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>👤 user2</strong><br><small style="opacity:0.8">一般利用者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('user3', 'password')" style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.4); color: #93c5fd; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>👤 user3</strong><br><small style="opacity:0.8">一般利用者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('dassai_admin', 'password')" style="background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.4); color: #c4b5fd; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>🍶 酒蔵(獺祭)</strong><br><small style="opacity:0.8">旭酒造</small>
            </button>
            <button type="button" onclick="selectQuickAccount('hakkai_admin', 'password')" style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); color: #fef3c7; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>🍶 酒蔵(八海山)</strong><br><small style="opacity:0.8">八海醸造</small>
            </button>
            <button type="button" onclick="selectQuickAccount('admin', 'password')" style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.5); color: #fca5a5; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>👑 admin</strong><br><small style="opacity:0.8">システム管理者</small>
            </button>
            <button type="button" onclick="selectQuickAccount('user1', 'password')" style="background: rgba(212, 175, 55, 0.15); border: 1px solid rgba(212, 175, 55, 0.4); color: #f3e5ab; padding: 0.5rem 0.3rem; border-radius: 8px; font-size: 0.75rem; cursor: pointer; text-align: center;">
                <strong>👤 user1</strong><br><small style="opacity:0.8">一般利用者</small>
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
🍶 日本酒データベース アプリケーション 簡易利用ガイド (README)
================================================================================

■ 1. サーバーの起動とアクセス方法
--------------------------------------------------------------------------------
【起動コマンド】
  python server.py

【アクセスURL】
  ・日本酒Viewer (メイン画面)       : http://127.0.0.1:5000/
  ・酒蔵管理者専用ポータル         : http://127.0.0.1:5000/brewery_admin.html
  ・システム管理者ダッシュボード   : http://127.0.0.1:5000/admin.html


■ 2. 権限（ロール）について
--------------------------------------------------------------------------------
本アプリには3種類の権限（ロール）があり、見れる画面や操作できる範囲が制御されます。

  👑 【システム管理者】 (system_admin)
      ・全データ（7,513件）の閲覧、編集、削除、一括CSVインポート、AI機能を含む全権限。
      ・システム管理画面 (/admin.html) および 酒蔵ポータル (/brewery_admin.html) へアクセス可能。

  🍶 【酒蔵管理者】 (brewery_admin)
      ・自社の酒蔵基本プロフィールの編集、および自社が醸造する銘柄のみの追加・修正・削除。
      ・酒蔵専用ポータル (/brewery_admin.html) にアクセス可能（他社データは編集不可）。

  👤 【一般利用者】 (user)
      ・日本酒の検索・閲覧・詳細確認、および自身の名前での口コミ投稿・修正・削除。
      ・管理画面へのアクセスは制限されます。


■ 3. ログイン方法
--------------------------------------------------------------------------------
1. 画面右上の「🔑 ログイン / アカウント切替」ボタンをクリックします。
2. 表示されるモーダルから、テスト用ボタンをワンクリックするか、ID/パスワードを入力します。

【主なテスト用アカウント一覧】 (※ パスワードはすべて password です)
  ・admin         / password  (👑 システム管理者 - システム管理者)
  ・dassai_admin / password  (🍶 酒蔵管理者 - 旭酒造「獺祭」)
  ・hakkai_admin / password  (🍶 酒蔵管理者 - 八海醸造「八海山」)
  ・hitoshi      / password  (👤 一般利用者 - hitoshi)
  ・nao          / password  (👤 一般利用者 - nao)
  ・user1        / password  (👤 一般利用者 - 日本酒ファン太郎)
  ・user2        / password  (👤 一般利用者)
  ・user3        / password  (👤 一般利用者)


■ 4. 主要機能の使い方
--------------------------------------------------------------------------------
🍶 【日本酒Viewer (利用者画面)】 (http://127.0.0.1:5000/)
   ・日本酒の検索・絞り込み・詳細表示（スペック、受賞歴、味わいマップ表示）。
   ・「➕ コメントを追加」または「✍️ コメントの修正」から評価やレビュー写真の投稿・編集が可能。
   ・画像は【酒蔵公式画像 ＞ 綺麗度の高い投稿写真 ＞ 空白枠】の順で自動表示されます。

🏛️ 【酒蔵管理者専用ポータル】 (http://127.0.0.1:5000/brewery_admin.html)
   ・酒蔵プロフィールの修正（住所、創業年、Webサイト、紹介文）。
   ・自社銘柄の登録（ボトル画像アップロード対応）・スペック修正・削除。

⚙️ 【システム管理者ダッシュボード】 (http://127.0.0.1:5000/admin.html)
   ・全銘柄・全酒蔵データの検索・個別編集・削除・CSV一括インポート。

================================================================================
"""

with open(README_PATH, 'w', encoding='utf-8') as f:
    f.write(README_CONTENT)
print(" Updated README.txt with hitoshi as user and admin as system_admin.")
