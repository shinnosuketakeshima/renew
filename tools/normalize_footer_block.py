# -*- coding: utf-8 -*-
"""Unify final CTA + site footer across root *.html (production pages)."""
from __future__ import annotations

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FOOTER_LINKS: list[tuple[str, str]] = [
    ("index.html", "トップ"),
    ("site-guide.html", "サイト案内"),
    ("about.html", "会社概要"),
    ("postmail.html", "資料請求"),
    ("recomend.html", "推薦・メディア"),
    ("yakkan.html", "約款"),
    ("privacy.html", "プライバシーポリシー"),
    ("program.html", "料金"),
    ("others.html", "航空券・保険"),
]

FINAL_CTA_BLOCK = """    <section class="final-cta final-cta--accent" id="final-cta" aria-labelledby="final-cta-heading">
      <div class="layout-container">
        <h2 id="final-cta-heading">まずは気軽にご相談ください</h2>
        <!--<p class="final-cta__copy">料金のこと、国の違いなど、<span class="keepword">資料とあわせて丁寧にご案内します。</span></p>-->
        <p class="final-cta__btn">
          <a class="btn btn--accent" href="postmail.html">資料請求・お問い合わせはこちら</a>
        </p>
        <p class="final-cta__tel">
          <span class="final-cta__tel-note">お電話でのご相談</span>
          <strong>03-6770-6191</strong>
        </p>
      </div>
    </section>

    <footer class="site-footer--simple" role="contentinfo">
      <div class="layout-container">
{footer_lines}
      </div>
    </footer>"""


def footer_inner_html(basename: str) -> str:
    base = basename.lower()
    lines: list[str] = []
    for href, label in FOOTER_LINKS:
        ac = ' aria-current="page"' if href.lower() == base else ""
        lines.append(f'        <a href="{href}"{ac}>{label}</a>')
    return "\n".join(lines)


def build_block(basename: str) -> str:
    return FINAL_CTA_BLOCK.replace("{footer_lines}", footer_inner_html(basename))


# CTA + footer still inside <main> (typical)
RE_INSIDE_MAIN = re.compile(
    r"<section class=\"(?:final-cta[^\"]*|program-cta[^\"]*|faq-cta[^\"]*|legal-others-cta[^\"]*)\"[\s\S]*?</section>\s*"
    r"<footer class=\"site-footer--simple\"[\s\S]*?</footer>\s*(?=</main>)",
    re.IGNORECASE,
)

# Premature </main> then CTA + footer outside main
RE_OUTSIDE_MAIN = re.compile(
    r"</main>\s*"
    r"<section class=\"final-cta[^\"]*\"[\s\S]*?</section>\s*"
    r"<footer class=\"site-footer--simple\"[\s\S]*?</footer>",
    re.IGNORECASE,
)

# Only footer before </main> (e.g. taiken*.html)
RE_FOOTER_ONLY = re.compile(
    r"<footer class=\"site-footer--simple\"[\s\S]*?</footer>\s*(?=</main>)",
    re.IGNORECASE,
)


def ensure_scripts(html: str) -> str:
    """Append card-visited.js after back-to-top when missing (other scripts untouched)."""
    if "assets/js/card-visited.js" in html:
        return html
    anchor = '  <script src="assets/js/back-to-top.js" defer></script>'
    if anchor in html:
        return html.replace(
            anchor,
            anchor + "\n  <script src=\"assets/js/card-visited.js\" defer></script>",
            1,
        )
    return html.replace(
        "</body>",
        '  <script src="assets/js/card-visited.js" defer></script>\n\n</body>',
        1,
    )


def process_file(path: str, dry: bool) -> bool:
    basename = os.path.basename(path)
    if not basename.lower().endswith(".html"):
        return False
    if basename.startswith("."):
        return False

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        original = f.read()

    if "site-footer--simple" not in original:
        return False

    html = original
    block = build_block(basename)

    # 1) CTA outside </main> → move inside
    if RE_OUTSIDE_MAIN.search(html):
        html = RE_OUTSIDE_MAIN.sub(block + "\n  </main>", html, count=1)
    # 2) Replace CTA + footer before </main>
    elif RE_INSIDE_MAIN.search(html):
        html = RE_INSIDE_MAIN.sub(block + "\n", html, count=1)
    # 3) Footer only before </main>
    elif RE_FOOTER_ONLY.search(html) and 'id="final-cta"' not in html:
        html = RE_FOOTER_ONLY.sub(block + "\n", html, count=1)
    else:
        if "id=\"final-cta\"" in html and "final-cta--accent" in html:
            # Still update footer links + aria-current
            def repl_footer(m: re.Match[str]) -> str:
                inner = footer_inner_html(basename)
                return (
                    '<footer class="site-footer--simple" role="contentinfo">\n'
                    "      <div class=\"layout-container\">\n"
                    f"{inner}\n"
                    "      </div>\n"
                    "    </footer>"
                )

            html = re.sub(
                r"<footer class=\"site-footer--simple\"[\s\S]*?</footer>",
                repl_footer,
                html,
                count=1,
            )
        else:
            sys.stderr.write(f"skip (no match): {basename}\n")
            return False

    html = ensure_scripts(html)

    if html != original:
        if not dry:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(html)
        return True
    return False


def main() -> int:
    dry = "--dry-run" in sys.argv
    root = REPO
    changed = 0
    for name in sorted(os.listdir(root)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(root, name)
        if not os.path.isfile(path):
            continue
        if process_file(path, dry):
            changed += 1
            print(("would write " if dry else "updated ") + name)
    print(f"total: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
