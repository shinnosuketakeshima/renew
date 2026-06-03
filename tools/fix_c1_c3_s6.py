#!/usr/bin/env python3
"""
C-1: ヒーロー画像 preload/src を WebP に更新（index / srilanka / nepal）
C-3: 全本番 HTML の CSS href に ?v=20260603 を付与（統一バージョニング）
S-6: program.html に料金 Service/Offer 構造化データを追加
リポジトリルートから実行: python tools/fix_c1_c3_s6.py
"""

import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER  = '20260603'

# 本番にアップしないディレクトリ
SKIP_DIRS = {'docs', 'tools', '.git', '.cursor', 'postmail', 'node_modules'}


def load(path):
    with open(path, 'rb') as f:
        raw = f.read()
    crlf = b'\r\n' in raw
    return raw.decode('utf-8').replace('\r\n', '\n'), crlf


def save(path, content, crlf):
    out = content.replace('\n', '\r\n') if crlf else content
    with open(path, 'wb') as f:
        f.write(out.encode('utf-8'))


# ============================================================
# C-1 ヒーロー preload + img src → WebP
# ============================================================

# index.html: preload + img src 両方更新
index_path = os.path.join(ROOT, 'index.html')
c, crlf = load(index_path)
orig = c

# preload: .JPG → .webp + type 追加
c = re.sub(
    r'(<link rel="preload" as="image" href=")(SriLankaPhotos/CoconutP1011106)\.JPG(")',
    r'\1\2.webp\3 type="image/webp"',
    c
)
# img src: .JPG → .webp
c = c.replace(
    'src="SriLankaPhotos/CoconutP1011106.JPG"',
    'src="SriLankaPhotos/CoconutP1011106.webp"'
)
if c != orig:
    save(index_path, c, crlf)
    print('C-1 index.html: preload + img src → WebP')

# srilanka.html: preload が .jpg を指しているが img は既に .webp
sl_path = os.path.join(ROOT, 'srilanka.html')
c, crlf = load(sl_path)
orig = c
c = re.sub(
    r'(<link rel="preload" as="image" href=")(SriLankaPhotos/sibasama)\.(?:jpg|JPG)(")',
    r'\1\2.webp\3 type="image/webp"',
    c
)
if c != orig:
    save(sl_path, c, crlf)
    print('C-1 srilanka.html: preload → WebP')
else:
    print('C-1 srilanka.html: 変更なし（既に対応済みか）')

# nepal.html: preload が .jpg を指しているが img は既に .webp
np_path = os.path.join(ROOT, 'nepal.html')
c, crlf = load(np_path)
orig = c
c = re.sub(
    r'(<link rel="preload" as="image" href=")(assets/images/country-nepal)\.(?:jpg|JPG)(")',
    r'\1\2.webp\3 type="image/webp"',
    c
)
if c != orig:
    save(np_path, c, crlf)
    print('C-1 nepal.html: preload → WebP')
else:
    print('C-1 nepal.html: 変更なし（既に対応済みか）')


# ============================================================
# C-3 CSS href に ?v=VER を統一付与
# ============================================================

def production_html_files():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        top = rel.split(os.sep)[0] if rel != '.' else ''
        if top in SKIP_DIRS:
            dns.clear()
            continue
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn.endswith('.html'):
                out.append(os.path.join(dp, fn))
    return out

# assets/css/foo.css または assets/css/foo.css?v=... を一律 ?v=VER に統一
CSS_RE = re.compile(
    r'(href="assets/css/[^"?]+\.css)(?:\?v=[^"]*)?(")',
    re.IGNORECASE
)

c3_fixed = 0
for fpath in production_html_files():
    c, crlf = load(fpath)
    new_c = CSS_RE.sub(rf'\1?v={VER}\2', c)
    if new_c != c:
        save(fpath, new_c, crlf)
        c3_fixed += 1

print(f'C-3 CSS バージョン統一: {c3_fixed} ファイルを ?v={VER} に更新')


# ============================================================
# S-6 program.html に Service/Offer 価格スキーマを追加
# ============================================================

