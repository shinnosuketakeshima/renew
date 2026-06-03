"""
taiken*.html の <img> タグに width/height 属性を一括追加するスクリプト。
画像の実寸を struct で読み取り（Pillow不要）、
すでに width/height がある img はスキップする。
"""
import glob, os, re, struct, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_image_size(path):
    """JPEG/PNG/GIF の width,height を返す。失敗時は None,None。"""
    try:
        with open(path, 'rb') as f:
            sig = f.read(4)
        # PNG
        if sig[:4] == b'\x89PNG':
            with open(path, 'rb') as f:
                f.seek(16)
                w = struct.unpack('>I', f.read(4))[0]
                h = struct.unpack('>I', f.read(4))[0]
            return w, h
        # GIF
        if sig[:3] == b'GIF':
            with open(path, 'rb') as f:
                f.seek(6)
                w, h = struct.unpack('<HH', f.read(4))
            return w, h
        # JPEG
        if sig[:2] == b'\xff\xd8':
            with open(path, 'rb') as f:
                f.read(2)
                while True:
                    marker, = struct.unpack('>H', f.read(2))
                    if marker in (0xFFC0, 0xFFC1, 0xFFC2):
                        f.read(3)
                        h = struct.unpack('>H', f.read(2))[0]
                        w = struct.unpack('>H', f.read(2))[0]
                        return w, h
                    length, = struct.unpack('>H', f.read(2))
                    f.seek(length - 2, 1)
    except Exception:
        pass
    return None, None

IMG_RE = re.compile(r'<img\b([^>]*?)(/?)>', re.DOTALL)

def add_dimensions(html, html_dir):
    changed = 0
    def replace(m):
        nonlocal changed
        attrs = m.group(1)
        close = m.group(2)
        # すでに両方ある → スキップ
        if re.search(r'\bwidth=', attrs) and re.search(r'\bheight=', attrs):
            return m.group(0)
        src_m = re.search(r'\bsrc="([^"]+)"', attrs)
        if not src_m:
            return m.group(0)
        src = src_m.group(1)
        # 外部URL はスキップ
        if src.startswith(('http://', 'https://', '//')):
            return m.group(0)
        img_path = os.path.normpath(os.path.join(html_dir, src))
        if not os.path.exists(img_path):
            img_path = os.path.normpath(os.path.join(ROOT, src))
        if not os.path.exists(img_path):
            return m.group(0)
        w, h = get_image_size(img_path)
        if not w:
            return m.group(0)
        # width/height を src の直後に挿入
        new_attrs = re.sub(
            r'(\bsrc="[^"]+"\s*)',
            rf'\1width="{w}" height="{h}" ',
            attrs, count=1
        )
        changed += 1
        return f'<img{new_attrs}{close}>'
    result = IMG_RE.sub(replace, html)
    return result, changed

def main():
    pages = glob.glob(os.path.join(ROOT, 'taiken*.html'))
    total_changed = 0
    files_changed = 0
    for path in sorted(pages):
        with open(path, encoding='utf-8') as f:
            html = f.read()
        new_html, n = add_dimensions(html, os.path.dirname(path))
        if n > 0:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f'  {os.path.basename(path)}: +{n} width/height')
            total_changed += n
            files_changed += 1
    print(f'\nDone: {files_changed} files updated, {total_changed} img tags fixed.')

if __name__ == '__main__':
    main()
