#!/usr/bin/env python3
"""Add analytics.js to all root HTML pages that load GA4 but lack the script."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_TAG = '  <script src="assets/js/analytics.js?v=20260612" defer></script>\n'
MARKER = "analytics.js"


def main() -> None:
    updated = 0
    for path in sorted(ROOT.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        if "G-40ZZ28MV66" not in text or MARKER in text:
            continue
        if "</body>" not in text:
            continue
        text = text.replace("</body>", SCRIPT_TAG + "</body>", 1)
        path.write_text(text, encoding="utf-8")
        updated += 1
        print(path.name)
    print(f"\nUpdated {updated} file(s).")


if __name__ == "__main__":
    main()
