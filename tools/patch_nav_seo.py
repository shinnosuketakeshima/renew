# -*- coding: utf-8 -*-
"""
SEO/GEO ナビゲーション最適化スクリプト:
  1. パンくずリスト HTML をサブページに追加
  2. フッターに NAP ブロックを追加
  3. CTA アンカーテキストをページ別に具体化
  4. recomend.html に JSON-LD / OGP / robots meta を追加
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 設定 ----------

NAP_BLOCK = '''\
        <address class="site-footer__nap">
          <span class="site-footer__nap-name">Beインターナショナル（Be International）</span>
          〒151-0072 東京都渋谷区幡ヶ谷1-23-19 サンハイムミヤタ2F　TEL: 03-6770-6191　<a href="mailto:info@be-intl.com">info@be-intl.com</a>
        </address>'''

# ページ別のパンくず設定 (file, label, url)
BREADCRUMBS = {
    'srilanka.html':      ('スリランカ語学留学',       'https://be-intl.com/srilanka.html'),
    'nepal.html':         ('ネパール語学留学',          'https://be-intl.com/nepal.html'),
    'program.html':       ('料金・コース',              'https://be-intl.com/program.html'),
    'voices.html':        ('参加者の声',                'https://be-intl.com/voices.html'),
    'faq.html':           ('よくある質問',              'https://be-intl.com/faq.html'),
    'postmail.html':      ('資料請求・お問い合わせ',    'https://be-intl.com/postmail.html'),
    'volunteer.html':     ('ネパールボランティア',       'https://be-intl.com/volunteer.html'),
    'about.html':         ('会社概要',                  'https://be-intl.com/about.html'),
    'process1.html':      ('出発までの流れ',             'https://be-intl.com/process1.html'),
    'living-basics.html': ('現地生活の基礎知識',        'https://be-intl.com/living-basics.html'),
    'others.html':        ('航空券・保険・入国手続',     'https://be-intl.com/others.html'),
    'privacy.html':       ('プライバシーポリシー',       'https://be-intl.com/privacy.html'),
    'yakkan.html':        ('約款',                      'https://be-intl.com/yakkan.html'),
    'site-guide.html':    ('サイト案内',                'https://be-intl.com/site-guide.html'),
    'recomend.html':      ('推薦・メディア',             'https://be-intl.com/recomend.html'),
}

# ページ別 CTA テキスト
CTA_TEXTS = {
    'index.html':         'スリランカ・ネパール留学の資料を請求する',
    'srilanka.html':      'スリランカ語学留学の資料を請求する',
    'nepal.html':         'ネパール語学留学の資料を請求する',
    'program.html':       '料金・コースの詳細資料を請求する',
    'voices.html':        '語学留学の資料を請求する',
    'faq.html':           '語学留学の資料を請求する',
    'volunteer.html':     'ネパールボランティア留学の資料を請求する',
    'about.html':         '資料請求・お問い合わせ',
    'process1.html':      '語学留学の資料を請求する',
    'living-basics.html': '資料請求・お問い合わせ',
    'others.html':        '資料請求・お問い合わせ',
    'recomend.html':      '資料請求・お問い合わせ',
    'privacy.html':       '資料請求・お問い合わせ',
    'yakkan.html':        '資料請求・お問い合わせ',
    'site-guide.html':    '資料請求・お問い合わせ',
}

# フッターリンクの anchor テキスト強化マップ（全ページ共通）
FOOTER_LINK_MAP = {
    '>資料請求<': '>資料請求・お問い合わせ<',
    '>トップ<':   '>トップページ<',
}

# ---------- ユーティリティ ----------

def breadcrumb_html(label):
    return (
        '\n'
        '    <nav class="breadcrumb-nav" aria-label="パンくずリスト">\n'
        '      <div class="layout-container">\n'
        '        <ol class="breadcrumb-nav__list">\n'
        '          <li><a href="index.html">トップ</a></li>\n'
        f'          <li aria-current="page">{label}</li>\n'
        '        </ol>\n'
        '      </div>\n'
        '    </nav>'
    )

def insert_breadcrumb(html, label):
    """最初の </section> の直後にパンくずを挿入。"""
    if 'breadcrumb-nav' in html:
        return html, False
    idx = html.find('</section>')
    if idx < 0:
        return html, False
    end = idx + len('</section>')
    return html[:end] + breadcrumb_html(label) + html[end:], True

def add_nap_to_footer(html):
    """site-footer--simple の .layout-container 開始直後に NAP を挿入。"""
    if 'site-footer__nap' in html:
        return html, False
    # <footer class="site-footer--simple"...> の中の最初の <div class="layout-container">
    pattern = r'(<footer[^>]*site-footer--simple[^>]*>.*?<div[^>]*layout-container[^>]*>)'
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        return html, False
    end = m.end()
    return html[:end] + '\n' + NAP_BLOCK + html[end:], True

def fix_cta_text(html, new_text):
    """final-cta 内の btn--accent ボタンのテキストを置換。"""
    old = r'<a class="btn btn--accent" href="postmail\.html">資料請求・お問い合わせはこちら</a>'
    new = f'<a class="btn btn--accent" href="postmail.html">{new_text}</a>'
    new_html, n = re.subn(old, new, html)
    return new_html, n > 0

def fix_footer_links(html):
    """フッターのアンカーテキストを強化。"""
    changed = False
    for old, new in FOOTER_LINK_MAP.items():
        if old in html:
            html = html.replace(old, new)
            changed = True
    return html, changed

# ---------- recomend.html 専用: JSON-LD / OGP / robots 追加 ----------

RECOMEND_JSONLD = '''
  <meta name="robots" content="index,follow">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://be-intl.com/recomend.html">
  <meta property="og:title" content="推薦・メディア | Beインターナショナル">
  <meta property="og:description" content="専門家推薦と第三者メディア掲載。Dr.アーナンダ・クマーラ氏の推薦文と、俳優・三波豊和氏による代表インタビューをご紹介します。">
  <meta property="og:image" content="https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG">
  <meta property="og:site_name" content="Beインターナショナル">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "トップ", "item": "https://be-intl.com/" },
      { "@type": "ListItem", "position": 2, "name": "推薦・メディア", "item": "https://be-intl.com/recomend.html" }
    ]
  }
  </script>
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

def fix_recomend(html):
    """recomend.html 専用: 既存の薄い Organization JSON-LD を TravelAgency + BreadcrumbList に置換し、OGP/robots を追加。"""
    old_schema = re.search(
        r'\s*<script type="application/ld\+json">\s*\{[^}]*"@type"\s*:\s*"Organization"[^}]*\}\s*</script>',
        html, re.DOTALL
    )
    if old_schema:
        html = html[:old_schema.start()] + RECOMEND_JSONLD + html[old_schema.end():]
    return html

# ---------- メイン ----------

def process_file(fname, breadcrumb_label=None, cta_text=None):
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path):
        print(f'  SKIP (not found): {fname}')
        return

    with open(path, encoding='utf-8-sig') as f:
        html = f.read()

    ops = []

    if fname == 'recomend.html':
        html = fix_recomend(html)
        ops.append('json-ld+ogp')

    if breadcrumb_label:
        html, ok = insert_breadcrumb(html, breadcrumb_label)
        if ok:
            ops.append('breadcrumb')

    html, ok = add_nap_to_footer(html)
    if ok:
        ops.append('nap')

    if cta_text:
        html, ok = fix_cta_text(html, cta_text)
        if ok:
            ops.append(f'cta="{cta_text}"')

    html, ok = fix_footer_links(html)
    if ok:
        ops.append('footer-links')

    if ops:
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(html)
        print(f'  {fname}: {", ".join(ops)}')
    else:
        print(f'  {fname}: no change')

def main():
    # サブページ（パンくず + NAP + CTA）
    for fname, (label, _) in BREADCRUMBS.items():
        cta = CTA_TEXTS.get(fname)
        process_file(fname, breadcrumb_label=label, cta_text=cta)

    # トップページ（パンくずなし、NAP + CTA のみ）
    process_file('index.html', breadcrumb_label=None, cta_text=CTA_TEXTS.get('index.html'))

    print('\nDone.')

if __name__ == '__main__':
    main()
