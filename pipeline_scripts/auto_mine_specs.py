import os
import sys
import sqlite3
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
import process_sake

# UTF-8対策
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database", os.path.join("..", "database", "sake_database.db"))

# 簡易DuckDuckGo検索スニペット抽出
def search_web_snippets(query):
    import re
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
        print("警告: GEMINI_API_KEY が設定されていません。デモモード（モック）で返答します。")
        return get_mock_response(brand)
        
    try:
        from google import genai
        import re
        clean_key = api_key.strip().replace('"', '').replace("'", "")
        client = genai.Client(api_key=clean_key)
        
        prompt = f'''以下の検索テキスト情報を元に、日本酒「{brand}」（製造蔵: {brewery}）の製品スペック（特定名称、アルコール度数、精米歩合、原材料、原料米、使用酵母、日本酒度、酸度、アミノ酸度）を抽出し、以下のキーを持つ純粋なJSONオブジェクトのみで返答してください。推測が含まれる場合は confidence を低く（0.5〜0.6）、確実な場合は高く（0.8〜0.9）設定してください。情報がない場合は null にしてください。
※余計な文章やマークダウンの ```json 等の囲みは一切含めず、純粋なJSON文字列だけを返してください。

【出力キーと型】
{{
  "category": "純米吟醸 などの特定名称文字列 (または null)",
  "alcohol": 15.5 などの数値 (または null)",
  "polish_ratio": "50% などの文字列 (または null)",
  "ingredients": "米、米麹 などのカンマ区切り文字列 (または null)",
  "rice_variety": "山田錦 などの文字列 (または null)",
  "yeast": "協会9号 などの酵母名 (または null)",
  "smv": "+3.0 などの符号付き日本酒度 (占は null)",
  "acidity": "1.4 などの酸度数値文字列 (または null)",
  "amino_acidity": "1.2 などのアミノ酸度数値文字列 (または null)",
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

def get_mock_response(brand):
    # デモ用のモックデータ
    mock_data = {
        "特別本醸造 八海山": {
            "category": "特別本醸造", "alcohol": 15.5, "polish_ratio": "55%", 
            "ingredients": "米、米麹、醸造アルコール", "rice_variety": "五百万石", "yeast": "協会701号", 
            "smv": "+4.0", "acidity": "1.3", "amino_acidity": "1.2", "confidence": 0.95
        },
        "久保田": {
            "category": "純米大吟醸", "alcohol": 15.0, "polish_ratio": "50%", 
            "ingredients": "米、米麹", "rice_variety": "五百万石", "yeast": "自社酵母", 
            "smv": "+2.0", "acidity": "1.2", "amino_acidity": "1.0", "confidence": 0.90
        }
    }
    for k, v in mock_data.items():
        if k in brand:
            return v
    return {
        "category": "特定名称不明", "alcohol": None, "polish_ratio": "不明", 
        "ingredients": "不明", "rice_variety": "不明", "yeast": "不明", 
        "smv": "非公開", "acidity": "非公開", "amino_acidity": "非公開", "confidence": 0.4
    }

def main():
    if not os.path.exists(DB_PATH):
        print("データベースが見つかりません。")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 未取得（categoryが特定名称不明など）のお酒を上限5件抽出してテスト実行
    cursor.execute("""
        SELECT id, spec_name, brewery_name FROM products 
        WHERE (category = '特定名称不明' OR ingredients = '不明')
          AND (spec_name LIKE '%久保田%' OR spec_name LIKE '%八海山%' OR spec_name LIKE '%新政%')
        LIMIT 3
    """)
    targets = cursor.fetchall()
    
    if not targets:
        print("自動マイニング対象のお酒はありません（すべてスペック判明済みです）。")
        conn.close()
        return
        
    print(f"未登録の {len(targets)} 件の日本酒スペック情報を自動検索・マイニングします...")
    
    updated_count = 0
    
    for pid, spec_name, brewery_name in targets:
        print(f"\n--- 検索開始: {spec_name} (酒蔵: {brewery_name}) ---")
        
        # 検索クエリ
        query = f"{brewery_name} {spec_name} 日本酒度 酸度 使用米"
        search_text = search_web_snippets(query)
        
        if not search_text:
            print("検索結果が得られませんでした。スキップします。")
            continue
            
        print("Web情報を元に Gemini API でスペック判定を行います...")
        specs = extract_specs_with_gemini(spec_name, brewery_name, search_text)
        
        if specs and specs.get("confidence", 0.0) >= 0.7:
            print(f"解析成功 (確信度: {specs['confidence']}):")
            print(json.dumps(specs, indent=2, ensure_ascii=False))
            
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
                    confidence = ?,
                    source_id = 'auto_mine_gemini',
                    evidence = ?
                WHERE id = ?
            """, (
                specs.get("category") or "特定名称不明",
                specs.get("alcohol"),
                specs.get("polish_ratio") or "不明",
                specs.get("ingredients") or "不明",
                specs.get("rice_variety") or "不明",
                specs.get("yeast") or "不明",
                specs.get("smv") or "非公開",
                specs.get("acidity") or "非公開",
                specs.get("amino_acidity") or "非公開",
                specs["confidence"],
                f"Gemini API extracted from: {query}",
                pid
            ))
            updated_count += 1
            print(f"DBを更新しました: ID {pid}")
        else:
            print("確信度が低いため、更新をスキップしました。")
            
        # APIのレートリミット対策
        time.sleep(2)
        
    conn.commit()
    conn.close()
    
    print(f"\n合計 {updated_count} 件のスペック情報を自動補完・更新しました。")
    
    if updated_count > 0:
        # JSデータの更新
        process_sake.export_to_js()
        print("sake_data.js を再エクスポートしました。")

if __name__ == "__main__":
    main()
