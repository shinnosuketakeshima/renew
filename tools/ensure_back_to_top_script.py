# 初回のみ: home.css を参照する HTML に back-to-top.js を一括挿入する（重複防止）

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG_ROOT = '  <script src="assets/js/back-to-top.js" defer></script>\n'
TAG_TEST2 = '  <script src="../assets/js/back-to-top.js" defer></script>\n'


def main() -> None:
    targets: list[Path] = list(ROOT.glob("*.html"))
    test2 = ROOT / "test2" / "index.html"
    if test2.exists():
        targets.append(test2)

    n = 0
    for p in targets:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "home.css" not in text or "back-to-top.js" in text:
            continue
        if "</body>" not in text.lower():
            continue
        low = text.lower()
        idx = low.rfind("</body>")
        if idx < 0:
            continue
        tag = TAG_TEST2 if p.parent.name == "test2" else TAG_ROOT
        new_text = text[:idx] + tag + text[idx:]
        p.write_text(new_text, encoding="utf-8")
        n += 1
        print("updated", p.relative_to(ROOT), file=sys.stderr)

    print("TOTAL", n, file=sys.stderr)


if __name__ == "__main__":
    main()
