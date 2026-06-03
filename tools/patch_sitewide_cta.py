# -*- coding: utf-8 -*-
"""
サイト全体に以下の変更を適用:
1. ヘッダーボタン: 資料請求・お問い合わせ → 資料請求
2. final-cta ボタン: 任意テキスト → 資料請求・お問合せはこちら
3. final-cta: tel/email ブロック削除
4. フッターNAP: 「運営会社：」プレフィックス追加 + 住所を2行に分割
"""
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'tools', 'docs', '.git', '.cursor', 'postmail', 'test2'}

def walk_html():
    result = []
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        top = rel.split(os.sep)[0] if rel != '.' else ''
        if top in SKIP:
            dns.clear()
            continue
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            if f.lower().endswith('.html'):
                result.append(os.path.join(dp, f))
    return result

# 1. ヘッダーCTAボタン
HEADER_BTN_RE = re.compile(
    r'(<a\s[^>]*class="btn btn--accent site-header__cta"[^>]*>)資料請求・お問い合わせ(</a>)'
)

# 2. final-cta ボタン（テキスト部分のみ置換。既に変更済みの場合も無害）
FINAL_CTA_BTN_RE = re.compile(
    r'(<p[^>]*class="final-cta__btn"[^>]*>\s*<a[^>]*class="btn btn--accent"[^>]*href="postmail\.html"[^>]*>)'
    r'[^<]*'
    r'(</a>\s*</p>)',
    re.DOTALL
)

# 3. final-cta tel ブロック削除
FINAL_CTA_TEL_RE = re.compile(
    r'\n[ \t]*<p\s+class="final-cta__tel">.*?</p>',
    re.DOTALL
)

# 4a. NAP 社名に「運営会社：」を追加（既に追加済みはスキップ）
NAP_NAME_RE = re.compile(
    r'(<span class="site-footer__nap-name">)(?!運営会社：)(.*?)(</span>)'
)

# 4b. NAP 住所を2行に分割（「サンハイムミヤタ2F　TEL:」→「サンハイムミヤタ2F<br>\n...TEL:」）
NAP_ADDR_RE = re.compile(
    r'(サンハイムミヤタ2F)　TEL: (03-6770-6191)　(<a href="mailto:info@be-intl\.com">info@be-intl\.com</a>)'
)

html_files = walk_html()
updated = 0
change_counts = {}

for path in sorted(html_files):
    with open(path, encoding='utf-8-sig') as f:
        content = f.read()

    original = content
    changes = []

    # 1. ヘッダーボタン
    new, n = HEADER_BTN_RE.subn(r'\g<1>資料請求\g<2>', content)
    if n:
        content = new
        changes.append(f'ヘッダーボタン({n})')

    # 2. final-cta ボタンテキスト
    new, n = FINAL_CTA_BTN_RE.subn(r'\g<1>資料請求・お問合せはこちら\g<2>', content)
    if n:
        content = new
        changes.append(f'CTAボタン({n})')

    # 3. final-cta tel 削除
    new, n = FINAL_CTA_TEL_RE.subn('', content)
    if n:
        content = new
        changes.append(f'tel削除({n})')

    # 4a. NAP 社名
    new, n = NAP_NAME_RE.subn(r'\g<1>運営会社：\g<2>\g<3>', content)
    if n:
        content = new
        changes.append(f'NAP社名({n})')

    # 4b. NAP 住所分割
    new, n = NAP_ADDR_RE.subn(
        r'\g<1><br>\n          TEL: \g<2>　E-mail: \g<3>',
        content
    )
    if n:
        content = new
        changes.append(f'NAP住所({n})')

    if content != original:
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        rel = os.path.relpath(path, ROOT)
        print(f"  更新: {rel:<50}  [{', '.join(changes)}]")
        updated += 1

print(f"\n合計: {updated} ファイル更新")
