"""Point taiken.html links to voices.html; normalize link label."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACK_OLD = '<a class="taiken-article__back" href="taiken.html">参加者の声（全件）</a>'
BACK_NEW = '<a class="taiken-article__back" href="voices.html">参加者の声</a>'

SKIP_DIRS = {"docs", "tools", ".git", ".cursor", "node_modules"}


def should_process(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.name in {"retarget_taiken_links.py", "rebuild_taiken_index.py"}:
        return False
    if path.suffix == ".html":
        return True
    if path.suffix == ".xml" and path.name == "sitemap.xml":
        return True
    if path.suffix == ".py" and path.parent.name in {"scripts", "tools"}:
        return path.name.startswith("migrate_")
    return False


def patch_text(text: str) -> tuple[str, bool]:
    orig = text
    text = text.replace(BACK_OLD, BACK_NEW)
    text = text.replace(
        '<a href="taiken.html">参加者の声（全件）</a>',
        '<a href="voices.html">参加者の声</a>',
    )
    text = text.replace('href="taiken.html"', 'href="voices.html"')
    text = text.replace("href='taiken.html'", "href='voices.html'")
    text = text.replace("../../taiken.html", "../../voices.html")
    text = text.replace("../taiken.html", "../voices.html")
    # aria-label 等（リンク文言以外）
    text = text.replace("の参加者の声（全件）", "の参加者の声")
    return text, text != orig


def main() -> None:
    changed: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_process(path):
            continue
        if path.name == "taiken.html":
            continue
        text = path.read_text(encoding="utf-8")
        new_text, ok = patch_text(text)
        if ok:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            changed.append(path)
    print(f"updated {len(changed)} files")
    for p in sorted(changed)[:20]:
        print(" ", p.relative_to(ROOT))
    if len(changed) > 20:
        print(f"  ... and {len(changed) - 20} more")


if __name__ == "__main__":
    main()
