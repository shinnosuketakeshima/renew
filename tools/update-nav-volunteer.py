#!/usr/bin/env python3
"""Insert ボランティア nav link after ネパール in site-header navigation."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HAS_VOLUNTEER_NAV = re.compile(
    r'<a\s+href="(?:\.\./)?volunteer\.html"[^>]*>ボランティア</a>'
)

NEPAL_THEN_PROGRAM = re.compile(
    r'(<a href="(?:\.\./)?nepal\.html"[^>]*>ネパール</a>\n)'
    r'(\s*)(<a href="(?:\.\./)?program\.html"[^>]*>料金</a>)'
)


def update_content(content: str, filename: str) -> tuple[str, bool]:
    if "site-nav" not in content or "nepal.html" not in content:
        return content, False

    if HAS_VOLUNTEER_NAV.search(content):
        if filename == "volunteer.html":
            new = re.sub(
                r'<a href="volunteer\.html"[^>]*>',
                '<a href="volunteer.html" aria-current="page">',
                content,
                count=1,
            )
            return new, new != content
        return content, False

    changed = False
    prefix = "../" if "../nepal.html" in content else ""

    compact_old = (
        f'<a href="{prefix}nepal.html">ネパール</a>'
        f'<a href="{prefix}program.html">料金</a>'
    )
    compact_new = (
        f'<a href="{prefix}nepal.html">ネパール</a>'
        f'<a href="{prefix}volunteer.html">ボランティア</a>'
        f'<a href="{prefix}program.html">料金</a>'
    )
    if compact_old in content:
        content = content.replace(compact_old, compact_new)
        changed = True

    def repl(match: re.Match[str]) -> str:
        indent = match.group(2)
        vol = f'{indent}<a href="{prefix}volunteer.html">ボランティア</a>\n'
        return match.group(1) + vol + indent + match.group(3)

    content, n = NEPAL_THEN_PROGRAM.subn(repl, content)
    if n:
        changed = True

    return content, changed


def main() -> None:
    updated: list[str] = []
    skipped: list[str] = []

    for path in sorted(ROOT.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        new_text, changed = update_content(text, path.name)
        if changed:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            updated.append(path.name)
        elif (
            "site-nav" in text
            and "nepal.html" in text
            and not HAS_VOLUNTEER_NAV.search(text)
        ):
            skipped.append(path.name)

    print(f"Updated {len(updated)} files")
    for name in updated:
        print(f"  {name}")
    if skipped:
        print(f"No pattern match ({len(skipped)}):")
        for name in skipped:
            print(f"  {name}")


if __name__ == "__main__":
    main()
