# 参加者の声一覧: 元データは docs/oldHP/taiken-legacy-root-backup.html から取得し、
# voices.html の国別テーブルを更新する。taiken.html は voices.html へのリダイレクトのみ。

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "oldHP" / "taiken-legacy-root-backup.html"
if not SRC.exists():
    sys.exit(f"missing source: {SRC}")
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
    name = name.replace("様", "さま")
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

# 旧 taiken.html と同様、1名につき2件の抜粋・リンクがある行
_MULTI_QUOTES: dict[str, list[tuple[str, str]]] = {
    "Masami Yoshidaさま": [
        ("taiken43.html", _quotes.get("taiken43.html", "")),
        (
            "taiken43.html#6months",
            "私は、1年前は全く英語を話せなかった。 でも、スリランカへ渡ってから10ヵ月後、"
            "インド資本の会社のスタッフとして、インドで働いています！",
        ),
    ],
    "齋藤碧さま": [
        ("taiken23.html", _quotes.get("taiken23.html", "")),
        (
            "report3.html#1day",
            "英語で相手の知らないことを一から相手にわかるように説明する・・・"
            "英語能力（特に会話能力）が格段に向上したように思う。",
        ),
    ],
    "松本直素さま": [
        (
            "report2.html#report",
            "このプログラムでは、他の日本人に接する機会が少ないので、英語学習の上では効率的・・・",
        ),
        (
            "report2.html#report2",
            "津波被害の被災地や、被災地の学校を訪問して・・・",
        ),
    ],
}


def _inject_extra_sri(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """旧 taiken.html では report2 リンクのみの行（松本直素さま）を挿入。"""
    if any(n == "松本直素さま" for n, _ in rows):
        return rows
    out: list[tuple[str, str]] = []
    for n, h in rows:
        out.append((n, h))
        if n == "清水美奈子さま":
            out.append(("松本直素さま", "report2.html#report"))
    return out


def _quote_block(h: str, q: str) -> str:
    esc = html.escape(q)
    h_esc = html.escape(h)
    return (
        '<blockquote class="taiken-index__quote">'
        f'<a class="taiken-index__quote-link" href="{h_esc}">'
        '<span class="taiken-index__quote-mark">「</span>'
        f'<span class="taiken-index__quote-text">{esc}</span>'
        '<span class="taiken-index__quote-mark">」</span>'
        "</a></blockquote>"
    )


def _quote_cell(h: str) -> str:
    base = h.split("#")[0]
    q = _quotes.get(base, "").strip()
    if not q:
        m = re.search(r"taiken(\d+)", h)
        if m:
            num = m.group(1)
            label = f"参加者の声{num}を開く"
        else:
            label = "詳細を開く"
        return (
            f'          <td class="taiken-index__cell-quote">'
            f'<a href="{html.escape(h)}">{label}</a></td>'
        )
    return f'          <td class="taiken-index__cell-quote">{_quote_block(h, q)}</td>'


def _quote_cell_multi(pairs: list[tuple[str, str]]) -> str:
    blocks = "".join(_quote_block(h, q) for h, q in pairs if q.strip())
    return (
        '          <td class="taiken-index__cell-quote">'
        f'<div class="taiken-index__quotes">{blocks}</div></td>'
    )


def _tr_row(n: str, h: str) -> str:
    n_esc = html.escape(n)
    if n in _MULTI_QUOTES:
        cell = _quote_cell_multi(_MULTI_QUOTES[n])
    else:
        cell = _quote_cell(h)
    return (
        "        <tr>\n"
        f'          <td class="taiken-index__cell-name">{n_esc}</td>\n'
        f"{cell}\n"
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
sri_rows = _inject_extra_sri(sri_rows)


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
          <div class="legal-table-wrap" role="region" aria-label="{html.escape(region_label)}の参加者の声" tabindex="0">
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

TAIKEN_REDIRECT = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>参加者の声 | Beインターナショナル</title>
  <meta name="description" content="スリランカ・ネパールの参加者の声一覧は参加者の声ページでご覧いただけます。">
  <meta name="robots" content="noindex,follow">
  <link rel="canonical" href="https://be-intl.com/voices.html">
  <meta http-equiv="refresh" content="0;url=voices.html#voices-browse">
  <link rel="stylesheet" href="assets/css/home.css">
  <link rel="stylesheet" href="assets/css/typography.css">
</head>
<body class="page-voices">
  <main id="main-content" class="layout-container" style="padding: 4rem 1rem;">
    <p><a href="voices.html#voices-browse">参加者の声</a>のページへ移動しています。</p>
  </main>
</body>
</html>
"""

_blocks_inner = (
    _country_block("nepal", "ネパール", "taiken-country-nepal", "ネパール", nepal_rows)
    + _country_block("srilanka", "スリランカ", "taiken-country-srilanka", "スリランカ", sri_rows)
)
_blocks_wrapper = (
    '        <div class="taiken-index__blocks" id="taiken-index-blocks">\n'
    + _blocks_inner
    + "\n        </div>\n"
)

(ROOT / "taiken.html").write_text(TAIKEN_REDIRECT, encoding="utf-8")
print("wrote", ROOT / "taiken.html", "(redirect)", file=sys.stderr)

voices_path = ROOT / "voices.html"
voices = voices_path.read_text(encoding="utf-8")
marker = '<div class="taiken-index__blocks" id="taiken-index-blocks">'
i0 = voices.find(marker)
if i0 < 0:
    sys.exit(f"voices.html: {marker!r} not found")
i1 = voices.find("\n        </div>\n      </div>\n    </section>", i0)
if i1 < 0:
    sys.exit("voices.html: end of taiken-index blocks not found")
voices_path.write_text(voices[:i0] + _blocks_wrapper.rstrip() + voices[i1:], encoding="utf-8")
print("wrote", voices_path, "(index blocks)", file=sys.stderr)

