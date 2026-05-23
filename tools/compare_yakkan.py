# -*- coding: utf-8 -*-
"""Compare yakkan.html legal body with docs/oldHP/yakkan.html."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def extract_legal_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if "legal-article" in raw:
        m = re.search(r'<article class="legal-article"[^>]*>(.*?)</article>', raw, re.S)
        chunk = m.group(1) if m else raw
    else:
        idx = raw.find("第1条")
        chunk = raw[idx:] if idx >= 0 else raw
        chunk = re.sub(r'<a name="[^"]+"></a>', "", chunk)
        chunk = re.sub(r'<a href="#up">.*?</a>', "", chunk, flags=re.S)
    chunk = re.sub(r"<br\s*/?>", "\n", chunk, flags=re.I)
    chunk = re.sub(r"<[^>]+>", "", chunk)
    chunk = chunk.replace("&nbsp;", " ")
    text = re.sub(r"[ \t]+", " ", chunk)
    text = re.sub(r"\n+", "\n", text)
    text = text.replace("｡", "。").replace("･", "・")
    text = re.sub(r"^お申し込みの前に.*?\n", "", text)
    return text.strip()


def normalize(s: str) -> str:
    s = re.sub(r"（(\d+)）", r"(\1)", s)
    s = re.sub(r"(\d+)．", r"\1.", s)
    s = re.sub(r"\s+", "", s)
    return s


def split_articles(text: str) -> dict[int, str]:
    matches = list(re.finditer(r"第(\d+)条", text))
    out: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[num] = text[start:end]
    return {k: normalize(v) for k, v in out.items()}


def strip_list_numbers(s: str) -> str:
    """Remove enum prefixes so <ol> vs 1． does not false-positive."""
    s = re.sub(r"(?<=[。B])第\d+条", "第X条", s)  # noop guard
    s = re.sub(r"^(\d+)[\.．]", "", s)
    s = re.sub(r"\((\d+)\)", r"(\1)", s)
    return s


def content_only_norm(s: str) -> str:
    s = normalize(s)
    s = re.sub(r"\d+[\.．]", "", s)
    return s


def main() -> int:
    old_p = ROOT / "docs" / "oldHP" / "yakkan.html"
    new_p = ROOT / "yakkan.html"
    old = extract_legal_text(old_p)
    new = extract_legal_text(new_p)
    no, nn = normalize(old), normalize(new)
    print(f"old length: {len(no)}")
    print(f"new length: {len(nn)}")
    print(f"normalized identical: {no == nn}")
    if no != nn:
        for i, (a, b) in enumerate(zip(no, nn)):
            if a != b:
                print(f"\nfirst char diff at {i}:")
                print(f"  old: ...{no[max(0, i - 50) : i + 50]}...")
                print(f"  new: ...{nn[max(0, i - 50) : i + 50]}...")
                break
        if len(no) != len(nn):
            print(f"length delta: {len(nn) - len(no)}")
        old_art = split_articles(old)
        new_art = split_articles(new)
        print("\nPer-article (content-normalized, no list numbers):")
        for n in range(1, 18):
            ok = content_only_norm(old_art.get(n, ""))
            nk = content_only_norm(new_art.get(n, ""))
            status = "OK" if ok == nk else "DIFF"
            if status == "DIFF":
                print(f"  第{n}条: {status} old={len(ok)} new={len(nk)}")
                if ok and nk:
                    for i, (a, b) in enumerate(zip(ok, nk)):
                        if a != b:
                            print(f"    first diff: old ...{ok[max(0,i-30):i+30]}...")
                            print(f"              new ...{nk[max(0,i-30):i+30]}...")
                            break
                    if len(ok) != len(nk):
                        # sentences only in one side
                        old_s = set(re.split(r"[。B]", ok))
                        new_s = set(re.split(r"[。B]", nk))
                        only_old = [s for s in old_s if s and s not in new_s and len(s) > 15]
                        only_new = [s for s in new_s if s and s not in old_s and len(s) > 15]
                        if only_old:
                            print(f"    only in old ({len(only_old)}): {only_old[0][:80]}...")
                        if only_new:
                            print(f"    only in new ({len(only_new)}): {only_new[0][:80]}...")
            else:
                print(f"  第{n}条: OK")
    # known legacy typos in both
    for typo in ["公序良欲", "稼動日", "行なう", "テレックス"]:
        print(f"'{typo}' in old: {typo in old}, in new: {typo in new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
