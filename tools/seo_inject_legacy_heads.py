#!/usr/bin/env python3
"""
Normalize legacy charset meta, add viewport + canonical when missing, and add
Organization JSON-LD when missing. Target: repository root *.html only.
Does not modify <body>.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[1]

LEGACY_CHARSET = re.compile(
    r"<meta\s+http-equiv\s*=\s*[\"']?content-type[\"']?\s+content\s*=\s*[\"']text/html;\s*charset=x-utf8[\"']?\s*>",
    re.I,
)
HEAD_OPEN = re.compile(r"<head[^>]*>", re.I)
HAS_CANONICAL = re.compile(r'rel\s*=\s*["\']canonical["\']', re.I)
HAS_ORG = re.compile(r'"@type"\s*:\s*"Organization"', re.I)
CLOSE_HEAD = re.compile(r"</head>", re.I)

ORG_SNIPPET = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Beインターナショナル",
  "url": "https://be-intl.com/"
}
</script>
"""


def canonical_href(filename: str) -> str:
    if filename == "index-legacy.html":
        return "https://be-intl.com/"
    return f"https://be-intl.com/{quote(filename)}"


def inject_canonical_viewport(text: str, filename: str) -> str:
    if HAS_CANONICAL.search(text):
        return text
    m = HEAD_OPEN.search(text)
    if not m:
        print(f"SKIP (no <head>): {filename}")
        return text
    tail = text[m.end() :]
    parts: list[str] = []
    if not re.match(r"\s*<meta\s+charset", tail, re.I):
        parts.append("\n<meta charset=\"utf-8\">\n")
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    parts.append(f'<link rel="canonical" href="{canonical_href(filename)}">\n')
    return text[: m.end()] + "".join(parts) + text[m.end() :]


def inject_org(text: str) -> str:
    if HAS_ORG.search(text):
        return text
    cm = CLOSE_HEAD.search(text)
    if not cm:
        return text
    return text[: cm.start()] + ORG_SNIPPET + "\n" + text[cm.start() :]


def main() -> int:
    n = 0
    for path in sorted(REPO.glob("*.html")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="cp932", errors="replace")

        orig = text
        text = LEGACY_CHARSET.sub('<meta charset="utf-8">', text, count=1)
        text = inject_canonical_viewport(text, path.name)
        text = inject_org(text)
        if text != orig:
            path.write_text(text, encoding="utf-8", newline="\n")
            print(path.name)
            n += 1
    print(f"Done. Updated {n} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

