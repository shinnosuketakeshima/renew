# 体験談索引: 元データは docs/oldHP/taiken-legacy-root-backup.html から取得し、
# リポジトリルートの taiken.html を更新する。FTP 用ファイルではない（tools/ 配下）。

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "oldHP" / "taiken-legacy-root-backup.html"
if not SRC.exists():
    SRC = ROOT / "taiken.html"
t = SRC.read_text(encoding="utf-8", errors="replace")
# name before taiken link in same <tr> (name cell often has style5 in nested fonts)
rows = []
for block in t.split("<tr>")[1:]:
    mhref = re.search(r'href="(taiken\d+\.html[^"]*)"', block)
    if not mhref:
        continue
    href = mhref.group(1)
    mname = re.search(
        r'class="style5"[^>]*>(?:<font[^>]*>)?([^<]+)(?:</font>)?</span>', block
    ) or re.search(r'<span class="style5"[^>]*><font[^>]*>([^<]+)</font>', block)
    if not mname:
        mname = re.search(r"style5[^>]*>([^<]+)</", block)
    name = mname.group(1).strip() if mname else ""
    rows.append((name, href))
seen: set[str] = set()
out: list[tuple[str, str]] = []
for n, h in rows:
    base = h.split("#")[0]
    if base in seen:
        continue
    seen.add(base)
    out.append((n, h))
nepal_nums = {82, 73, 69, 56, 46, 37, 36, 27, 26, 9}


def key(item):
    n, h = item
    num = int(re.search(r"taiken(\d+)", h).group(1))
    is_n = num in nepal_nums
    return (0 if is_n else 1, -num)


out.sort(key=key)
lines: list[str] = []
for n, h in out:
    num = int(re.search(r"taiken(\d+)", h).group(1))
    ctry = "ネパール" if num in nepal_nums else "スリランカ"
    lines.append(f"{num}\t{ctry}\t{n}\t{h}")
(ROOT / "tools" / "_taiken_index.tsv").write_text("\n".join(lines), encoding="utf-8")
print("TOTAL", len(out), file=sys.stderr)

tr_list = []
for n, h in out:
    num = int(re.search(r"taiken(\d+)", h).group(1))
    country = "ネパール" if num in nepal_nums else "スリランカ"
    cshort = "ネパール" if country == "ネパール" else "スリランカ"
    tr_list.append(
        f'        <tr data-taiken-country="{"nepal" if cshort == "ネパール" else "srilanka"}">'
        f"\n          <td>{cshort}</td>\n"
        f"          <td>{n}</td>\n"
        f'          <td><a href="{h}">体験談{num}を開く</a></td>\n'
        f"        </tr>"
    )

HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>体験談 一覧・索引 | Beインターナショナル</title>
  <meta name="description" content="スリランカ・ネパールの体験談（体験談1〜）を国別の一覧から開けます。年代の目安は各記事をご覧ください。">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://be-intl.com/taiken.html">
  <link rel="stylesheet" href="assets/css/home.css">
  <link rel="stylesheet" href="assets/css/typography.css">
  <link rel="stylesheet" href="assets/css/voices.css">
  <link rel="stylesheet" href="assets/css/legal.css">
