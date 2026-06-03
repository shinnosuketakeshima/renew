"""
taiken*.html に Google Fonts の preconnect + 非同期読み込みブロックを追加する。
すでに fonts.googleapis.com が含まれているページはスキップ。
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT_BLOCK = '''\
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&display=swap" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&display=swap"></noscript>'''

def patch(html):
    if 'fonts.googleapis.com' in html:
        return html, False
    # home.css の <link> の直前に挿入
    new_html = re.sub(
        r'(\s*<link rel="stylesheet" href="assets/css/home\.css">)',
        f'\n{FONT_BLOCK}\\1',
        html,
        count=1
    )
    return new_html, new_html != html

def main():
    pages = glob.glob(os.path.join(ROOT, 'taiken*.html'))
    updated = 0
    for path in sorted(pages):
        with open(path, encoding='utf-8') as f:
            html = f.read()
        new_html, changed = patch(html)
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            updated += 1
    print(f'Done: {updated}/{len(pages)} files updated.')

if __name__ == '__main__':
    main()
