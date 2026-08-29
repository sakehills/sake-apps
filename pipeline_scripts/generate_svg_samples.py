import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "static", "sample_svgs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_PRODUCTS = [
    {"name": "風の森 ALPHA 1", "brewery": "油長酒造", "pref": "奈良県", "cat": "純米酒", "alc": "12%", "polish": "65%", "color": "#1a365d", "gold": "#d4af37", "bg": "#f7fafc"},
    {"name": "十四代 双虹", "brewery": "高木酒造", "pref": "山形県", "cat": "大吟醸酒", "alc": "16%", "polish": "35%", "color": "#742a2a", "gold": "#e2b714", "bg": "#fffaf0"},
    {"name": "獺祭 磨き二割三分", "brewery": "旭酒造", "pref": "山口県", "cat": "純米大吟醸酒", "alc": "16%", "polish": "23%", "color": "#1a202c", "gold": "#c69214", "bg": "#ffffff"},
    {"name": "黒龍 二左衛門", "brewery": "黒龍酒造", "pref": "福井県", "cat": "純米大吟醸酒", "alc": "16%", "polish": "35%", "color": "#2d3748", "gold": "#ecc94b", "bg": "#1a202c"},
    {"name": "AKABU 魂ノ刻", "brewery": "赤武酒造", "pref": "岩手県", "cat": "純米大吟醸酒", "alc": "15%", "polish": "35%", "color": "#9b2c2c", "gold": "#ecc94b", "bg": "#2d3748"},
    {"name": "鍋島 大吟醸 雫茶", "brewery": "富久千代酒造", "pref": "佐賀県", "cat": "大吟醸酒", "alc": "16%", "polish": "35%", "color": "#22543d", "gold": "#d69e2e", "bg": "#f0fff4"},
    {"name": "飛露喜 特別純米", "brewery": "廣木酒造本店", "pref": "福島県", "cat": "特別純米酒", "alc": "16%", "polish": "55%", "color": "#2c5282", "gold": "#dd6b20", "bg": "#ebf8ff"},
    {"name": "酔鯨 DAITO 2025", "brewery": "酔鯨酒造", "pref": "高知県", "cat": "純米大吟醸酒", "alc": "16%", "polish": "30%", "color": "#171923", "gold": "#d4af37", "bg": "#0f172a"},
    {"name": "千代むすび 強力40", "brewery": "千代むすび酒造", "pref": "鳥取県", "cat": "純米大吟醸酒", "alc": "16%", "polish": "40%", "color": "#2b6cb0", "gold": "#ecc94b", "bg": "#f7fafc"},
    {"name": "さつま白若潮 25度", "brewery": "若潮酒造", "pref": "鹿児島県", "cat": "本格焼酎", "alc": "25%", "polish": "非公開", "color": "#702459", "gold": "#ecc94b", "bg": "#faf5ff"}
]

