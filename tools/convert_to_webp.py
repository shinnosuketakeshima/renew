# -*- coding: utf-8 -*-
"""
WebP batch conversion + HTML src= update.

Phase 1: Walk the repo, convert every JPEG to WebP q90.
         If WebP is LARGER than original, delete it and skip.
Phase 2: Update src= in every HTML <img> to .webp path.
         OGP og:image and JSON-LD "image" are intentionally left as JPG
         (social-media / search-engine crawler compatibility).
"""
import os, re, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'tools', 'docs', '.git', '.cursor', 'postmail'}


def walk(exts):
    out = []
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        top = rel.split(os.sep)[0] if rel != '.' else ''
        if top in SKIP:
            dns.clear()
            continue
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            if os.path.splitext(f)[1].lower() in exts:
                out.append(os.path.join(dp, f))
    return out


def kb(p):
    return os.path.getsize(p) / 1024


def to_webp(src):
    dst = os.path.splitext(src)[0] + '.webp'
    img = Image.open(src)
    exif = img.info.get('exif', b'')
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    kw = dict(quality=90, lossless=False, method=6)
    if exif:
        kw['exif'] = exif
    img.save(dst, 'WEBP', **kw)
    img.close()
    return dst


# ── Phase 1: Convert ──────────────────────────────────────────────────────────
print("=== Phase 1: JPEG → WebP q90 変換 ===\n")
jpegs = walk({'.jpg', '.jpeg'})
print(f"対象: {len(jpegs)} ファイル\n")

pairs = []       # (src_abs, webp_abs) — converted and smaller
skip_large = skip_err = 0
saved_kb = 0.0

for src in sorted(jpegs):
    try:
        webp = to_webp(src)
        sk, wk = kb(src), kb(webp)
        if wk < sk:
            pairs.append((src, webp))
            saved_kb += sk - wk
            pct = (1 - wk / sk) * 100
            rel = os.path.relpath(src, ROOT)
            print(f"  OK  {rel:<60}  {sk:>7.0f}K -> {wk:>7.0f}K  ({pct:.1f}%)")
        else:
            os.remove(webp)
            skip_large += 1
    except Exception as e:
        skip_err += 1
        print(f"  ERR {os.path.relpath(src, ROOT)}: {e}")

print(f"\n変換: {len(pairs)} 枚  スキップ(WebP大): {skip_large} 枚  エラー: {skip_err} 枚")
print(f"削減合計: {saved_kb / 1024:.1f} MB\n")


# ── Phase 2: Update HTML ──────────────────────────────────────────────────────
print("=== Phase 2: HTML <img src> 更新 ===\n")

# rel_conv: lowercase forward-slash relative path from ROOT → webp relative path from ROOT
rel_conv = {}
for src_abs, webp_abs in pairs:
    src_rel  = os.path.relpath(src_abs,  ROOT).replace('\\', '/')
    webp_rel = os.path.relpath(webp_abs, ROOT).replace('\\', '/')
    rel_conv[src_rel.lower()] = webp_rel

# Matches src="path/to/file.jpg" or src='...' (case-insensitive extension)
IMG_SRC_RE = re.compile(r'\bsrc=(["\'])([^"\']+\.jpe?g)(\1)', re.IGNORECASE)

html_files    = walk({'.html'})
updated_total = 0

for html_path in sorted(html_files):
    html_dir     = os.path.dirname(html_path)
    html_dir_rel = os.path.relpath(html_dir, ROOT).replace('\\', '/')
    if html_dir_rel == '.':
        html_dir_rel = ''

    with open(html_path, encoding='utf-8-sig') as f:
        content = f.read()

    n = [0]  # mutable counter for use inside closure

    def replacer(m, _hdr=html_dir_rel, _hd=html_dir, _n=n):
        quote = m.group(1)
        path  = m.group(2)
        # Resolve to a path relative to ROOT
        base = (_hdr + '/' + path) if _hdr else path
        norm = os.path.normpath(base).replace('\\', '/').lower()
        if norm in rel_conv:
            webp_root_rel = rel_conv[norm]
            webp_abs_path = os.path.join(ROOT, webp_root_rel.replace('/', os.sep))
            rel_to_html   = os.path.relpath(webp_abs_path, _hd).replace('\\', '/')
            _n[0] += 1
            return f'src={quote}{rel_to_html}{quote}'
        return m.group(0)

    new_content = IMG_SRC_RE.sub(replacer, content)

    if n[0] > 0:
        with open(html_path, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        rel = os.path.relpath(html_path, ROOT)
        print(f"  更新: {rel}  ({n[0]}箇所)")
        updated_total += 1

print(f"\nHTML更新完了: {updated_total} ファイル")
print("=== 完了 ===")
