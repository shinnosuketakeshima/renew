# -*- coding: utf-8 -*-
"""Insert blank line between </main> and first bottom script (matches index template)."""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    pat = re.compile(r"(  </main>)\r?\n(  <script src=\"assets/js/)", re.MULTILINE)
    for name in sorted(os.listdir(REPO)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(REPO, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            t = f.read()
        t2, n = pat.subn(r"\1\n\n\2", t)
        if n and t2 != t:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(t2)
            print(name, n)


if __name__ == "__main__":
    main()
