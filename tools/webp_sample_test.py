# -*- coding: utf-8 -*-
"""
WebP サンプル変換スクリプト（承認前テスト用）。
quality=90 / quality=95 / lossless の3パターンで変換し、
ファイルサイズを比較する。出力は tools/webp_samples/ へ。
EXIFデータを保持する。
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, 'tools', 'webp_samples')
os.makedirs(OUT, exist_ok=True)

SAMPLES = [
    r'SriLankaPhotos\CoconutP1011106.JPG',
    r'SriLankaPhotos\sibasama.jpg',
    r'assets\images\country-nepal.jpg',
    r'kanekosama1.jpg',
    r'shimizusama4.jpg',
    r'fujiwarasama1.jpg',
    r'manel.jpg',
]

MODES = [
    ('q90',      dict(quality=90,  lossless=False, method=6)),
    ('q95',      dict(quality=95,  lossless=False, method=6)),
    ('lossless', dict(quality=100, lossless=True,  method=6)),
]

def kb(path):
    return round(os.path.getsize(path) / 1024, 1)

def convert(src_path, mode_name, kwargs):
    stem = os.path.splitext(os.path.basename(src_path))[0]
    out  = os.path.join(OUT, f'{stem}__{mode_name}.webp')
    img  = Image.open(src_path)

    # EXIF 保持
    exif = img.info.get('exif', b'')

    # RGBA は WebP 対応だが、P(パレット)・1 は RGB 変換が必要
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    save_kwargs = dict(**kwargs)
    if exif:
        save_kwargs['exif'] = exif

    img.save(out, 'WEBP', **save_kwargs)
    img.close()
    return out

print(f"\n{'ファイル':<28} {'元JPG':>9} | {'q90':>8} {'削減%':>6} | {'q95':>8} {'削減%':>6} | {'lossless':>9} {'削減%':>6}")
print("-" * 95)

for rel in SAMPLES:
    src = os.path.join(ROOT, rel)
    if not os.path.exists(src):
        print(f"  SKIP: {rel}")
        continue

    orig_kb = kb(src)
    row = [os.path.basename(rel)[:27], f'{orig_kb:>8.1f}K']

    for mode_name, kwargs in MODES:
        out_path = convert(src, mode_name, kwargs)
        out_kb   = kb(out_path)
        ratio    = round((1 - out_kb / orig_kb) * 100, 1)
        row += [f'{out_kb:>8.1f}K', f'{ratio:>+5.1f}%']

    print(' | '.join(row))

print(f"\n変換ファイルの保存先: {OUT}")
