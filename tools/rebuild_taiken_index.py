# 参加者の声索引: 元データは docs/oldHP/taiken-legacy-root-backup.html から取得し、
# リポジトリルートの taiken.html を更新する。FTP 用ファイルではない（tools/ 配下）。

import html
import json
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

_quotes_path = ROOT / "tools" / "data" / "taiken_quotes.json"
_quotes: dict[str, str] = {}
if _quotes_path.exists():
    _quotes = json.loads(_quotes_path.read_text(encoding="utf-8"))


def _quote_cell(h: str) -> str:
    base = h.split("#")[0]
    q = _quotes.get(base, "").strip()
    if not q:
        num = int(re.search(r"taiken(\d+)", h).group(1))
        return f'          <td class="taiken-index__cell-quote"><a href="{html.escape(h)}">参加者の声{num}を開く</a></td>'
    esc = html.escape(q)
    h_esc = html.escape(h)
    return (
        '          <td class="taiken-index__cell-quote">'
        '<blockquote class="taiken-index__quote">'
        f'<a class="taiken-index__quote-link" href="{h_esc}">'
        '<span class="taiken-index__quote-mark">「</span>'
        f'<span class="taiken-index__quote-text">{esc}</span>'
        '<span class="taiken-index__quote-mark">」</span>'
        f"</a></blockquote></td>"
    )


def _tr_row(n: str, h: str) -> str:
    n_esc = html.escape(n)
    return (
        "        <tr>\n"
        f'          <td class="taiken-index__cell-name">{n_esc}</td>\n'
        f"{_quote_cell(h)}\n"
        "        </tr>"
    )


nepal_rows: list[tuple[str, str]] = []
sri_rows: list[tuple[str, str]] = []
for n, h in out:
    num = int(re.search(r"taiken(\d+)", h).group(1))
    if num in nepal_nums:
        nepal_rows.append((n, h))
    else:
        sri_rows.append((n, h))


def _country_block(
    data_country: str,
    title: str,
    title_id: str,
    region_label: str,
    items: list[tuple[str, str]],
) -> str:
    if not items:
        return ""
    trs = "\n".join(_tr_row(n, h) for n, h in items)
    return f"""        <section class="taiken-index__country-block" data-taiken-country="{data_country}" aria-labelledby="{title_id}">
          <h3 class="taiken-index__country-title" id="{title_id}">{html.escape(title)}</h3>
          <div class="legal-table-wrap" role="region" aria-label="{html.escape(region_label)}の参加者の声一覧" tabindex="0">
            <table class="legal-table taiken-index__table">
              <caption class="visually-hidden">{html.escape(region_label)}。参加者と心に残ったこと・一言メッセージ。各参加者の声のページへリンク</caption>
              <thead>
                <tr>
                  <th scope="col">参加者</th>
                  <th scope="col">心に残ったこと・一言メッセージ<span class="taiken-index__th-sub">（抜粋）</span></th>
                </tr>
              </thead>
              <tbody>
{trs}
              </tbody>
            </table>
          </div>
        </section>
"""

HEADER = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>参加者の声一覧 | Beインターナショナル</title>
  <meta name="description" content="スリランカ・ネパールの参加者の声（参加者の声1〜）を国別の一覧から開けます。年代の目安は各記事をご覧ください。">
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
            <li><a href="voices.html">参加者の声</a></li>
            <li aria-current="page">参加者の声一覧</li>
          </ol>
        </nav>
        <div class="hero__panel voices-hero__panel">
          <p class="page-voices__kicker">VOICES <span class="hero__kicker-sep" aria-hidden="true">|</span> 参加者の声一覧</p>
          <h1 class="hero__title" id="taiken-heading">参加者の声一覧</h1>
          <h2 class="hero__sub">国ごとに参加者と心に残ったこと・一言メッセージから、各参加者の声の本文ページへ進めます。掲出時期の目安は、各ページの表記に従います。</h2>
        </div>
      </div>
    </section>
    <section class="voices-section" id="taiken-index" aria-labelledby="taiken-index-h">
      <div class="layout-container">
        <h2 class="voices-section__title" id="taiken-index-h">国別 一覧</h2>
        <p class="voices-section__sub"><a href="voices.html">参加者の声</a>に掲載のない参加者の声も、下の一覧から国で絞り込んで開けます。</p>
        <div class="voices-toolbar" role="toolbar" aria-label="国の絞り込み">
          <p class="voices-toolbar__label" id="taiken-filter-label">国</p>
          <div class="voices-filter" role="group" aria-labelledby="taiken-filter-label">
            <button type="button" class="voices-filter__btn is-active" data-taiken-filter="all" aria-pressed="true">すべて</button>
            <button type="button" class="voices-filter__btn" data-taiken-filter="nepal" aria-pressed="false">ネパール</button>
            <button type="button" class="voices-filter__btn" data-taiken-filter="srilanka" aria-pressed="false">スリランカ</button>
          </div>
        </div>
        <div class="taiken-index__blocks" id="taiken-index-blocks">
"""
FOOTER = """
        </div>
        <p class="voices-back"><a href="voices.html">参加者の声（抜粋ページ）へ戻る</a></p>
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
        <p class="final-cta__copy">国や日数、参加者の声で気になった点も、あわせてメールでお聞かせください。</p>
        <p class="final-cta__btn">
          <a class="btn btn--accent" href="postmail.html">資料請求・お問合せはこちら</a>
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
        <a href="site-guide.html">サイト案内</a>
        <a href="about.html">会社概要</a>
        <a href="postmail.html">資料請求</a>
        <a href="recomend.html">推薦・メディア</a>
        <a href="yakkan.html">約款</a>
        <a href="privacy.html">プライバシーポリシー</a>
        <a href="program.html">料金</a>
        <a href="others.html">航空券・保険</a>
      </div>
    </footer>
  </main>
  <script src="assets/js/site-header-nav.js" defer></script>
  <script>
  (function () {
    var fBtns = document.querySelectorAll('[data-taiken-filter]');
    var countryBlocks = document.querySelectorAll('.taiken-index__country-block[data-taiken-country]');
    fBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-taiken-filter') || 'all';
        fBtns.forEach(function (x) {
          var on = x === b;
          x.classList.toggle('is-active', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        countryBlocks.forEach(function (block) {
          var c = block.getAttribute('data-taiken-country');
          var show = f === 'all' || c === f;
          block.hidden = !show;
        });
      });
    });
  })();
  </script>
  <script src="assets/js/back-to-top.js" defer></script>
</body>
</html>
"""
_blocks = (
    _country_block("nepal", "ネパール", "taiken-country-nepal", "ネパール", nepal_rows)
    + _country_block("srilanka", "スリランカ", "taiken-country-srilanka", "スリランカ", sri_rows)
)
(ROOT / "taiken.html").write_text(HEADER + _blocks + FOOTER, encoding="utf-8")
print("wrote", ROOT / "taiken.html", file=sys.stderr)

