import urllib.request
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

url = 'http://127.0.0.1:5000/api/admin/breweries?limit=5'
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as res:
    data = json.loads(res.read().decode('utf-8'))
    print("API Response Total:", data.get('total'))
    for b in data.get('breweries', []):
        print(f"  [{b['id']}] {b['name']} ({b.get('prefecture')})")
        print(f"      創業: {b.get('founded_year')}年 ({b.get('founded_era')}) / 水質: {b.get('water_hardness_type')}")
        print(f"      TEL: {b.get('phone')} / 代表者: {b.get('president_name')} / 杜氏: {b.get('toji_name')}")
        print(f"      HP: {b.get('website')} / EC: {b.get('official_ec_url')}")
