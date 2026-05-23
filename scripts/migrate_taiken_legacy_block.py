# -*- coding: utf-8 -*-
"""docs/oldHP/taikenNN.html から本文ブロックを抽出し、新シェルHTMLを生成する。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "docs" / "oldHP"

SHELL_HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Beインターナショナル</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://be-intl.com/{outname}">
  <link rel="stylesheet" href="assets/css/home.css">
  <link rel="stylesheet" href="assets/css/typography.css">
  <link rel="stylesheet" href="assets/css/taiken-article.css">
  <script type="application/ld+json">
  {{"@context": "https://schema.org", "@type": "Article", "headline": {h1_json}, "inLanguage": "ja", "url": "https://be-intl.com/{outname}", "isPartOf": {{"@type": "WebSite", "name": "Beインターナショナル", "url": "https://be-intl.com/"}}}}
  </script>
  <script type="application/ld+json">
  {{"@context": "https://schema.org", "@type": "Organization", "name": "Beインターナショナル", "url": "https://be-intl.com/"}}
  </script>
</head>
<body class="page-taiken-article {country_class}">
  <a class="visually-hidden" href="#main-content">本文へスキップ</a>
  <header class="site-header" id="top">
    <div class="layout-container site-header__inner">
      <a class="site-logo" href="index.html">Beインターナショナル<span class="site-logo__sub">アジア語学留学</span></a>
      <nav class="site-nav" id="primary-nav" aria-label="主要ナビゲーション" data-nav>
        <a href="srilanka.html">スリランカ</a><a href="nepal.html">ネパール</a><a href="program.html">料金</a><a href="voices.html">参加者の声</a><a href="faq.html">よくある質問</a>
      </nav>
      <div class="site-header__end">
        <button class="nav-toggle" type="button" id="nav-toggle" aria-expanded="false" aria-controls="primary-nav" data-menu-btn>
          <span class="visually-hidden">メニューを開く</span><span class="nav-toggle__icon" aria-hidden="true"></span>
        </button>
        <a class="btn btn--accent site-header__cta" href="postmail.html">資料請求</a>
      </div>
    </div>
  </header>
  <main id="main-content">
    <div class="taiken-head">
      <div class="layout-container">
        <h1 class="taiken-head__h1" id="taiken-h1">{h1}</h1>
        <ul class="taiken-meta">
          <li><strong>参加国</strong>：{country}</li>
          <li><strong>参加時期</strong>：{period}</li>
        </ul>
      </div>
    </div>
    <article class="taiken-article" aria-labelledby="taiken-h1">
      <div class="taiken-body taiken-legacy">
{inner}
        <footer class="taiken-article__foot">
          <div class="taiken-article__actions">
            <a class="taiken-article__back" href="voices.html">参加者の声</a>
          </div>
        </footer>
      </div>
    </article>
    <footer class="site-footer--simple" role="contentinfo">
      <div class="layout-container">
        <a href="index.html">トップ</a>
        <a href="yakkan.html">約款</a>
        <a href="privacy.html">プライバシーポリシー</a>
        <a href="others.html">航空券・保険</a>
      </div>
    </footer>
  </main>
  <script>
  (function () {{ var h = document.querySelector('.site-header'), b = document.querySelector('[data-menu-btn]'), n = document.getElementById('primary-nav');
    if (h && b && n) {{ function o(x) {{ h.classList.toggle('is-menu-open', x); b.setAttribute('aria-expanded', x); }}
      b.addEventListener('click', function () {{ o(!h.classList.contains('is-menu-open')); }});
      n.querySelectorAll('a').forEach(function (l) {{ l.addEventListener('click', function () {{ o(false); }}); }});
    }} }})();
  </script>
  <script src="assets/js/back-to-top.js" defer></script>
</body>
</html>
"""

