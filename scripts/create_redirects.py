import os

REDIRECTS = {
    "company.html": "about.html",
    "qa.html": "faq.html",
    "cost.html": "program.html#srilanka",
    "ncost.html": "program.html#nepal",
    "scost.html": "program.html#srilanka",
    "lesson.html": "program.html#inclusions",
    "nlesson.html": "nepal.html#nepal-lesson",
    "slesson.html": "srilanka.html#srilanka-lesson",
    "sample.html": "program.html#inclusions",
    "homestay.html": "srilanka.html#srilanka-homestay",
    "nhomestay.html": "nepal.html#nepal-homestay",
    "village.html": "srilanka.html#srilanka-village",
    "security.html": "srilanka.html#srilanka-safety",
    "nsecurity.html": "nepal.html#nepal-local-safety",
    "sinhara.html": "srilanka.html#srilanka-language",
    "nepallg.html": "nepal.html#nepal-language",
    "knowledge.html": "faq.html#knowledge-moved",
    "support.html": "srilanka.html#srilanka-support",
    "free.html": "program.html#inclusions",
    "info.html": "index.html",
    "link.html": "index.html",
    "links.html": "index.html",
    "cancel.html": "yakkan.html",
    "ncancel.html": "yakkan.html",
    "process2.html": "process1.html",
    "nprocess2.html": "process1.html",
    "indonesia.html": "index.html",
    "volunteers.html": "volunteer.html",
}

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>転送中… | Beインターナショナル</title>
  <link rel="canonical" href="https://be-intl.com/{target}">
  <meta http-equiv="refresh" content="0;url={target}">
  <meta name="robots" content="noindex,follow">
  <script>location.replace("{target}");</script>
</head>
<body>
  <p>このページは移転しました。数秒待たない場合は <a href="{target}">こちら（{target}）</a> お進みください。</p>
</body>
</html>
"""

def apply_redirects():
    for source, target in REDIRECTS.items():
        # Check in root and docs/oldHP
        paths_to_try = [source, os.path.join("docs", "oldHP", source)]
        found = False
        for p in paths_to_try:
            if os.path.exists(p):
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(TEMPLATE.format(target=target))
                print(f"Created redirect: {p} -> {target}")
                found = True
        if not found:
            # Create in root if not found anywhere (to be safe for newly identified redirects)
            with open(source, 'w', encoding='utf-8') as f:
                f.write(TEMPLATE.format(target=target))
            print(f"Created new redirect in root: {source} -> {target}")

if __name__ == "__main__":
    apply_redirects()
