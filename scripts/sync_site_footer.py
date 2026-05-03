"""
Unify <footer class="site-footer--simple"> across site to match index.html (8 links).
Run from repo root: python scripts/sync_site_footer.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (href from site root, label, current_key)
FOOTER_ITEMS = [
    ("index.html", "トップ", "index"),
    ("site-guide.html", "サイト案内", "site-guide"),
    ("about.html", "会社概要", "about"),
    ("postmail.html", "資料請求", "postmail"),
    ("recomend.html", "推薦・メディア", "recomend"),
    ("yakkan.html", "約款", "yakkan"),
    ("privacy.html", "プライバシーポリシー", "privacy"),
    ("program.html", "料金", "program"),
    ("others.html", "航空券・保険", "others"),
]

# 直前のインデントごと置換し、二重スペースを残さない
FOOTER_RE = re.compile(
    r"[ \t]*<footer\s+class=\"site-footer--simple\"\s+role=\"contentinfo\">\s*"
    r"<div\s+class=\"layout-container\">.*?</div>\s*</footer>",
    re.DOTALL | re.IGNORECASE,
)


def current_key_for_path(rel: Path) -> str | None:
    name = rel.as_posix()
    if name == "index.html":
        return "index"
    mapping = {
        "site-guide.html": "site-guide",
        "about.html": "about",
        "postmail.html": "postmail",
        "recomend.html": "recomend",
        "yakkan.html": "yakkan",
        "privacy.html": "privacy",
        "program.html": "program",
        "others.html": "others",
    }
    return mapping.get(rel.name)


def href_for_item(item_href: str, in_test2: bool) -> str:
    if not in_test2:
        return item_href
    return f"../{item_href}"


def build_footer(rel: Path) -> str:
    in_test2 = rel.as_posix().startswith("test2/")
    cur = current_key_for_path(rel)
    lines = ['    <footer class="site-footer--simple" role="contentinfo">', '      <div class="layout-container">']
    for href, label, key in FOOTER_ITEMS:
        h = href_for_item(href, in_test2)
        if cur == key:
            lines.append(f'        <a href="{h}" aria-current="page">{label}</a>')
        else:
            lines.append(f'        <a href="{h}">{label}</a>')
    lines.extend(["      </div>", "    </footer>"])
    return "\n".join(lines)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    m = FOOTER_RE.search(text)
    if not m:
        print(f"skip (no footer match): {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    rel = path.relative_to(ROOT)
    new_footer = build_footer(rel)
    new_text = FOOTER_RE.sub(new_footer, text, count=1)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"updated: {rel.as_posix()}")
    return True


def main() -> None:
    updated = 0
    for p in sorted(ROOT.glob("*.html")):
        if process_file(p):
            updated += 1
    test2_index = ROOT / "test2" / "index.html"
    if test2_index.is_file() and process_file(test2_index):
        updated += 1
    print(f"Done. {updated} files updated.")


if __name__ == "__main__":
    main()

