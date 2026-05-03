from pathlib import Path

root = Path(__file__).resolve().parents[1]
count = 0
paths = list(root.glob("*.html")) + [root / "test2" / "index.html"]
for p in paths:
    if not p.is_file():
        continue
    t = p.read_text(encoding="utf-8")
    old = "\n        <footer class=\"site-footer--simple\""
    new = "\n    <footer class=\"site-footer--simple\""
    t2 = t.replace(old, new)
    if t2 != t:
        p.write_text(t2, encoding="utf-8", newline="\n")
        count += 1
print("fixed indent:", count)