def json_escape(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_heading(raw: str) -> tuple[str, str, str, str] | None:
    m = re.search(r"■■<strong>([^<]+)</strong>", raw)
    if not m:
        return None
    line = m.group(1).strip()
    if line.startswith("スリランカ：") or line.startswith("スリランカ:"):
        country = "スリランカ"
        rest = line.split("：", 1)[1] if "：" in line else line.split(":", 1)[1]
        h1 = f"参加者の声：スリランカ　{rest.strip()}"
    elif line.startswith("ネパール：") or line.startswith("ネパール:"):
        country = "ネパール"
        rest = line.split("：", 1)[1] if "：" in line else line.split(":", 1)[1]
        h1 = f"参加者の声：ネパール　{rest.strip()}"
    else:
        country = "スリランカ"
        h1 = line if line.startswith("参加者の声") else f"参加者の声：{line}"
    cclass = "page-taiken-article--srilanka" if country == "スリランカ" else "page-taiken-article--nepal"
    pm = re.search(r"(\d{4}年[^<]*?ご参加)", line)
    if pm:
        period = pm.group(1).strip()
    else:
        period = line.split("：", 1)[-1] if "：" in line else "—"
    return h1, country, cclass, period


def extract_inner_html(raw: str) -> str | None:
    """旧メイン枠内のHTML（table入り）。"""
    m = re.search(
        r'<table[^>]+width="533"[^>]*>\s*<tr>\s*<td[^>]*>(?P<inner>[\s\S]+?)</table>\s*</td>\s*</tr>\s*<tr>\s*<td>\s*&nbsp;\s*</td>',
        raw,
        re.IGNORECASE,
    )
    if m:
        return m.group("inner").strip()
    m2 = re.search(
        r"■■<strong>[^<]+</strong>[\s\S]*?</tr>\s*<tr>\s*<td>\s*(?P<inner>[\s\S]*?)<a href=\"#up\">UP",
        raw,
    )
    if m2:
        return m2.group("inner").strip()
    return None


def clean_inner(s: str) -> str:
    return s


def run_one(old_name: str, out_name: str | None = None) -> bool:
    path = OLD / old_name
    if not path.exists():
        print("missing", path)
        return False
    raw = path.read_text(encoding="utf-8", errors="replace")
    ph = parse_heading(raw)
    if not ph:
        print("no heading", old_name)
        return False
    h1, country, cclass, period = ph
    inner = extract_inner_html(raw)
    if not inner:
        print("no inner", old_name)
        return False
    inner = clean_inner(inner)
    outn = out_name or old_name
    desc = re.sub(r"\s+", " ", h1)[:200]
    out = SHELL_HEAD.format(
        title=h1.replace('"', "＂")[:200],
        h1=h1,
        h1_json=json_escape(h1),
        desc=desc,
        outname=outn,
        country=country,
        period=period,
        country_class=cclass,
        inner=inner,
    )
    (ROOT / outn).write_text(out, encoding="utf-8")
    print("wrote", outn)
    return True


if __name__ == "__main__":
    files = [
        ("taiken54.html", "taiken54.html"),
        ("taiken55.html", "taiken55.html"),
        ("taiken58.html", "taiken58.html"),
        ("taiken60.html", "taiken60.html"),
        ("taiken61.html", "taiken61.html"),
        ("taiken62.html", "taiken62.html"),
        ("taiken63.html", "taiken63.html"),
        ("taiken63-r.html", "taiken63-r.html"),
        ("taiken63-r_new.html", "taiken63-r_new.html"),
        ("taiken64.html", "taiken64.html"),
        ("taiken65.html", "taiken65.html"),
        ("taiken67.html", "taiken67.html"),
        ("taiken68.html", "taiken68.html"),
        ("taiken72.html", "taiken72.html"),
        ("taiken74.html", "taiken74.html"),
        ("taiken77.html", "taiken77.html"),
        ("taiken79.html", "taiken79.html"),
    ]
    for a, b in files:
        if len(sys.argv) > 1 and a not in sys.argv[1:]:
            continue
        run_one(a, b)
    for p in OLD.glob("taiken84*.html"):
        if "修正" in p.name:
            run_one(p.name, "taiken84修正前.html")

