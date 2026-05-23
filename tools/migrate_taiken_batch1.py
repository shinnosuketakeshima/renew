# -*- coding: utf-8 -*-
"""
参加者の声（taiken）ページを新テンプレに変換。ソース: docs/oldHP/taikenN.html（なければルート）。
Run: python scripts/migrate_taiken_batch1.py
"""
from __future__ import annotations

import json
import re
import html
from pathlib import Path

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parent.parent
# 1–49 番（taiken19 は手組み版を上書きしない）
BATCH = [str(n) for n in range(1, 50) if n != 19]

HEADER_NAV = r'''  <header class="site-header" id="top">
    <div class="layout-container site-header__inner">
      <a class="site-logo" href="index.html">
        Beインターナショナル
        <span class="site-logo__sub">アジア語学留学</span>
      </a>
      <nav class="site-nav" id="primary-nav" aria-label="主要ナビゲーション" data-nav>
        <a href="srilanka.html">スリランカ</a>
        <a href="nepal.html">ネパール</a>
        <a href="program.html">料金</a>
        <a href="voices.html">参加者の声</a>
        <a href="faq.html">よくある質問</a>
      </nav>
      <div class="site-header__end">
        <button class="nav-toggle" type="button" id="nav-toggle" aria-expanded="false" aria-controls="primary-nav" data-menu-btn>
          <span class="visually-hidden">メニューを開く</span>
          <span class="nav-toggle__icon" aria-hidden="true"></span>
        </button>
        <a class="btn btn--accent site-header__cta" href="postmail.html">資料請求</a>
      </div>
    </div>
  </header>'''

FOOTER_JS = r'''  <script>
  (function () {
    var header = document.querySelector('.site-header');
    var btn = document.querySelector('[data-menu-btn]');
    var nav = document.getElementById('primary-nav');
    if (header && btn && nav) {
      function setOpen(open) {
        header.classList.toggle('is-menu-open', open);
        btn.setAttribute('aria-expanded', open);
      }
      btn.addEventListener('click', function () {
        setOpen(!header.classList.contains('is-menu-open'));
      });
      nav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
          setOpen(false);
        });
      });
    }
  })();
  </script>'''


def find_article_table(soup: BeautifulSoup):
    for strong in soup.find_all("strong"):
        t = strong.get_text()
        if "スリランカ：" not in t and "ネパール：" not in t:
            continue
        tr = strong.find_parent("tr")
        if not tr:
            continue
        tbl = tr.find_parent("table")
        if not tbl:
            continue
        while tbl:
            rows = tbl.find_all("tr", recursive=False)
            if len(rows) >= 2:
                return tbl
            tbl = tbl.find_parent("table")
    return None


def _heading_in_tr(tr) -> str | None:
    """国名付き見出しの strong テキスト。第1行目でない表（空行＋見出し）に対応。"""
    for s in tr.find_all("strong"):
        t = s.get_text()
        if "スリランカ：" in t or "ネパール：" in t:
            return s.get_text().strip()
    return None


def find_heading_strong(main_table) -> str | None:
    for tr in main_table.find_all("tr", recursive=False):
        h = _heading_in_tr(tr)
        if h:
            return h
    return None


def collect_body_html(main_table) -> str:
    trs = main_table.find_all("tr", recursive=False)
    start = 0
    for i, tr in enumerate(trs):
        if _heading_in_tr(tr):
            start = i + 1
            break
    if start == 0 and trs:
        # 表が拾えているが国名行が未検出のときは従来どおり1行目を除く
        start = 1
    parts: list[str] = []
    for tr in trs[start:]:
        if tr.find("a", href=lambda x: x and "#up" in x):
            break
        tds = tr.find_all("td", recursive=False)
        if not tds:
            continue
        td = tds[0]
        inner = "".join(str(x) for x in td.children)
        st = re.sub(r"\s+", " ", tr.get_text("", strip=True))
        if (not st or st in ("\xa0",)) and "img" not in inner and "IMG" not in inner:
            continue
        if inner.strip():
            parts.append(inner.strip())
    return "\n\n".join(parts)


def clean_legacy(html_fragment: str) -> str:
    frag = re.sub(r"\r\n", "\n", html_fragment)
    soup = BeautifulSoup(frag, "html.parser")
    for tag in soup.find_all(string=lambda t: isinstance(t, Comment)):
        tag.extract()
    for bad in list(soup.find_all(["script", "style", "csobj"])):
        bad.decompose()
    for a in soup.find_all("a", href=True):
        if a.get("href") and "#up" in a["href"]:
            a.decompose()
    for tbl in list(soup.find_all("table")):
        if tbl.find("img"):
            continue
        if tbl.find("IMG"):
            continue
        t = re.sub(r"\s+", "", tbl.get_text() or "")
        if len(t) < 2:
            tbl.decompose()
    return str(soup)


