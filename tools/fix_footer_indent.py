# -*- coding: utf-8 -*-
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main() -> None:
    for name in sorted(os.listdir(REPO)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(REPO, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            t = f.read()
        orig = t
        t = re.sub(
            r'(?m)^        <section class="final-cta final-cta--accent"',
            '    <section class="final-cta final-cta--accent"',
            t,
        )
        t = re.sub(
            r'(?m)^      <section class="final-cta final-cta--accent"',
            '    <section class="final-cta final-cta--accent"',
            t,
        )
        t = re.sub(r"(?m)^</main>\s*$", "  </main>", t)
        if t != orig:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(t)
            print("fixed", name)


if __name__ == "__main__":
    main()
