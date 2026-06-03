# -*- coding: utf-8 -*-
"""
OGP タグ + TravelAgency JSON-LD が未追加のページに一括追加する。
canonical タグの直後に OGP ブロックを、preconnect の前か <link rel="stylesheet"> の前に挿入。
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ORG_JSONLD = '''\
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "TravelAgency",
    "@id": "https://be-intl.com/#organization",
    "name": "Beインターナショナル",
    "alternateName": "Be International",
    "url": "https://be-intl.com/",
    "image": "https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG",
    "description": "スリランカ・ネパールでのホームステイとマンツーマン英語レッスンを組み合わせたアジア語学留学。22年の運営実績。",
    "foundingDate": "2004",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "幡ヶ谷1-23-19 サンハイムミヤタ2F",
      "addressLocality": "渋谷区",
      "addressRegion": "東京都",
      "postalCode": "151-0072",
      "addressCountry": "JP"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": "35.680",
      "longitude": "139.676"
    },
    "telephone": "+81-3-6770-6191",
    "email": "info@be-intl.com",
    "contactPoint": {
      "@type": "ContactPoint",
      "telephone": "+81-3-6770-6191",
      "contactType": "customer service",
      "email": "info@be-intl.com",
      "availableLanguage": "Japanese"
    }
  }
  </script>'''

# ページ別の OGP 設定
PAGE_CONFIG = {
    'living-basics.html': {
        'og_title':       '現地生活の基礎知識（スリランカ・ネパール） | Beインターナショナル',
        'og_description': 'スリランカ・ネパールのホームステイ滞在に共通する食事・飲み水・電圧・衛生・バスルームなど出発前の基礎知識。',
        'og_image':       'https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG',
        'og_url':         'https://be-intl.com/living-basics.html',
    },
    'others.html': {
        'og_title':       'スリランカ・ネパール留学の航空券・海外保険・入国手続 | Beインターナショナル',
        'og_description': '航空券の各自手配、海外旅行保険の推奨、スリランカ・ネパールの入国手続。手配のヒントと補償の確認ポイント。',
        'og_image':       'https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG',
        'og_url':         'https://be-intl.com/others.html',
    },
    'privacy.html': {
        'og_title':       'プライバシーポリシー | Beインターナショナル',
        'og_description': 'Beインターナショナルの個人情報の取扱い。取得項目・利用目的・Cookie・開示請求など個人情報保護法に基づく表示。',
        'og_image':       'https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG',
        'og_url':         'https://be-intl.com/privacy.html',
    },
    'yakkan.html': {
        'og_title':       '留学プログラム約款 | Beインターナショナル',
        'og_description': 'Beインターナショナルのプログラム約款。申込金・キャンセル料・免責事項など、お申し込み前にご確認ください。',
        'og_image':       'https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG',
        'og_url':         'https://be-intl.com/yakkan.html',
    },
    'site-guide.html': {
        'og_title':       'サイト案内 | Beインターナショナル（スリランカ・ネパール 語学留学）',
        'og_description': 'Beインターナショナル公式サイトのページ一覧。国別案内・料金・参加者の声・FAQ・資料請求など主要ページへのリンク。',
        'og_image':       'https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG',
        'og_url':         'https://be-intl.com/site-guide.html',
    },
}

def ogp_block(cfg):
    return (
        f'  <!-- OGP / SNS -->\n'
        f'  <meta property="og:type" content="website">\n'
        f'  <meta property="og:url" content="{cfg["og_url"]}">\n'
        f'  <meta property="og:title" content="{cfg["og_title"]}">\n'
        f'  <meta property="og:description" content="{cfg["og_description"]}">\n'
        f'  <meta property="og:image" content="{cfg["og_image"]}">\n'
        f'  <meta property="og:site_name" content="Beインターナショナル">\n'
        f'  <meta name="twitter:card" content="summary_large_image">'
    )

def patch_page(fname, cfg):
    path = os.path.join(ROOT, fname)
    with open(path, encoding='utf-8-sig') as f:
        html = f.read()

    ops = []

    # 1. OGP 追加（og:type がなければ canonical の後ろに挿入）
    if 'og:type' not in html:
        canonical_re = re.compile(r'(<link rel="canonical"[^>]+>)')
        new_html = canonical_re.sub(
            r'\1\n' + ogp_block(cfg),
            html, count=1
        )
        if new_html != html:
            html = new_html
            ops.append('OGP')

    # 2. TravelAgency JSON-LD 追加（既存の薄い Organization を置換、またはなければ </head> 前に追加）
    if 'TravelAgency' not in html:
        old_org = re.search(
            r'\s*<script type="application/ld\+json">\s*\{[^}]*"@type"\s*:\s*"Organization"[^}]*\}\s*</script>',
            html, re.DOTALL
        )
        if old_org:
            html = html[:old_org.start()] + '\n' + ORG_JSONLD + html[old_org.end():]
            ops.append('JSON-LD(replaced)')
        else:
            html = html.replace('</head>', ORG_JSONLD + '\n</head>', 1)
            ops.append('JSON-LD(added)')

    if ops:
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(html)
        print(f'  {fname}: {", ".join(ops)}')
    else:
        print(f'  {fname}: no change')

def main():
    for fname, cfg in PAGE_CONFIG.items():
        patch_page(fname, cfg)
    print('\nDone.')

if __name__ == '__main__':
    main()