</head>
<body class="page-voices page-taiken-index">
  <a class="visually-hidden" href="#main-content">本文へスキップ</a>
  <header class="site-header" id="top">
    <div class="layout-container site-header__inner">
      <a class="site-logo" href="index.html">
        Beインターナショナル
        <span class="site-logo__sub">アジア語学留学</span>
      </a>
      <nav class="site-nav" id="primary-nav" aria-label="主要ナビゲーション" data-nav>
        <a href="srilanka.html">スリランカ</a>
        <a href="nepal.html">ネパール</a>
        <a href="program.html">料金</a>
        <a href="voices.html">体験者の声</a>
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
  </header>
  <main id="main-content">
    <section class="voices-hero voices-hero--compact" id="taiken-hero" aria-labelledby="taiken-heading">
      <div class="voices-hero__bg" aria-hidden="true">
        <div class="voices-hero__color-plane"></div>
      </div>
      <div class="layout-container voices-hero__row">
        <nav class="voices-breadcrumb" aria-label="パンくず">
          <ol>
            <li><a href="index.html">トップ</a></li>
            <li><a href="voices.html">体験者の声</a></li>
            <li aria-current="page">体験談 一覧</li>
          </ol>
        </nav>
        <div class="hero__panel voices-hero__panel">
          <p class="page-voices__kicker">TAIKEN <span class="hero__kicker-sep" aria-hidden="true">|</span> 体験談の索引</p>
          <h1 class="hero__title" id="taiken-heading">体験談 一覧・索引</h1>
          <p class="hero__sub">国と掲載名から、各体験談の本文ページへ進めます。掲出時期の目安は、各ページの表記に従います。</p>
        </div>
      </div>
    </section>
    <section class="voices-section" id="taiken-index" aria-labelledby="taiken-index-h">
      <div class="layout-container">
        <h2 class="voices-section__title" id="taiken-index-h">国別 一覧</h2>
        <p class="voices-section__sub"><a href="voices.html">体験者の声</a>に掲載のない体験談も、下表から国で絞り込んで開けます。<!-- 掲載名は旧トップ面の面付に準拠。要修正は TODO 事務局 --></p>
        <div class="voices-toolbar" role="toolbar" aria-label="国の絞り込み">
          <p class="voices-toolbar__label" id="taiken-filter-label">国</p>
          <div class="voices-filter" role="group" aria-labelledby="taiken-filter-label">
            <button type="button" class="voices-filter__btn is-active" data-taiken-filter="all" aria-pressed="true">すべて</button>
            <button type="button" class="voices-filter__btn" data-taiken-filter="srilanka" aria-pressed="false">スリランカ</button>
            <button type="button" class="voices-filter__btn" data-taiken-filter="nepal" aria-pressed="false">ネパール</button>
          </div>
        </div>
        <p class="taiken-index__note" id="taiken-43-sub">体験談43（Masami Yoshida様）には、別の掲出ブロック用の<a href="taiken43.html#6months">内部リンク</a>があります。</p>
        <div class="legal-table-wrap" role="region" aria-label="体験談 一覧" tabindex="0">
          <table class="legal-table taiken-index__table" id="taiken-index-table">
            <caption class="visually-hidden">国、掲載名、各体験談ページへのリンク</caption>
            <thead>
              <tr>
                <th scope="col">国</th>
                <th scope="col">掲載名</th>
                <th scope="col">体験談</th>
              </tr>
            </thead>
            <tbody id="taiken-index-tbody">
"""
FOOTER = """
            </tbody>
          </table>
        </div>
        <p class="voices-back"><a href="voices.html">体験者の声（抜粋ページ）へ戻る</a></p>
      </div>
    </section>
    <section class="final-cta srilanka-cta" id="taiken-cta" aria-labelledby="taiken-cta-h">
      <div class="srilanka-cta__color-base" aria-hidden="true"></div>
      <div class="final-cta__bg" aria-hidden="true">
        <img src="assets/images/cta-bg.jpg" width="1200" height="600" alt="" decoding="async">
      </div>
      <div class="final-cta__overlay" aria-hidden="true"></div>
      <div class="layout-container">
        <h2 class="srilanka-lead-to-cta" id="taiken-cta-h">資料をご覧のうえ、お気軽にお問い合わせください</h2>
        <p class="final-cta__copy">国や日数、体験談で気になった点も、あわせてメールでお聞かせください。</p>
        <p class="final-cta__reply">ご依頼後、<strong>2〜3営業日以内</strong>にメールにて返信します。</p>
        <p class="final-cta__btn">
          <a class="btn btn--accent" href="postmail.html">資料請求はこちら</a>
        </p>
        <p class="final-cta__tel">
          <span class="final-cta__tel-note">お電話でのご相談</span>
          <strong>03-6770-6191</strong>
        </p>
      </div>
    </section>
    <footer class="site-footer--simple" role="contentinfo">
      <div class="layout-container">
        <a href="index.html">トップ</a>
        <a href="yakkan.html">約款</a>
        <a href="privacy.html">プライバシーポリシー</a>
        <a href="program.html">料金</a>
        <a href="others.html">航空券・保険</a>
      </div>
    </footer>
  </main>
  <script>
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
        link.addEventListener('click', function () { setOpen(false); });
      });
    }
    var fBtns = document.querySelectorAll('[data-taiken-filter]');
    var rows = document.querySelectorAll('#taiken-index-tbody tr[data-taiken-country]');
    fBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-taiken-filter') || 'all';
        fBtns.forEach(function (x) {
          var on = x === b;
          x.classList.toggle('is-active', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        rows.forEach(function (row) {
          var c = row.getAttribute('data-taiken-country');
          var show = f === 'all' || c === f;
          row.hidden = !show;
        });
      });
    });
  })();
  </script>
</body>
</html>
"""
(ROOT / "taiken.html").write_text(HEADER + "\n".join(tr_list) + FOOTER, encoding="utf-8")
print("wrote", ROOT / "taiken.html", file=sys.stderr)
