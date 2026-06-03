"""
home.css を参照しているが fonts.googleapis.com がないページに
preconnect + 非同期フォント読み込みを追加する。
taiken*.html は別スクリプト対象のため除外。
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT_BLOCK = (
    '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=Noto+Sans+JP:wght@400;500;600;700&display=swap" media="print" onload="this.media=\'all\'">\n'
    '  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=Noto+Sans+JP:wght@400;500;600;700&display=swap"></noscript>'
)

# home.css の link の直前に挿入（rel/href どちらの順でも対応）
CSS_RE = re.compile(
    r'(\s*<link\b[^>]*\bhref="assets/css/home\.css"[^>]*>)',
    re.IGNORECASE
)

def patch(html):
    if 'fonts.googleapis.com' in html:
        return html, False
    if 'home.css' not in html:
        return html, False
    new_html = CSS_RE.sub(f'\n{FONT_BLOCK}\\1', html, count=1)
    return new_html, new_html != html

def main():
    pages = [p for p in glob.glob(os.path.join(ROOT, '*.html'))
             if not os.path.basename(p).startswith('taiken')]
    updated = 0
    for path in sorted(pages):
        with open(path, encoding='utf-8') as f:
            html = f.read()
        new_html, changed = patch(html)
        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f'  {os.path.basename(path)}: fonts added')
            updated += 1
    print(f'\nDone: {updated} files updated.')

if __name__ == '__main__':
    main()
