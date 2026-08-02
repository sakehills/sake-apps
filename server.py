import os
import sqlite3
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_scripts"))
import process_sake  # DB更新後にJSを再エクスポートするためにインポート

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "sake_database.db")

import base64
import uuid

UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_base64_image(base64_str, prefix="img"):
    if not base64_str or not base64_str.startswith("data:image/"):
        return base64_str
    
    try:
        # ヘッダーとデータ部分を分離
        header, encoded = base64_str.split(",", 1)
        # 拡張子の特定
        ext = "png"
        if "jpeg" in header or "jpg" in header:
            ext = "jpeg"
        elif "gif" in header:
            ext = "gif"
        elif "webp" in header:
            ext = "webp"
            
        # デコード
        data = base64.b64decode(encoded)
        filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(data)
            
        # 相対パスを返す
        return f"uploaded_images/{filename}"
    except Exception as e:
        print(f"画像保存エラー: {e}")
        return base64_str

import urllib.parse
import urllib.request
import re

def search_web_snippets(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://duckduckgo.com/'
    }
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        snippets = []
        matches = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        for m in matches[:5]:
            clean = re.sub(r'<[^>]+>', '', m).strip()
            snippets.append(clean)
        return "\n".join(snippets)
    except Exception as e:
        print(f"検索エラー (HTML GET): {e}")
        return ""

def extract_specs_with_gemini(brand, brewery, search_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("警告: GEMINI_API_KEY が設定されていません。")
        return {
            "category": None, "alcohol": None, "polish_ratio": None,
            "ingredients": None, "rice_variety": None, "yeast": None,
            "smv": None, "acidity": None, "amino_acidity": None,
            "heating_type": None, "is_genshu": None, "brewing_method": None, "serving_temperature": None,
            "confidence": 0.0
        }
        
    try:
        from google import genai
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        client = genai.Client(api_key=clean_key)
        
        prompt = f'''以下の検索テキスト情報を元に、日本酒「{brand}」（製造蔵: {brewery}）の製品スペック（特定名称、アルコール度数、精米歩合、原材料、原料米、使用酵母、日本酒度、酸度、アミノ酸度、およびディープスペックとして火入れ回数/タイプ、原酒かどうか、仕込み方法、推奨飲用温度帯）を抽出し、以下のキーを持つ純粋なJSONオブジェクトのみで返答してください。推測が含まれる場合は confidence を低く（0.5〜0.6）、確実な場合は高く（0.8〜0.9）設定してください。情報がない場合は null にしてください。
※余計な文章やマークダウンの ```json 等の囲みは一切含めず、純粋なJSON文字列だけを返してください。

【出力キーと型】
{{
  "category": "純米吟醸 などの特定名称文字列 (または null)",
  "alcohol": 15.5 などの数値 (または null)",
  "polish_ratio": "50% などの文字列 (または null)",
  "ingredients": "米、米麹 などのカンマ区切り文字列 (または null)",
  "rice_variety": "山田錦 などの文字列 (または null)",
  "yeast": "協会9号 などの酵母名 (または null)",
  "smv": "+3.0 などの符号付き日本酒度 (または null)",
  "acidity": "1.4 などの酸度数値文字列 (占有は null)",
  "amino_acidity": "1.2 などのアミノ酸度数値文字列 (または null)",
  "heating_type": "生酒, 生詰, 生貯蔵, 2回火入れ などの加熱タイプ文字列 (または null)",
  "is_genshu": 原酒である（加水無しの記述あり）なら 1, そうでないなら 0 (または null)",
  "brewing_method": "生酛, 山廃, 木桶仕込み などの製造手法文字列 (または null)",
  "serving_temperature": "冷酒, ぬる燗, 熱燗 などのおすすめ温度帯文字列 (または null)",
  "confidence": 0.0〜1.0 の数値
}}

【検索情報】
{search_text}'''
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"Gemini SDK実行エラー: {e}")
        return None

def analyze_label_with_gemini(image_base64):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("警告: GEMINI_API_KEY が設定されていません。")
        return None
        
    try:
        from google import genai
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        client = genai.Client(api_key=clean_key)
        
        # Base64をパース
        if "," in image_base64:
            header, encoded = image_base64.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]
        else:
            encoded = image_base64
            mime_type = "image/jpeg"
            
        img_bytes = base64.b64decode(encoded)
        
        prompt = '''この日本酒の裏ラベル画像から、記載されている製品スペック（特定名称、アルコール度数、精米歩合、原材料、原料米、使用酵母、日本酒度、酸度、アミノ酸度、およびディープスペックとして火入れ回数/タイプ、原酒かどうか、仕込み方法、推奨飲用温度帯）をテキストOCRで読み取り、以下のキーを持つ純粋なJSONオブジェクトのみで返答してください。
画像内に値が明記されていない、または読み取れない項目は絶対に推測せず、必ず null に設定してください。
※余計な文章やマークダウンの ```json 等の囲みは一切含めず、純粋なJSON文字列だけを返してください。

【出力キーと型】
{
  "category": "純米吟醸 などの特定名称文字列 (または null)",
  "alcohol": 15.5 などの数値 (或者 null)",
  "polish_ratio": "50% などの文字列 (または null)",
  "ingredients": "米、米麹 などのカンマ区切り文字列 (または null)",
  "rice_variety": "山田錦 などの使用米文字列 (または null)",
  "yeast": "協会9号 などの使用酵母名 (または null)",
  "smv": "+3.0 などの符号付き日本酒度 (または null)",
  "acidity": "1.4 などの酸度数値文字列 (または null)",
  "amino_acidity": "1.2 などのアミノ酸度数値文字列 (または null)",
  "heating_type": "生酒, 生詰, 生貯蔵, 2回火入れ などの加熱タイプ文字列 (または null)",
  "is_genshu": 原酒である（加水無しの記述あり）なら 1, そうでないなら 0 (または null)",
  "brewing_method": "生酛, 山廃, 木桶仕込み などの製造手法文字列 (または null)",
  "serving_temperature": "冷酒, ぬる燗, 熱燗 などのおすすめ温度帯文字列 (または null)"
}'''
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                genai.types.Part.from_bytes(data=img_bytes, mime_type=mime_type),
                prompt
            ]
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"GeminiマルチモーダルOCRエラー: {e}")
        return None