SL_OFFERS = [
    ('スリランカ語学留学 7日間コース',   '92000',   '個人レッスン20時間・ホームステイ6泊7日・全食事付き'),
    ('スリランカ語学留学 15日間コース',  '164500',  '個人レッスン44時間・ホームステイ14泊15日・全食事付き'),
    ('スリランカ語学留学 30日間コース',  '269500',  '個人レッスン88時間・ホームステイ29泊30日・全食事付き'),
    ('スリランカ語学留学 45日間コース',  '353500',  '個人レッスン136時間・ホームステイ44泊45日・全食事付き'),
    ('スリランカ語学留学 2ヶ月間コース', '442000',  '個人レッスン186時間・ホームステイ59泊60日・全食事付き'),
    ('スリランカ語学留学 4ヶ月間コース', '766000',  '個人レッスン370時間・ホームステイ119泊120日・全食事付き'),
    ('スリランカ語学留学 6ヶ月間コース', '1074000', '個人レッスン564時間・ホームステイ179泊180日・全食事付き'),
]
NP_OFFERS = [
    ('ネパール語学留学 7日間コース',    '92000',   '個人レッスン20時間・ホームステイ6泊7日・全食事付き'),
    ('ネパール語学留学 12日間コース',   '136500',  '個人レッスン32時間・ホームステイ11泊12日・全食事付き'),
    ('ネパール語学留学 18日間コース',   '180500',  '個人レッスン48時間・ホームステイ17泊18日・全食事付き'),
    ('ネパール語学留学 30日間コース',   '258500',  '個人レッスン80時間・ホームステイ29泊30日・全食事付き'),
    ('ネパール語学留学 45日間コース',   '344500',  '個人レッスン120時間・ホームステイ44泊45日・全食事付き'),
    ('ネパール語学留学 2ヶ月間コース',  '431500',  '個人レッスン160時間・ホームステイ59泊60日・全食事付き'),
    ('ネパール語学留学 3ヶ月間コース',  '606000',  '個人レッスン240時間・ホームステイ89泊90日・全食事付き'),
]


def offers_json(offers, url_fragment):
    lines = []
    for i, (name, price, desc) in enumerate(offers):
        comma = ',' if i < len(offers) - 1 else ''
        lines.append(
            f'      {{\n'
            f'        "@type": "Offer",\n'
            f'        "name": "{name}",\n'
            f'        "price": "{price}",\n'
            f'        "priceCurrency": "JPY",\n'
            f'        "description": "{desc}",\n'
            f'        "url": "https://be-intl.com/program.html#{url_fragment}"\n'
            f'      }}{comma}'
        )
    return '\n'.join(lines)


price_schema = (
    '\n  <script type="application/ld+json">\n'
    '  [\n'
    '    {\n'
    '      "@context": "https://schema.org",\n'
    '      "@type": "Service",\n'
    '      "name": "スリランカ語学留学プログラム（ホームステイ＋個人レッスン）",\n'
    '      "description": "スリランカでの全コース個人レッスンとホームステイを組み合わせた語学留学。英語が公用語の環境で、リゾートエリアに滞在。",\n'
    '      "provider": { "@id": "https://be-intl.com/#organization" },\n'
    '      "url": "https://be-intl.com/program.html#srilanka",\n'
    '      "areaServed": { "@type": "Country", "name": "Sri Lanka" },\n'
    '      "offers": [\n'
    + offers_json(SL_OFFERS, 'srilanka') + '\n'
    '      ]\n'
    '    },\n'
    '    {\n'
    '      "@context": "https://schema.org",\n'
    '      "@type": "Service",\n'
    '      "name": "ネパール語学留学プログラム（ホームステイ＋個人レッスン）",\n'
    '      "description": "ネパール・カトマンズでの全コース個人レッスンとホームステイを組み合わせた語学留学。ヒマラヤの麓で異文化体験とボランティア活動も可能。",\n'
    '      "provider": { "@id": "https://be-intl.com/#organization" },\n'
    '      "url": "https://be-intl.com/program.html#nepal",\n'
    '      "areaServed": { "@type": "Country", "name": "Nepal" },\n'
    '      "offers": [\n'
    + offers_json(NP_OFFERS, 'nepal') + '\n'
    '      ]\n'
    '    }\n'
    '  ]\n'
    '  </script>'
)

prog_path = os.path.join(ROOT, 'program.html')
c, crlf = load(prog_path)

if '"@type": "Service"' in c:
    print('S-6 program.html: Service スキーマ既存のためスキップ')
else:
    # 最後の </script> の直後（</head> の直前）に挿入
    c = c.replace('\n</head>', price_schema + '\n</head>', 1)
    save(prog_path, c, crlf)
    print('S-6 program.html: Service/Offer 価格スキーマを追加')
