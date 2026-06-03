#!/usr/bin/env python3
import os, glob, re

ROOT = r'D:\github\renew'
GA_TAG = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-40ZZ28MV66"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-40ZZ28MV66');
  </script>"""

files = glob.glob(os.path.join(ROOT, "*.html"))
fixed = 0

for fp in files:
    with open(fp, 'rb') as f:
        raw = f.read()
    
    crlf = b'\r\n' in raw
    content = raw.decode('utf-8').replace('\r\n', '\n')

    if 'G-40ZZ28MV66' in content:
        continue

    # <head> または <head ...> の直後に挿入 (\b を使用して header との誤一致を防ぐ)
    new_content = re.sub(r'(<head\b[^>]*>)', r'\1\n' + GA_TAG, content, flags=re.IGNORECASE)
    
    if new_content != content:
        out = new_content.replace('\n', '\r\n') if crlf else new_content
        with open(fp, 'wb') as f:
            f.write(out.encode('utf-8'))
        fixed += 1

print(f"Added GA tag to {fixed} / {len(files)} files.")
