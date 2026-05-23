"""Compare taiken39+ pages to docs/oldHP for truncated body text and portrait crop risk."""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = 39
END = 84
TEXT_RATIO_WARN = 0.75


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        t = data.strip()
        if t:
            self.parts.append(t)


def extract_text(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S | re.I)
    p = TextExtractor()
    p.feed(html)
    return "".join(p.parts)


def new_article_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<article[^>]*>(.*?)</article>", raw, re.S | re.I)
    chunk = m.group(1) if m else raw
    return extract_text(chunk)


def old_article_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    idx = raw.find("スリランカ：")
    if idx < 0:
        idx = raw.find("ネパール：")
    if idx < 0:
        return new_article_text(path)
    sub = raw[idx:]
    up = sub.find("#up")
    if up > 0:
        sub = sub[:up]
    return extract_text(sub)


def portrait_srcs(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    out: list[str] = []
    for tag in re.findall(r"<img[^>]+>", raw, re.I):
        wm = re.search(r'width=["\']?(\d+)', tag, re.I)
        hm = re.search(r'height=["\']?(\d+)', tag, re.I)
        if not (wm and hm):
            continue
        w, h = int(wm.group(1)), int(hm.group(1))
        if h <= w:
            continue
        sm = re.search(r'src=["\']([^"\']+)', tag, re.I)
        out.append(sm.group(1) if sm else "?")
    return out


def article_portrait_srcs(path: Path) -> list[str]:
    """Portrait participant photos in old article body (exclude site chrome under images/)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    idx = raw.find("スリランカ：")
    if idx < 0:
        idx = raw.find("ネパール：")
    if idx < 0:
        return []
    sub = raw[idx:]
    up = sub.find("#up")
    if up > 0:
        sub = sub[:up]
    out: list[str] = []
    sub = re.sub(r"<!--.*?-->", "", sub, flags=re.S)
    for tag in re.findall(r"<img[^>]+>", sub, re.I):
        sm = re.search(r'src=["\']([^"\']+)', tag, re.I)
        src = sm.group(1) if sm else ""
        if not src or src.startswith("images/") or "spacer" in src.lower():
            continue
        wm = re.search(r'width=["\']?(\d+)', tag, re.I)
        hm = re.search(r'height=["\']?(\d+)', tag, re.I)
        if not (wm and hm):
            continue
        if int(hm.group(1)) <= int(wm.group(1)):
            continue
        out.append(src)
    return out


def main() -> int:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else START
    end = int(sys.argv[2]) if len(sys.argv) > 2 else END
    flagged: list[tuple] = []
    print("num\tflags\tnew_len\told_len\tnotes")
    for n in range(start, end + 1):
        fn = f"taiken{n}.html"
        new_p = ROOT / fn
        old_p = ROOT / "docs" / "oldHP" / fn
        if not new_p.is_file():
            continue
        if not old_p.is_file():
            print(f"{n}\tno_old\t-\t-\t-")
            continue
        nt = new_article_text(new_p)
        ot = old_article_text(old_p)
        ratio = len(nt) / len(ot) if ot else 1.0
        raw = new_p.read_text(encoding="utf-8", errors="replace")
        blocks = "taiken-article__blocks" in raw
        natural = "page-taiken-blocks-natural" in raw
        old_portraits = article_portrait_srcs(old_p) if blocks else []
        crop_risk = blocks and old_portraits and not natural
        flags: list[str] = []
        notes: list[str] = []
        if ratio < TEXT_RATIO_WARN:
            flags.append(f"text_{ratio:.0%}")
        if crop_risk:
            flags.append(f"crop_risk:{len(old_portraits)}")
            notes.append(",".join(old_portraits[:3]))
        if not flags:
            continue
        flagged.append((n, flags, len(nt), len(ot), notes))
        print(f"{n}\t{','.join(flags)}\t{len(nt)}\t{len(ot)}\t{notes}")
    print(f"--- flagged: {len(flagged)} / {end - start + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