def plain_excerpt(soup: BeautifulSoup, max_len: int) -> str:
    t = soup.get_text(" ", strip=True)
    t = re.sub(r"\s+", " ", t)
    if len(t) > max_len:
        return t[: max_len - 1] + "…"
    return t


def build_meta(heading: str) -> tuple[str, str | None]:
    cty = ""
    if "スリランカ" in heading:
        cty = "スリランカ"
    elif "ネパール" in heading:
        cty = "ネパール"
    period = None
    m2 = re.search(r"(\d{4}年[^■]{0,80}?ご参加|(?:\d{4}年\d+月)～\d+月?ご参加|(?:\d{4}年\d+月)～\d+年[^(ご参加)]+?ご参加)", heading)
    if m2:
        period = m2.group(1).strip()
    if not period:
        m3 = re.search(r"(\d{4}年[^■]{0,30})", heading)
        if m3:
            period = m3.group(1).strip()
    return cty, period


def h1_string(heading: str) -> str:
    t = re.sub(r"■■\s*", "", heading)
    t = t.replace("■■", "").strip()
    if not t.startswith("参加者の声："):
        t = f"参加者の声：{t}"
    t = re.sub(r"^参加者の声：スリランカ：\s*", "参加者の声：スリランカ　", t)
    t = re.sub(r"^参加者の声：ネパール：\s*", "参加者の声：ネパール　", t)
    return t


def run():
    for num in BATCH:
        src = ROOT / "docs" / "oldHP" / f"taiken{num}.html"
        if not src.is_file():
            src = ROOT / f"taiken{num}.html"
        if not src.is_file():
            print("missing", num)
            continue
        raw = src.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(raw, "html.parser")
        main = find_article_table(soup)
        if not main:
            print("no article table", num)
            continue
        h_raw = find_heading_strong(main)
        if not h_raw:
            print("no heading", num)
            continue
        cty, period = build_meta(h_raw)
        body_html = collect_body_html(main)
        if not body_html.strip():
            print("empty body", num)
            continue
        body_clean = clean_legacy(body_html)
        body_soup = BeautifulSoup(body_clean, "html.parser")
        desc = plain_excerpt(body_soup, 150)
        h1e = h1_string(h_raw)
        title = f"{h1e} | Beインターナショナル" if len(h1e) < 100 else f"{h1e[:90]}… | Beインターナショナル"
        fn = f"taiken{num}.html"
        h1_escaped = html.escape(h1e)
        desc_e = html.escape(desc)
        mod = "page-taiken-article--nepal" if "ネパール" in h_raw else "page-taiken-article--srilanka"
        meta_lines = [f"          <li><strong>参加国</strong>：{html.escape(cty)}</li>"] if cty else []
        if period:
            meta_lines.append(f"          <li><strong>参加時期</strong>：{html.escape(period)}</li>")
        meta_block = "\n".join(meta_lines) if meta_lines else "          <!-- TODO: メタ情報 -->\n"
        art = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": h1e,
            "inLanguage": "ja",
            "url": f"https://be-intl.com/{fn}",
            "description": desc,
            "isPartOf": {"@type": "WebSite", "name": "Beインターナショナル", "url": "https://be-intl.com/"},
        }
        json_ld = json.dumps(art, ensure_ascii=False, indent=2)
        indent_ld = "  " + json_ld.replace("\n", "\n  ")
        legacy_block = body_clean
        if "</script" in legacy_block:
            legacy_block = legacy_block.replace("</script", "<\\/script")
        out = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{desc_e}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://be-intl.com/{fn}">
  <link rel="stylesheet" href="assets/css/home.css">
  <link rel="stylesheet" href="assets/css/typography.css">
  <link rel="stylesheet" href="assets/css/taiken-article.css">
  <script type="application/ld+json">
{indent_ld}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Beインターナショナル",
    "url": "https://be-intl.com/"
  }}
  </script>
  <!-- 本文は旧HTMLから抽出（レイアウトは .taiken-legacy で再スタイル） -->
  <!-- 特殊行間・囲みは TODO: 事務局で誤字・体裁を確認 -->
</head>
<body class="page-taiken-article {mod}">
  <a class="visually-hidden" href="#main-content">本文へスキップ</a>

{HEADER_NAV}

  <main id="main-content">
    <div class="taiken-head">
      <div class="layout-container">
        <h1 class="taiken-head__h1" id="taiken-h1">{h1_escaped}</h1>
        <ul class="taiken-meta">
{meta_block}
        </ul>
        <!-- TODO: 本番URL・301 設計と合わせる -->
      </div>
    </div>

    <article class="taiken-article" aria-labelledby="taiken-h1">
      <div class="taiken-body taiken-legacy">
{legacy_block}

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

{FOOTER_JS}
</body>
</html>
"""
        (ROOT / fn).write_text(out, encoding="utf-8")
        print("wrote", fn)


if __name__ == "__main__":
    run()

