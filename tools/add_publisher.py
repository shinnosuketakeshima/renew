#!/usr/bin/env python3
import os, re, glob

ROOT = r'D:\github\renew'
files = sorted(glob.glob(os.path.join(ROOT, 'taiken*.html')))
PUBLISHER_LINE = '    "publisher": {"@id": "https://be-intl.com/#organization"},'
fixed = 0

for fp in files:
    with open(fp, 'rb') as f:
        raw = f.read()
    crlf = b'\r\n' in raw
    c = raw.decode('utf-8').replace('\r\n', '\n')

    if '"publisher"' in c:
        continue  # 冪等: 既に追加済みならスキップ

    # "author": { ... } の閉じ } の直後に publisher を挿入
    new_c = re.sub(
        r'("author":\s*\{[^}]+\})',
        r'\1,\n' + PUBLISHER_LINE,
        c
    )
    if new_c != c:
        out = new_c.replace('\n', '\r\n') if crlf else new_c
        with open(fp, 'wb') as f:
            f.write(out.encode('utf-8'))
        fixed += 1

print(f'publisher 追加: {fixed} / {len(files)} ファイル')
