# ルート直下の旧HTMLに home.css / typography.css / back-to-top.js を付与（重複しないようスキップ）

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEAD_SNIPPET = """
  <link rel="stylesheet" href="assets/css/home.css">
  <link rel="stylesheet" href="assets/css/typography.css">
"""

SCRIPT_LINE = '  <script src="assets/js/back-to-top.js" defer></script>\n'


def patch_file(p: Path) -> tuple[bool, str]:
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return False, str(e)

    orig = text
    if "home.css" not in text:
        m = re.search(r"</head>", text, flags=re.IGNORECASE)
        if m:
            text = text[: m.start()] + HEAD_SNIPPET + text[m.start() :]
        else:
            m2 = re.search(r"<head[^>]*>", text, flags=re.IGNORECASE | re.DOTALL)
            if m2:
                i = m2.end()
                text = text[:i] + HEAD_SNIPPET + text[i:]
            else:
                return False, "no head"

    if "back-to-top.js" not in text:
        low = text.lower()
        idx = low.rfind("</body>")
        if idx < 0:
            return False, "no body"
        text = text[:idx] + SCRIPT_LINE + text[idx:]

    if text == orig:
        return False, "unchanged"
    p.write_text(text, encoding="utf-8")
    return True, "ok"


def main() -> None:
    n = 0
    for p in sorted(ROOT.glob("*.html")):
        try:
            c = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "home.css" in c and "back-to-top.js" in c:
            continue
        ok, msg = patch_file(p)
        if ok:
            n += 1
            print("patched", p.name, file=sys.stderr)
        elif msg not in ("unchanged",):
            print("skip", p.name, msg, file=sys.stderr)

    print("TOTAL_PATCHED", n, file=sys.stderr)


if __name__ == "__main__":
    main()