def generate_ai_comment_for_product(conn, product_id, user_name, image_path, image_path_2=None, custom_notes=""):
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    p = cur.fetchone()
    if not p:
        return None, "Product not found"
        
    cur.execute("SELECT * FROM user_profiles WHERE user_name = ?", (user_name,))
    prof = cur.fetchone()
    if not prof:
        cur.execute("SELECT * FROM user_profiles WHERE is_primary = 1 LIMIT 1")
        prof = cur.fetchone()
        
    display_name = prof['display_name'] if prof else user_name
    writing_style = prof['writing_style'] if prof else "丁寧で実感を込めたレビュー文体"
    preference_text = prof['preference_text'] if prof else ""

    brand = p['brand_name'] or ''
    spec = p['spec_name'] or ''
    brewery = p['brewery_name'] or ''
    cat = p['category'] or '日本酒'
    alcohol = f"{p['alcohol']}度" if p['alcohol'] else '度数不明'
    polish = p['polish_ratio'] or '不明'
    rice = p['rice_variety'] or '国産米'

    prompt = f"""
あなたは以下のペルソナ（ユーザープロフィール）になりきって、実際に試飲した日本酒の口コミレビューと詳細評価を作成してください。

【レビュー投稿者】
名前: {display_name}
口調・文体方針: {writing_style}
好み・視点: {preference_text}

【評価対象の日本酒】
銘柄: {brand}
詳細・スペック: {spec}
酒蔵: {brewery}
特定名称: {cat}
アルコール度数: {alcohol}
精米歩合: {polish}
使用米: {rice}
追加メモ/特記事項: {custom_notes}

以下のJSONフォーマットのみを返してください。余計な解説テキストは一切含めないでください。

```json
{{
    "comment": "ペルソナになりきったリアルで魅力的なレビューテキスト（100〜250文字程度）",
    "ssi_type": "薫酒",
    "body_level": "中庸",
    "aroma_level": "華やか",
    "total_score": 4.5,
    "taste_score": 4.4,
    "aroma_score": 4.6
}}
```
"""
    api_key = os.environ.get("GEMINI_API_KEY")
    result_data = None
    if api_key:
        try:
            from google import genai
            clean_key = api_key.strip().replace('"', '').replace("'", "")
            client = genai.Client(api_key=clean_key)
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            raw = response.text.strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                result_data = json.loads(match.group(0))
        except Exception as e:
            print(f"[AI Comment Gen Error]: {e}")
            
    if not result_data:
        # Structured Fallback Generator
        if "大吟醸" in cat or "吟醸" in cat:
            ssi = "薫酒"
            aroma = "華やか"
            body = "やや軽快"
            comment = f"【{brand}】口に含んだ瞬間、華やかでエレガントな香りが広がり、繊細な米の旨味がスッと消えていく素晴らしいキレを感じました！{brewery}さんの技術が詰まった至高の一杯ですね。"
        elif "純米" in cat or "特別純米" in cat:
            ssi = "醇酒"
            aroma = "穏やか"
            body = "中庸"
            comment = f"【{brand}】お米本来の深みとふくよかなコクがしっかり感じられます！冷やしても温めても美味しい食中酒として最高の味わいでした。"
        else:
            ssi = "爽酒"
            aroma = "穏やか"
            body = "軽快"
            comment = f"【{brand}】非常にすっきりとした口当たりで、どんな料理にも合わせやすい爽やかな一杯でした！"

        if user_name == "sommelier_yamada":
            comment = f"プロの視点から評価させていただきます。{brand}（{brewery}）は、{rice}由来の酸と立ち上がるアロマのバランスが非常に秀逸です。食中酒としてのペアリング提案が非常に楽しみな逸品です。"
        elif user_name == "izakaya_meguri":
            comment = f"居酒屋で一杯！{brand}、呑みごたえがあって最高にウマい！おつまみがどんどん進んじゃうキレとコク、リピート確定です！"

        result_data = {
            "comment": comment,
            "ssi_type": ssi,
            "body_level": body,
            "aroma_level": aroma,
            "total_score": 4.5,
            "taste_score": 4.4,
            "aroma_score": 4.6
        }

    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO user_flavor_ratings (
            product_id, user_name, ssi_type, body_level, aroma_level, comment, rating_image, rating_image_2, user_id, created_at, total_score, taste_score, aroma_score, image_accuracy_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1.0)
    """, (
        product_id, user_name, result_data['ssi_type'], result_data['body_level'], result_data['aroma_level'],
        result_data['comment'], image_path, image_path_2, user_name, now,
        result_data['total_score'], result_data['taste_score'], result_data['aroma_score']
    ))
    conn.commit()
    return result_data, None


class SakeApiServer(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # viewer.htmlをルートとしてサービングするためのパス翻訳
        if path == "/" or path == "":
            return os.path.join(BASE_DIR, "app", "viewer.html")
        elif path == "/admin" or path == "/admin.html":
            return os.path.join(BASE_DIR, "app", "admin.html")
        elif path == "/brewery_admin" or path == "/brewery_admin.html":
            return os.path.join(BASE_DIR, "app", "brewery_admin.html")
        return super().translate_path(path)
    def do_GET(self):
        if self.path.startswith("/api/image/proxy"):
            import urllib.parse
            import urllib.request
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            image_url = params.get('url', [None])[0]
            
            if not image_url:
                self.send_response(400)
                self.end_headers()
                return
                
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Referer': 'https://shop.isego.shop/'
                }
                req = urllib.request.Request(image_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    img_data = response.read()
                    content_type = response.headers.get('Content-Type', 'image/jpeg')
                    
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(img_data)
            except Exception as e:
                print(f"画像プロキシエラー: {e}")
                self.send_response(500)
                self.end_headers()
            return
            
        elif self.path == "/api/products":
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        p.id as id,
                        p.brand_name as name,
                        p.spec_name as sub_name,
                        p.brewery_name as brewery,
                        p.category as sake_type,
                        p.alcohol as alcohol_content,
                        p.ingredients as raw_materials,
                        p.polish_ratio as polishing_rate,
                        p.rice_variety as rice_variety,
                        p.yeast as yeast,
                        p.smv as smv,
                        p.acidity as acidity,
                        p.amino_acidity as amino_acidity,
                        p.cropped_image_path_front as cropped_image_path_front,
                        p.cropped_image_path_back as cropped_image_path_back,
                        p.ssi_type as ssi_type,
                        p.body_level as body_level,
                        p.aroma_level as aroma_level,
                        p.comment as comment,
                        p.heating_type as heating_type,
                        p.is_genshu as is_genshu,
                        p.brewing_method as brewing_method,
                        p.serving_temperature as serving_temperature,
                        p.jan_code as jan_code,
                        p.prefecture as prefecture
                    FROM products p
                    ORDER BY p.id ASC
                """)
                products = [dict(row) for row in cursor.fetchall()]
                
                # 2. 口コミ全件を一括取得
                cursor.execute("""
                    SELECT product_id, ssi_type, body_level, aroma_level, comment, user_name, created_at, rating_image, rating_image_2, total_score, taste_score, aroma_score, image_accuracy_score
                    FROM user_flavor_ratings
                    ORDER BY id DESC
                """)
                all_ratings = [dict(row) for row in cursor.fetchall()]
                
                # 3. ratings を product_id ごとにマッピング
                ratings_map = {}
                for r in all_ratings:
                    pid = r['product_id']
                    if pid not in ratings_map:
                        ratings_map[pid] = []
                    ratings_map[pid].append(r)
                
                # 3. awards を厳格な完全一致 (entry_name == spec_name / brand_name) でマッピング
                product_awards_map = {}
                try:
                    cursor.execute("""
                        SELECT a.id, a.competition_id, c.name as competition_name, a.year, a.prize, a.category as award_category, a.entry_name
                        FROM awards a
                        JOIN competitions c ON a.competition_id = c.id
                    """)
                    all_awards = [dict(row) for row in cursor.fetchall()]
                    
                    product_by_spec = {}
                    product_by_brand = {}
                    for p in products:
                        pid = p['id']
                        bname = (p.get('name') or p.get('brand_name') or '').strip()
                        sname = (p.get('sub_name') or p.get('spec_name') or '').strip()
                        if bname:
                            product_by_brand.setdefault(bname, []).append(pid)
                        if sname:
                            product_by_spec.setdefault(sname, []).append(pid)
                            
                    for aw in all_awards:
                        entry = (aw['entry_name'] or '').strip()
                        if not entry:
                            continue
                        matched_pids = set()
                        # 1. spec_name との完全一致
                        if entry in product_by_spec:
                            for pid in product_by_spec[entry]:
                                matched_pids.add(pid)
                        # 2. brand_name との完全一致
                        elif entry in product_by_brand:
                            for pid in product_by_brand[entry]:
                                matched_pids.add(pid)
                                
                        for pid in matched_pids:
                            product_awards_map.setdefault(pid, []).append(aw)
                except Exception as e:
                    print(f"Awards query warning: {e}")
                
                # 4. products に結合し、外部画像はプロキシ経由にし、ローカルは相対パス補正
                import urllib.parse
                import re

                def parse_numeric(val):
                    if not val or val == "非公開":
                        return None
                    matches = re.findall(r'[-+]?\d+(?:\.\d+)?', str(val))
                    if not matches:
                        return None
                    floats = [float(m) for m in matches]
                    return sum(floats) / len(floats)

                def calculate_flavor_coordinates(smv_str, acidity_str):
                    smv = parse_numeric(smv_str)
                    acidity = parse_numeric(acidity_str)
                    if smv is None or acidity is None:
                        return None, None
                    try:
                        amakarado = 193593.0 / (1443.0 + smv) - 1.16 * acidity - 132.57
                        noutando = 94545.0 / (1443.0 + smv) + 1.88 * acidity - 68.54
                        # 一般的なマップに合わせて右側(+)を辛口、左側(-)を甘口とするため符号を反転
                        flavor_x = round(-1.0 * amakarado, 2)
                        flavor_y = round(noutando, 2)
                        return flavor_x, flavor_y
                    except ZeroDivisionError:
                        return None, None

                for p in products:
                    p['ratings'] = ratings_map.get(p['id'], [])
                    p['awards'] = product_awards_map.get(p['id'], [])
                    
                    # 画像選出ロジック: 口コミ投稿の写真を優先し、精度スコア順に選出
                    ratings_list = p['ratings']
                    img_ratings = [r for r in ratings_list if r.get('rating_image')]
                    if img_ratings:
                        def img_score(r):
                            acc = float(r.get('image_accuracy_score') or 1.0) * 50
                            usr = 100 if r.get('user_name') == 'hitocie' else 20
                            tot = float(r.get('total_score') or 0.0) * 10
                            has_c = 20 if r.get('comment') else 0
                            return acc + usr + tot + has_c
                        best_r = max(img_ratings, key=img_score)
                        p['cropped_image_path_front'] = best_r['rating_image']
                    else:
                        p['cropped_image_path_front'] = 'cropped_images/placeholder_noimage.jpg'
                    
                    # 味わいマップ座標の動的計算
                    fx, fy = calculate_flavor_coordinates(p.get('smv'), p.get('acidity'))
                    p['flavor_x'] = fx
                    p['flavor_y'] = fy

                    if p['cropped_image_path_front']:
                        try:
                            val = p['cropped_image_path_front']
                            if val.startswith("http://") or val.startswith("https://") or val.startswith("http:/") or val.startswith("https:/"):
                                if val.startswith("https:/") and not val.startswith("https://"):
                                    val = val.replace("https:/", "https://", 1)
                                elif val.startswith("http:/") and not val.startswith("http://"):
                                    val = val.replace("http:/", "http://", 1)
                                p['cropped_image_path_front'] = f"/api/image/proxy?url={urllib.parse.quote(val)}"
                            elif not val.startswith("data:image/") and not val.startswith("uploaded_images/") and not val.startswith("cropped_images/"):
                                p['cropped_image_path_front'] = os.path.relpath(val, BASE_DIR).replace('\\', '/')
                        except Exception:
                            pass
                            
                    if p['cropped_image_path_back']:
                        try:
                            val = p['cropped_image_path_back']
                            if val.startswith("http://") or val.startswith("https://") or val.startswith("http:/") or val.startswith("https:/"):
                                if val.startswith("https:/") and not val.startswith("https://"):
                                    val = val.replace("https:/", "https://", 1)
                                elif val.startswith("http:/") and not val.startswith("http://"):
                                    val = val.replace("http:/", "http://", 1)
                                p['cropped_image_path_back'] = f"/api/image/proxy?url={urllib.parse.quote(val)}"
                            elif not val.startswith("data:image/") and not val.startswith("uploaded_images/") and not val.startswith("cropped_images/"):
                                p['cropped_image_path_back'] = os.path.relpath(val, BASE_DIR).replace('\\', '/')
                        except Exception:
                            pass
                
                
                    # 画像優先度判定ロジック:
                    # (1) 酒蔵管理者が登録した画像 (cropped_image_path_front)
                    # (2) なければコメント写真の中で最もラベル精度が高いもの (image_accuracy_score)
                    # (3) なければ None (画面上は空白表示)
                    best_img = None
                    if p.get('cropped_image_path_front') and str(p.get('cropped_image_path_front')).strip():
                        best_img = p['cropped_image_path_front']
                        
                    if not best_img and p.get('ratings'):
                        r_with_imgs = [r for r in p['ratings'] if r.get('rating_image') and str(r.get('rating_image')).strip()]
                        if r_with_imgs:
                            r_with_imgs.sort(key=lambda x: float(x.get('image_accuracy_score') or 0), reverse=True)
                            best_img = r_with_imgs[0]['rating_image']
                            
                    if best_img:
                        val = best_img
                        if val.startswith("http://") or val.startswith("https://") or val.startswith("http:/") or val.startswith("https:/"):
                            if val.startswith("https:/") and not val.startswith("https://"):
                                val = val.replace("https:/", "https://", 1)
                            elif val.startswith("http:/") and not val.startswith("http://"):
                                val = val.replace("http:/", "http://", 1)
                            best_img = f"/api/image/proxy?url={urllib.parse.quote(val)}"
                        elif not val.startswith("data:image/") and not val.startswith("uploaded_images/") and not val.startswith("cropped_images/"):
                            try:
                                best_img = os.path.relpath(val, BASE_DIR).replace('\\', '/')
                            except Exception: pass
                    
                    p['display_image'] = best_img

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(products, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                err_res = {"status": "error", "message": f"製品取得に失敗しました: {str(e)}"}
                self.wfile.write(json.dumps(err_res).encode('utf-8'))
                print(f"API製品取得エラー: {e}")
            finally:
                if conn:
                    conn.close()
        elif self.path.startswith("/api/brewery_admin/products"):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            brewery = params.get('brewery', [None])[0]
            
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if brewery:
                    cursor.execute("SELECT * FROM products WHERE brewery_name LIKE ? OR brand_name LIKE ? ORDER BY id DESC", (f"%{brewery}%", f"%{brewery}%"))
                else:
                    cursor.execute("SELECT * FROM products ORDER BY id DESC LIMIT 100")
                prods = [dict(row) for row in cursor.fetchall()]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(prods, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            finally:
                if conn: conn.close()
            return

        elif self.path.startswith("/api/brewery"):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            name = params.get('name', [None])[0]
            
            if not name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "name parameter is required"}).encode('utf-8'))
                return
                
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM breweries WHERE name = ? OR name_norm = ?", (name, name))
                brewery = cursor.fetchone()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                if brewery:
                    self.wfile.write(json.dumps(dict(brewery)).encode('utf-8'))
                else:
                    self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))
            except Exception as e:
                print(f"API brewery fetch error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn:
                    conn.close()
        elif self.path.startswith("/api/competitions"):
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.*, ce.year, ce.edition_label, ce.venue, ce.entries_total, ce.gold_count, ce.trophy_count, ce.platinum_count, ce.website as event_website
                    FROM competitions c
                    LEFT JOIN competition_events ce ON c.id = ce.competition_id
                    ORDER BY c.id ASC
                """)
                competitions = [dict(row) for row in cursor.fetchall()]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(competitions, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                print(f"API competitions error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn:
                    conn.close()

        elif self.path.startswith("/api/competition"):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            comp_id = params.get('id', [None])[0]
            
            if not comp_id:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "id parameter is required"}).encode('utf-8'))
                return
                
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM competitions WHERE id = ?", (comp_id,))
                comp = cursor.fetchone()
                
                if not comp:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Competition not found"}).encode('utf-8'))
                    return
                    
                cursor.execute("SELECT * FROM competition_events WHERE competition_id = ?", (comp_id,))
                events = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute("""
                    SELECT a.id, a.year, a.prize, a.category, a.entry_name, p.id as product_id, p.brand_name, p.brewery_name, p.cropped_image_path_front
                    FROM awards a
                    LEFT JOIN products p ON p.brand_name = a.entry_name OR p.spec_name = a.entry_name
                    WHERE a.competition_id = ?
                    ORDER BY a.year DESC, a.prize ASC
                """, (comp_id,))
                awards_list = [dict(row) for row in cursor.fetchall()]
                
                res_data = {
                    "competition": dict(comp),
                    "events": events,
                    "awards": awards_list
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                print(f"API competition detail error: {e}")
                self.send_response(500)
                self.end_headers()
        elif self.path == "/api/admin/profiles":
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_profiles ORDER BY is_primary DESC, id ASC")
                profiles = [dict(row) for row in cursor.fetchall()]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(profiles, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                print(f"API admin profiles error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn:
                    conn.close()
            return
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/login":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                u_id = data.get('user_id', '').strip()
                pwd = data.get('password', '').strip()
                
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, user_id, user_name, role, assigned_brewery FROM users WHERE user_id = ? AND password = ?", (u_id, pwd))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    u_dict = dict(user)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "user": u_dict}, ensure_ascii=False).encode('utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "ユーザーIDまたはパスワードが違います。"}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        elif self.path == "/api/brewery_admin/info/save":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                b_name = data.get('brewery_name', '').strip()
                kura_name = data.get('kura_name', '').strip()
                pref = data.get('prefecture', '').strip()
                address = data.get('address', '').strip()
                website = data.get('website', '').strip()
                founded = data.get('founded_year')
                desc = data.get('description', '').strip()
                now = datetime.now().isoformat()
                
                if not b_name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "酒蔵名が必要です"}).encode('utf-8'))
                    return
                    
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO breweries (name, kura_name, prefecture, address, website, founded_year, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(name) DO UPDATE SET kura_name=excluded.kura_name, prefecture=excluded.prefecture, address=excluded.address, website=excluded.website, founded_year=excluded.founded_year, description=excluded.description, updated_at=excluded.updated_at", (b_name, kura_name, pref, address, website, founded, desc, now, now))
                conn.commit()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "酒蔵基本情報を保存しました"}).encode('utf-8'))
            except Exception as e:
                print(f"Brewery info save error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn: conn.close()
            return

        elif self.path == "/api/brewery_admin/product/save":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                p_id = data.get('id')
                brand = data.get('brand_name', '').strip()
                spec = data.get('spec_name', '').strip()
                brewery = data.get('brewery_name', '').strip()
                cat = data.get('category', '').strip()
                alcohol = data.get('alcohol')
                smv = data.get('smv', '').strip()
                acidity = data.get('acidity', '').strip()
                polish = data.get('polish_ratio', '').strip()
                rice = data.get('rice_variety', '').strip()
                img_front = data.get('cropped_image_path_front', '')
                
                if not brand or not brewery:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "銘柄名と酒蔵名が必要です"}).encode('utf-8'))
                    return
                    
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                if p_id:
                    cursor.execute("UPDATE products SET brand_name=?, spec_name=?, brewery_name=?, category=?, alcohol=?, smv=?, acidity=?, polish_ratio=?, rice_variety=?, cropped_image_path_front=? WHERE id=?", (brand, spec, brewery, cat, alcohol, smv, acidity, polish, rice, img_front, p_id))
                else:
                    cursor.execute("INSERT INTO products (brand_name, spec_name, brewery_name, category, alcohol, smv, acidity, polish_ratio, rice_variety, cropped_image_path_front, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (brand, spec, brewery, cat, alcohol, smv, acidity, polish, rice, img_front, datetime.now().isoformat()))
                conn.commit()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "銘柄情報を保存しました"}).encode('utf-8'))
            except Exception as e:
                print(f"Brewery product save error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn: conn.close()
            return

        elif self.path == "/api/rating/delete":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                r_id = data.get('id')
                user_name = data.get('user_name')
                
                if not r_id:
                    self.send_response(400)
                    self.end_headers()
                    return
                    
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Verify ownership before deleting
                cursor.execute("SELECT user_name FROM user_flavor_ratings WHERE id = ?", (r_id,))
                r = cursor.fetchone()
                if not r:
                    self.send_response(404)
                    self.end_headers()
                    return
                    
                if user_name and r[0] != user_name:
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": "他人のコメントは削除できません"}).encode('utf-8'))
                    return
                    
                cursor.execute("DELETE FROM user_flavor_ratings WHERE id = ?", (r_id,))
                conn.commit()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "コメントを削除しました"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            finally:
                if conn: conn.close()
            return
        elif self.path == "/api/brewery_admin/product/delete":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                p_id = data.get('id')
                if not p_id:
                    self.send_response(400)
                    self.end_headers()
                    return
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = ?", (p_id,))
                conn.commit()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "銘柄を削除しました"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            finally:
                if conn: conn.close()
            return

        elif self.path == "/api/admin/profiles/save":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_name = data.get('user_name', '').strip()
                display_name = data.get('display_name', '').strip()
                avatar_icon = data.get('avatar_icon', '👤')
                preference_text = data.get('preference_text', '')
                writing_style = data.get('writing_style', '')
                is_primary = 1 if data.get('is_primary') else 0
                now = datetime.now().isoformat()
                
                if not user_name or not display_name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "user_name and display_name required"}).encode('utf-8'))
                    return
                    
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_profiles (user_name, display_name, avatar_icon, preference_text, writing_style, is_primary, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_name) DO UPDATE SET
                        display_name=excluded.display_name,
                        avatar_icon=excluded.avatar_icon,
                        preference_text=excluded.preference_text,
                        writing_style=excluded.writing_style,
                        is_primary=excluded.is_primary
                """, (user_name, display_name, avatar_icon, preference_text, writing_style, is_primary, now))
                conn.commit()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                print(f"API admin profile save error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn:
                    conn.close()
            return

        elif self.path == "/api/admin/generate-comment":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                product_id = int(data.get('product_id'))
                user_name = data.get('user_name', 'hitocie')
                rating_image = data.get('rating_image')
                rating_image_2 = data.get('rating_image_2') or data.get('rating_image2')
                custom_notes = data.get('custom_notes', '')
                
                if rating_image and rating_image.startswith("data:image/"):
                    rating_image = save_base64_image(rating_image, f"ai_gen_{product_id}_{user_name}_1")
                if rating_image_2 and rating_image_2.startswith("data:image/"):
                    rating_image_2 = save_base64_image(rating_image_2, f"ai_gen_{product_id}_{user_name}_2")

                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                res, err = generate_ai_comment_for_product(conn, product_id, user_name, rating_image, rating_image_2, custom_notes)
                
                if err:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": err}).encode('utf-8'))
                    return

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "data": res}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                print(f"API admin generate comment error: {e}")
                self.send_response(500)
                self.end_headers()
            finally:
                if conn:
                    conn.close()
            return
        if self.path == "/api/rate":
            print("[DEBUG] /api/rate POST request received.")
            content_length = int(self.headers['Content-Length'])
            print(f"[DEBUG] Content-Length: {content_length}")
            post_data = self.rfile.read(content_length)
            print("[DEBUG] Successfully read post_data.")
            
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                product_id = int(data.get('product_id'))
                ssi_type = data.get('ssi_type')
                body_level = data.get('body_level')
                aroma_level = data.get('aroma_level')
                comment = data.get('comment')
                user_name = data.get('user_name', '匿名')
                user_id = data.get('user_id', 'test_seed_secondary_sources')
                
                print(f"[DEBUG] Parsing parameters. user_name={user_name}, product_id={product_id}")
                rating_image = data.get('rating_image')
                rating_image_2 = data.get('rating_image_2') or data.get('rating_image2')
                if rating_image:
                    rating_image = save_base64_image(rating_image, f"rate_{product_id}_{user_name}_1")
                if rating_image_2:
                    rating_image_2 = save_base64_image(rating_image_2, f"rate_{product_id}_{user_name}_2")
                
                total_score = data.get('total_score')
                taste_score = data.get('taste_score')
                aroma_score = data.get('aroma_score')
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                if user_name == "hitocie":
                    cursor.execute("SELECT id FROM user_flavor_ratings WHERE product_id = ? AND user_name = 'hitocie'", (product_id,))
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute("""
                            UPDATE user_flavor_ratings SET
                                ssi_type = ?,
                                body_level = ?,
                                aroma_level = ?,
                                comment = ?,
                                rating_image = ?,
                                rating_image_2 = ?,
                                created_at = ?,
                                total_score = ?,
                                taste_score = ?,
                                aroma_score = ?
                            WHERE product_id = ? AND user_name = 'hitocie'
                        """, (ssi_type, body_level, aroma_level, comment, rating_image, rating_image_2, datetime.now().isoformat(),
                              total_score, taste_score, aroma_score, product_id))
                    else:
                        cursor.execute("""
                            INSERT INTO user_flavor_ratings (
                                product_id, ssi_type, body_level, aroma_level, comment, rating_image, rating_image_2, user_name, user_id, created_at,
                                total_score, taste_score, aroma_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (product_id, ssi_type, body_level, aroma_level, comment, rating_image, rating_image_2, user_name, user_id, datetime.now().isoformat(),
                              total_score, taste_score, aroma_score))
                else:
                    cursor.execute("""
                        INSERT INTO user_flavor_ratings (
                            product_id, ssi_type, body_level, aroma_level, comment, rating_image, rating_image_2, user_name, user_id, created_at,
                            total_score, taste_score, aroma_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (product_id, ssi_type, body_level, aroma_level, comment, rating_image, rating_image_2, user_name, user_id, datetime.now().isoformat(),
                          total_score, taste_score, aroma_score))
                
                conn.commit()
                print("[DEBUG] Transaction committed successfully.")
                
            except Exception as e:
                print(f"エラー発生: {str(e)}")
                import traceback
                traceback.print_exc()
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "status": "error",
                        "message": f"保存処理に失敗しました: {str(e)}"
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                except Exception as send_error:
                    print(f"レスポンス送信失敗: {str(send_error)}")
            finally:
                if conn:
                    conn.close()
                    print("[DEBUG] SQLite connection closed.")
            
            try:
                # レスポンス送信
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "コメントと味わい評価を正常に保存しました。"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"製品ID {product_id} の評価が更新されました。")
            except Exception as response_error:
                print(f"レスポンス送信エラー: {response_error}")
                
        elif self.path == "/api/rate/delete":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                product_id = int(data.get('product_id'))
                user_name = data.get('user_name', 'hitocie') # 削除できるのは hitocie 固定
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # 物理削除を実行
                cursor.execute("DELETE FROM user_flavor_ratings WHERE product_id = ? AND user_name = ?", (product_id, user_name))
                conn.commit()
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "コメントを正常に削除しました。"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"製品ID {product_id} の評価データが削除されました。")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "status": "error",
                    "message": f"削除処理に失敗しました: {str(e)}"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"削除エラー発生: {str(e)}")
        elif self.path == "/api/product/suggest":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                product_id = int(data.get('product_id'))
                req_jan_code = data.get('jan_code')
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT brand_name, brewery_name, jan_code FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()
                
                if not row:
                    raise Exception("指定された製品が見つかりません。")
                
                brand, brewery, db_jan_code = row[0], row[1], row[2]
                jan_code = req_jan_code if req_jan_code is not None else db_jan_code
                
                if jan_code:
                    print(f"[AI Suggest] JANコード「{jan_code}」からスペック情報をWeb自動検索中...")
                    query = f"JANコード {jan_code} スペック"
                else:
                    print(f"[AI Suggest] 銘柄「{brand}」({brewery}) のスペック情報をWebから自動検索中...")
                    query = f"{brewery} {brand} スペック"
                
                search_text = search_web_snippets(query)
                suggested_specs = extract_specs_with_gemini(brand, brewery, search_text)
                
                if suggested_specs is None:
                    raise Exception("AIによるスペック抽出に失敗しました。")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "data": suggested_specs
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                print(f"[AI Suggest] 銘柄「{brand}」のAI提案データを正常に送信しました。")
            except Exception as e:
                print(f"AI提案エラー発生: {str(e)}")
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "status": "error",
                        "message": f"AI提案の生成に失敗しました: {str(e)}"
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                except Exception as send_error:
                    print(f"レスポンス送信失敗: {str(send_error)}")
            finally:
                if conn:
                    conn.close()
        elif self.path == "/api/product/update":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            conn = None
            try:
                data = json.loads(post_data.decode('utf-8'))
                product_id = int(data.get('id'))
                category = data.get('category')
                alcohol = data.get('alcohol')
                polish_ratio = data.get('polish_ratio')
                ingredients = data.get('ingredients')
                rice_variety = data.get('rice_variety')
                yeast = data.get('yeast')
                smv = data.get('smv')
                acidity = data.get('acidity')
                amino_acidity = data.get('amino_acidity')
                jan_code = data.get('jan_code')
                heating_type = data.get('heating_type')
                is_genshu = data.get('is_genshu')
                brewing_method = data.get('brewing_method')
                serving_temperature = data.get('serving_temperature')
                
                # 画像（Base64またはnull）
                cropped_image_path_front = data.get('cropped_image_path_front')
                cropped_image_path_front = save_base64_image(cropped_image_path_front, f"front_{product_id}")
                cropped_image_path_back = data.get('cropped_image_path_back')
                cropped_image_path_back = save_base64_image(cropped_image_path_back, f"back_{product_id}")
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE products SET
                        category = ?,
                        alcohol = ?,
                        polish_ratio = ?,
                        ingredients = ?,
                        rice_variety = ?,
                        yeast = ?,
                        smv = ?,
                        acidity = ?,
                        amino_acidity = ?,
                        jan_code = ?,
                        heating_type = ?,
                        is_genshu = ?,
                        brewing_method = ?,
                        serving_temperature = ?,
                        cropped_image_path_front = COALESCE(?, cropped_image_path_front),
                        cropped_image_path_back = COALESCE(?, cropped_image_path_back)
                    WHERE id = ?
                """, (
                    category, alcohol, polish_ratio, ingredients, rice_variety, yeast, smv, acidity, amino_acidity, jan_code,
                    heating_type, is_genshu, brewing_method, serving_temperature,
                    cropped_image_path_front, cropped_image_path_back, product_id
                ))
                
                if cropped_image_path_front == "":
                    cursor.execute("UPDATE products SET cropped_image_path_front = NULL WHERE id = ?", (product_id,))
                if cropped_image_path_back == "":
                    cursor.execute("UPDATE products SET cropped_image_path_back = NULL WHERE id = ?", (product_id,))
                
                conn.commit()
            except Exception as e:
                print(f"スペック更新エラー発生: {str(e)}")
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "status": "error",
                        "message": f"スペック更新処理に失敗しました: {str(e)}"
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                except Exception as send_error:
                    print(f"レスポンス送信失敗: {str(send_error)}")
            finally:
                if conn:
                    conn.close()
                    
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "スペック情報を正常に更新しました。"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"製品ID {product_id} のスペック情報が更新されました。")
            except Exception as response_error:
                print(f"レスポンス送信エラー: {response_error}")
        elif self.path == "/api/product/analyze-label":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                image_base64 = data.get('image')
                
                if not image_base64:
                    raise Exception("画像データがありません。")
                
                print("[AI OCR] ボトル裏ラベル画像を解析中...")
                suggested_specs = analyze_label_with_gemini(image_base64)
                
                if suggested_specs is None:
                    raise Exception("Geminiによるラベル画像解析に失敗しました。")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "data": suggested_specs
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                print("[AI OCR] ラベル画像からスペックを正常に抽出しました。")
            except Exception as e:
                print(f"ラベル画像解析エラー発生: {str(e)}")
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "status": "error",
                        "message": f"ラベル画像解析に失敗しました: {str(e)}"
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                except Exception as send_error:
                    print(f"レスポンス送信失敗: {str(send_error)}")
        elif self.path == "/api/product/import-csv":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                import csv
                import io
                
                data = json.loads(post_data.decode('utf-8'))
                csv_text = data.get('csv_text')
                
                if not csv_text:
                    raise Exception("CSVテキストがありません。")
                
                f = io.StringIO(csv_text.strip())
                reader = csv.DictReader(f)
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                updated_count = 0
                skipped_count = 0
                
                # ヘッダーのエイリアスマッピング
                mappings = {
                    'brand_name': ['brand_name', 'ブランド名', '銘柄', '銘柄名', 'name', '商品名'],
                    'brewery_name': ['brewery_name', '蔵元', '蔵元名', '酒蔵', '酒蔵名', 'brewery'],
                    'jan_code': ['jan_code', 'jan', 'JAN', 'JANコード', 'バーコード'],
                    'category': ['category', '特定名称', 'カテゴリ', 'sake_type'],
                    'alcohol': ['alcohol', '度数', 'アルコール', 'アルコール度数', 'alcohol_content'],
                    'polish_ratio': ['polish_ratio', '精米歩合', '精米', 'polishing_rate'],
                    'ingredients': ['ingredients', '原材料', 'raw_materials'],
                    'rice_variety': ['rice_variety', '原料米', '使用米', '米の品種'],
                    'yeast': ['yeast', '酵母', '使用酵母'],
                    'smv': ['smv', '日本酒度', 'SMV'],
                    'acidity': ['acidity', '酸度'],
                    'amino_acidity': ['amino_acidity', 'アミノ酸度']
                }
                
                def get_mapped_value(row, field_key):
                    possible_keys = mappings.get(field_key, [])
                    for pk in possible_keys:
                        if pk in row:
                            return row[pk]
                    return None
                
                for row in reader:
                    brand = get_mapped_value(row, 'brand_name')
                    brewery = get_mapped_value(row, 'brewery_name')
                    jan = get_mapped_value(row, 'jan_code')
                    
                    if not brand and not jan:
                        skipped_count += 1
                        continue
                    
                    category = get_mapped_value(row, 'category')
                    alcohol = get_mapped_value(row, 'alcohol')
                    polish_ratio = get_mapped_value(row, 'polish_ratio')
                    ingredients = get_mapped_value(row, 'ingredients')
                    rice_variety = get_mapped_value(row, 'rice_variety')
                    yeast = get_mapped_value(row, 'yeast')
                    smv = get_mapped_value(row, 'smv')
                    acidity = get_mapped_value(row, 'acidity')
                    amino_acidity = get_mapped_value(row, 'amino_acidity')
                    
                    try:
                        alcohol = float(alcohol) if alcohol else None
                    except ValueError:
                        alcohol = None
                    
                    product_id = None
                    if jan:
                        cursor.execute("SELECT id FROM products WHERE jan_code = ?", (jan,))
                        res = cursor.fetchone()
                        if res:
                            product_id = res[0]
                    
                    if not product_id and brand:
                        if brewery:
                            cursor.execute("SELECT id FROM products WHERE brand_name LIKE ? AND brewery_name LIKE ?", (f"%{brand}%", f"%{brewery}%"))
                        else:
                            cursor.execute("SELECT id FROM products WHERE brand_name LIKE ?", (f"%{brand}%",))
                        res = cursor.fetchone()
                        if res:
                            product_id = res[0]
                            
                    if not product_id:
                        skipped_count += 1
                        continue
                    
                    update_fields = []
                    params = []
                    
                    fields_to_update = {
                        'category': category,
                        'alcohol': alcohol,
                        'polish_ratio': polish_ratio,
                        'ingredients': ingredients,
                        'rice_variety': rice_variety,
                        'yeast': yeast,
                        'smv': smv,
                        'acidity': acidity,
                        'amino_acidity': amino_acidity,
                        'jan_code': jan
                    }
                    
                    for f_name, f_val in fields_to_update.items():
                        if f_val is not None:
                            update_fields.append(f"{f_name} = ?")
                            params.append(f_val)
                    
                    if not update_fields:
                        skipped_count += 1
                        continue
                        
                    params.append(product_id)
                    query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, tuple(params))
                    updated_count += 1
                
                conn.commit()
                conn.close()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": f"CSVのインポートに成功しました。{updated_count}件を更新、{skipped_count}件をスキップしました。",
                    "updated": updated_count,
                    "skipped": skipped_count
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                print(f"[CSV Import] Processed CSV: updated={updated_count}, skipped={skipped_count}")
                
            except Exception as e:
                print(f"CSVインポートエラー発生: {str(e)}")
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "status": "error",
                        "message": f"CSVインポートに失敗しました: {str(e)}"
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                except Exception as send_error:
                    print(f"レスポンス送信失敗: {str(send_error)}")
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=SakeApiServer, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting API Server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run()