for idx, p in enumerate(SAMPLE_PRODUCTS, 1):
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="100%" height="100%">
  <defs>
    <!-- 背景グラデーション -->
    <radialGradient id="bgGrad{idx}" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="{p['bg']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0a0e17" stop-opacity="1"/>
    </radialGradient>
    
    <!-- 瓶ガラスグラデーション -->
    <linearGradient id="bottleGrad{idx}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.95"/>
      <stop offset="25%" stop-color="#334155" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#1e293b" stop-opacity="0.9"/>
      <stop offset="75%" stop-color="{p['color']}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#020617" stop-opacity="0.98"/>
    </linearGradient>

    <!-- 和紙ラベルのテクスチャ -->
    <linearGradient id="labelGrad{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fdfbf7"/>
      <stop offset="100%" stop-color="#f3ede2"/>
    </linearGradient>

    <!-- 金箔グラデーション -->
    <linearGradient id="goldGrad{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f6e05e"/>
      <stop offset="50%" stop-color="{p['gold']}"/>
      <stop offset="100%" stop-color="#975a16"/>
    </linearGradient>

    <!-- 影効果 -->
    <filter id="dropShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="12" stdDeviation="15" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- カード背景 -->
  <rect width="400" height="600" rx="16" fill="url(#bgGrad{idx})"/>

  <!-- 背景の和風装飾サークル -->
  <circle cx="200" cy="300" r="150" fill="none" stroke="{p['gold']}" stroke-width="1.5" stroke-dasharray="4 6" opacity="0.4"/>
  <circle cx="200" cy="300" r="165" fill="none" stroke="{p['color']}" stroke-width="0.8" opacity="0.3"/>

  <!-- ボトルシルエット本体 -->
  <g filter="url(#dropShadow)">
    <!-- 瓶首 -->
    <path d="M 182 80 L 218 80 L 220 170 C 220 190 260 215 265 260 L 265 510 C 265 525 250 535 235 535 L 165 535 C 150 535 135 525 135 510 L 135 260 C 140 215 180 190 180 170 Z" fill="url(#bottleGrad{idx})"/>
    
    <!-- 瓶口・キャップ封印 -->
    <rect x="180" y="65" width="40" height="20" rx="3" fill="url(#goldGrad{idx})"/>
    <path d="M 180 85 L 220 85 L 216 115 L 184 115 Z" fill="{p['color']}" opacity="0.9"/>
    <!-- 水引 / 封印紐 -->
    <line x1="178" y1="100" x2="222" y2="100" stroke="url(#goldGrad{idx})" stroke-width="2"/>

    <!-- 和紙調メインラベル -->
    <rect x="145" y="240" width="110" height="220" rx="4" fill="url(#labelGrad{idx})" stroke="#d7ccc8" stroke-width="0.8"/>

    <!-- ラベル内部デザイン -->
    <rect x="149" y="244" width="102" height="212" rx="2" fill="none" stroke="{p['gold']}" stroke-width="0.75" opacity="0.7"/>

    <!-- 落款（蔵元印） -->
    <rect x="185" y="252" width="30" height="30" rx="3" fill="#c53030"/>
    <text x="200" y="272" font-family="'Noto Serif JP', serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">極上</text>

    <!-- 特定名称バッジ -->
    <text x="200" y="302" font-family="'Noto Sans JP', sans-serif" font-size="10" font-weight="600" letter-spacing="3" fill="{p['color']}" text-anchor="middle">【 {p['cat']} 】</text>

    <!-- 銘柄名（縦書きタイポグラフィ） -->
    <text x="200" y="340" font-family="'Yu Mincho', 'Noto Serif JP', serif" font-size="18" font-weight="bold" letter-spacing="4" fill="#1a202c" text-anchor="middle">{p['name'].split()[0]}</text>
    <text x="200" y="368" font-family="'Yu Mincho', 'Noto Serif JP', serif" font-size="13" font-weight="600" letter-spacing="2" fill="#4a5568" text-anchor="middle">{' '.join(p['name'].split()[1:])}</text>

    <!-- スペック（精米歩合・度数） -->
    <text x="200" y="405" font-family="'Noto Sans JP', sans-serif" font-size="9" fill="#718096" text-anchor="middle">精米歩合 {p['polish']} / Alc {p['alc']}</text>

    <!-- 蔵元名 -->
    <text x="200" y="435" font-family="'Noto Serif JP', serif" font-size="10" font-weight="bold" letter-spacing="2" fill="{p['color']}" text-anchor="middle">{p['brewery']}</text>
    <text x="200" y="448" font-family="'Noto Sans JP', sans-serif" font-size="8" fill="#a0aec0" text-anchor="middle">{p['pref']}</text>
  </g>

  <!-- カード下部製品名バナー -->
  <rect x="25" y="545" width="350" height="42" rx="8" fill="#0f172a" opacity="0.85" stroke="{p['gold']}" stroke-width="0.5"/>
  <text x="40" y="571" font-family="'Noto Sans JP', sans-serif" font-size="13" font-weight="bold" fill="#ffffff">{p['name']}</text>
  <text x="360" y="571" font-family="'Noto Sans JP', sans-serif" font-size="11" font-weight="600" fill="url(#goldGrad{idx})" text-anchor="end">{p['cat']}</text>
</svg>'''

    filepath = os.path.join(OUTPUT_DIR, f"sample_{idx}_{p['name'].split()[0]}.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✨ [SVGラベル生成] {filepath}")

print("\n🎉 10種類の動的SVGプレミアム和風ラベルサンプルが生成されました。")
