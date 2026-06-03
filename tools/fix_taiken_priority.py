#!/usr/bin/env python3
"""
taiken 記事一括修正（リポジトリルートから実行）

  S-1: datePublished "YYYY-MM" → "YYYY-MM-01"
  S-2: H1 にキーワードプレフィックス追加（スリランカ/ネパール別）
  S-5: Review JSON-LD ブロック削除
  A-1: <footer role="contentinfo"> を </main> の外側に移動
"""

import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
taiken_files = sorted(glob.glob(os.path.join(ROOT, 'taiken*.html')))

# ネパール記事（body クラスで確認済み）
NEPAL_FILES = {
    'taiken9.html', 'taiken26.html', 'taiken27.html', 'taiken36.html',
    'taiken37.html', 'taiken46.html', 'taiken56.html', 'taiken69.html',
    'taiken73.html', 'taiken82.html',
}

fixed = []
errors = []

for filepath in taiken_files:
    filename = os.path.basename(filepath)

    # バイナリ読み込みで改行コードを保持
    with open(filepath, 'rb') as f:
        raw = f.read()
    uses_crlf = b'\r\n' in raw
    content = raw.decode('utf-8').replace('\r\n', '\n')
    original = content

    # ----------------------------------------------------------------
    # S-1: datePublished "YYYY-MM" → "YYYY-MM-01"
    # Article と Review の両方に存在する
    # ----------------------------------------------------------------
    content = re.sub(
        r'"datePublished":\s*"(\d{4}-\d{2})"',
        lambda m: f'"datePublished": "{m.group(1)}-01"',
        content
    )

    # ----------------------------------------------------------------
    # S-5: Review JSON-LD ブロックを丸ごと削除
    # ファイルによって前の</script>との間が \n or \n\n — {1,2} で吸収
    # ----------------------------------------------------------------
    content = re.sub(
        r'\n{1,2}  <script type="application/ld\+json">[^<]*"@type":\s*"Review".*?</script>',
        '',
        content,
        flags=re.DOTALL
    )

    # ----------------------------------------------------------------
    # S-2: H1 にキーワードプレフィックスを追加
    # 既に付いている場合はスキップ（冪等）
    # ----------------------------------------------------------------
    prefix = 'ネパール英語留学 体験談｜' if filename in NEPAL_FILES \
             else 'スリランカ語学留学 体験談｜'
    content = re.sub(
        r'(<h1 class="taiken-head__h1" id="taiken-h1">)(?!スリランカ|ネパール)',
        r'\1' + prefix,
        content
    )

    # ----------------------------------------------------------------
    # A-1: <footer role="contentinfo"> を </main> の外へ移動
    # 現状: ... <footer ...>...</footer>\n  </main>
    # 修正: ... \n  </main>\n\n  <footer ...>...</footer>
    # ----------------------------------------------------------------
    content = re.sub(
        r'\n{1,3}    (<footer class="site-footer--simple" role="contentinfo">.*?</footer>)\n  </main>',
        r'\n  </main>\n\n  \1',
        content,
        flags=re.DOTALL
    )

    if content == original:
        continue

    output = content.replace('\n', '\r\n') if uses_crlf else content
    with open(filepath, 'wb') as f:
        f.write(output.encode('utf-8'))
    fixed.append(filename)

print(f'修正済み: {len(fixed)} / {len(taiken_files)} ファイル')
if errors:
    print('エラー:', errors)
