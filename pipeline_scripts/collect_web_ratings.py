import os
import sqlite3
import random
from datetime import datetime, timedelta
import process_sake

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database", os.path.join("..", "database", "sake_database.db"))

# SNSや口コミ風のAさん、Bさん、Cさん用のコメントテンプレート
FLAVOR_TEMPLATES = {
    "薫酒": [
        "香りがとにかく華やかでフルーティ！一口飲むだけで甘酸っぱくてジューシーな旨味が口いっぱいに広がります。冷やしてワイングラスで飲むのがお気に入りです！",
        "洋梨のようなフレッシュなアロマが最高。日本酒特有のツンとするアルコール感がなく、すっきり綺麗に飲めるので女性にも超おすすめです。"
    ],
    "爽酒": [
        "キリッと冷やして飲むと抜群のキレ味！雑味が一切なくてクリアな喉越しなので、お刺身やカルパッチョなど魚料理との相性が完璧です。",
        "非常にスッキリした飲み口で、何杯でもいけちゃいます。食中酒としてこれ以上のものはないですね。毎日のお晩酌に常備したいです。"
    ],
    "醇酒": [
        "お米の豊かなコクとふくよかな旨味がしっかり主張してきます。常温や少し温めのぬる燗にすると旨味がさらに開いて美味しいです！",
        "しっかりとした飲みごたえがあり、焼き鳥や煮物といった醤油系の濃い味のお料理と合わせると最高のマリアージュを楽しめます。"
    ],
    "熟酒": [
        "琥珀色の美しい見た目と、ドライフルーツのような熟成された芳醇な香りがとにかく贅沢。ちびちびと常温で楽しむのがベストです。",
        "ナッツのような深い熟成香と濃厚な甘みが素晴らしいです。ブルーチーズやビターチョコレートといった個性的な肴とよく合います。"
    ]
}

USER_NAMES = ["Aさん", "Bさん", "Cさん"]
BODY_LEVELS = ["淡麗辛口", "中間", "濃醇"]
AROMA_LEVELS = ["しっかり個性的", "すっきりおだやか", "華やかフルーティ"]

def main():
    if not os.path.exists(DB_PATH):
        print("データベースが見つかりません。")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # "hitocie" 以外の一般ユーザー (Aさん, Bさん, Cさんなど) の既存評価を一旦クリア
    print("Aさん、Bさん、Cさんの過去の自動生成口コミデータをクリアします...")
    cursor.execute("DELETE FROM user_flavor_ratings WHERE user_name != 'hitocie'")
    
    # productsの一覧を取得
    cursor.execute("SELECT id, spec_name, category, ssi_type, cropped_image_path_front FROM products")
    products = cursor.fetchall()
    
    print(f"全 {len(products)} 銘柄に対して「Aさん」「Bさん」「Cさん」名義の画像付き口コミデータを自動生成・登録します...")
    
    ratings_count = 0
    
    for product in products:
        pid, spec_name, category, ssi_type, img_front = product
        
        # SSIタイプが未設定の場合は、カテゴリから大まかに割り当て
        ssi_type = ssi_type or "爽酒"
        
        # 1銘柄につき 1〜2 件の他者レビューを登録
        num_reviews = random.randint(1, 2)
        selected_users = random.sample(USER_NAMES, num_reviews)
        
        for user in selected_users:
            comment_text = random.choice(FLAVOR_TEMPLATES[ssi_type])
            
            body_level = random.choice(BODY_LEVELS)
            aroma_level = random.choice(AROMA_LEVELS)
            
            # スコアの生成 (総合: 3.5〜5.0, 個別: 3.0〜5.0 / 20%でNone)
            total_score = random.choice([3.5, 4.0, 4.5, 5.0])
            taste_score = random.choice([3.0, 3.5, 4.0, 4.5, 5.0]) if random.random() < 0.8 else None
            aroma_score = random.choice([3.0, 3.5, 4.0, 4.5, 5.0]) if random.random() < 0.8 else None
            
            # 投稿時間をランダムにバラつかせる
            days_ago = random.randint(2, 45)
            created_at = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))).isoformat()
            
            # 約80%の確率で、お酒の切り出し前面画像を「口コミ添付写真」としてダミー登録する
            rating_image = img_front if random.random() < 0.8 else None
            
            cursor.execute("""
                INSERT INTO user_flavor_ratings (
                    product_id, user_name, ssi_type, body_level, aroma_level, comment, rating_image, user_id, created_at,
                    total_score, taste_score, aroma_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pid, user, ssi_type, body_level, aroma_level, comment_text, rating_image, 'dummy_sns_source', created_at,
                  total_score, taste_score, aroma_score))
            ratings_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"合計 {ratings_count} 件の他者評価レビュー（画像付き）を登録しました。")
    
    # JSデータをエクスポート
    process_sake.export_to_js()
    print("JSデータのエクスポートが完了しました。")

if __name__ == "__main__":
    main()
