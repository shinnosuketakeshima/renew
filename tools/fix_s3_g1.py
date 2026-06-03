#!/usr/bin/env python3
"""
S-3: taiken 記事に OGP / Twitter Card メタタグを追加（84記事）
G-1: voices.html の ItemList スキーマに itemListElement を追加
リポジトリルートから実行: python tools/fix_s3_g1.py
"""

import os
import re
import glob
import csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEPAL_FILES = {
    'taiken9.html', 'taiken26.html', 'taiken27.html', 'taiken36.html',
    'taiken37.html', 'taiken46.html', 'taiken56.html', 'taiken69.html',
    'taiken73.html', 'taiken82.html',
}
SL_IMAGE = 'https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG'
NP_IMAGE = 'https://be-intl.com/assets/images/country-nepal.jpg'

# ============================================================
# S-3: OGP タグを taiken 記事に追加
# ============================================================
taiken_files = sorted(glob.glob(os.path.join(ROOT, 'taiken*.html')))
s3_fixed = 0

for filepath in taiken_files:
    filename = os.path.basename(filepath)

    with open(filepath, 'rb') as f:
        raw = f.read()
    uses_crlf = b'\r\n' in raw
    content = raw.decode('utf-8').replace('\r\n', '\n')

    # 既に OGP がある場合はスキップ（冪等）
    if 'og:type' in content:
        continue

    title_m  = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    # description: 属性順序が異なる2パターンに対応
    desc_m   = (re.search(r'<meta\s+name="description"\s+content="(.*?)"', content) or
                re.search(r'<meta\s+content="(.*?)"[^>]+name="description"', content))
    # canonical: href/rel どちらが先でも対応
    canon_m  = (re.search(r'<link\s+rel="canonical"\s+href="(.*?)"', content) or
                re.search(r'<link\s+href="(.*?)"[^>]+rel="canonical"', content))
    if not (title_m and desc_m and canon_m):
        print(f'  SKIP (data missing): {filename}')
        continue

    title    = title_m.group(1).strip()
    desc     = desc_m.group(1)
    url      = canon_m.group(1)
    og_image = NP_IMAGE if filename in NEPAL_FILES else SL_IMAGE

    ogp_block = (
        '  <!-- OGP / SNS -->\n'
        f'  <meta property="og:type" content="article">\n'
        f'  <meta property="og:url" content="{url}">\n'
        f'  <meta property="og:title" content="{title}">\n'
        f'  <meta property="og:description" content="{desc}">\n'
        f'  <meta property="og:image" content="{og_image}">\n'
        f'  <meta property="og:site_name" content="Beインターナショナル">\n'
        f'  <meta name="twitter:card" content="summary_large_image">'
    )

    # canonical タグを regex で特定して直後に挿入（属性順序・自己閉じ不問）
    canon_pattern = re.compile(
        r'(<link\s+(?:rel="canonical"\s+href=|href=)[^>]+>)',
        re.IGNORECASE
    )
    content, n = canon_pattern.subn(r'\1\n' + ogp_block, content, count=1)
    if n == 0:
        print(f'  WARN (canonical tag not replaced): {filename}')
        continue

    output = content.replace('\n', '\r\n') if uses_crlf else content
    with open(filepath, 'wb') as f:
        f.write(output.encode('utf-8'))
    s3_fixed += 1

print(f'S-3 OGP追加: {s3_fixed} / {len(taiken_files)} ファイル')

# ============================================================
# G-1: voices.html の ItemList に itemListElement を追加
# ============================================================
tsv_path = os.path.join(ROOT, 'tools', 'taiken_seo_preview.tsv')
items = []
with open(tsv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for i, row in enumerate(reader, start=1):
        filename = row['filename'].strip()
        proposed = row['proposed_title'].strip()
        # "| Beインターナショナル" サフィックスを除去
        name = re.sub(r'\s*[|｜]\s*Beインターナショナル\s*$', '', proposed).strip()
        url  = f'https://be-intl.com/{filename}'
        items.append((i, url, name))

# JSON-LD 文字列生成
item_lines = []
for pos, url, name in items:
    # JSON 内の " をエスケープ
    name_safe = name.replace('"', '\\"')
    comma = ',' if pos < len(items) else ''
    item_lines.append(
        f'      {{\n'
        f'        "@type": "ListItem",\n'
        f'        "position": {pos},\n'
        f'        "url": "{url}",\n'
        f'        "name": "{name_safe}"\n'
        f'      }}{comma}'
    )

new_schema = (
    '  <script type="application/ld+json">\n'
    '  {\n'
    '    "@context": "https://schema.org",\n'
    '    "@type": "ItemList",\n'
    '    "name": "スリランカ・ネパール留学 体験談一覧",\n'
    f'    "numberOfItems": {len(items)},\n'
    '    "itemListElement": [\n'
    + '\n'.join(item_lines) + '\n'
    '    ]\n'
    '  }\n'
    '  </script>'
)

voices_path = os.path.join(ROOT, 'voices.html')
with open(voices_path, 'rb') as f:
    raw = f.read()
uses_crlf = b'\r\n' in raw
content = raw.decode('utf-8').replace('\r\n', '\n')

old_schema = re.search(
    r'  <script type="application/ld\+json">\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"ItemList".*?</script>',
    content,
    re.DOTALL
)
if old_schema:
    content = content[:old_schema.start()] + new_schema + content[old_schema.end():]
    output = content.replace('\n', '\r\n') if uses_crlf else content
    with open(voices_path, 'wb') as f:
        f.write(output.encode('utf-8'))
    print(f'G-1 ItemList更新: voices.html ({len(items)}件のitemListElement)')
else:
    print('G-1 SKIP: ItemListブロックが見つかりませんでした')
