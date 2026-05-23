# -*- coding: utf-8 -*-
"""Restore taiken pages from docs/oldHP into taiken38-style blocks (full text + natural photos)."""
from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import migrate_taiken_batch1 as mig  # noqa: E402

DEFAULT_RANGE = range(39, 85)


@dataclass
class Figure:
    src: str
    width: int | None
    height: int | None
    caption: str

    @property
    def is_portrait(self) -> bool:
        if self.width and self.height:
            return self.height > self.width
        return False


@dataclass
class ImageBlock:
    side: str  # left | right
    figure: Figure
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class TextBlock:
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class FigureRowBlock:
    figures: list[Figure] = field(default_factory=list)


Block = ImageBlock | TextBlock | FigureRowBlock


def is_participant_img(img: Tag) -> bool:
    src = (img.get("src") or "").strip()
    return bool(src) and not src.startswith("images/") and "spacer" not in src.lower()


def td_has_participant_img(td: Tag) -> bool:
    return any(is_participant_img(im) for im in td.find_all("img"))


def is_2col_image_table(table: Tag) -> bool:
    trs = table.find_all("tr", recursive=False)
    if len(trs) != 1:
        return False
    tds = trs[0].find_all("td", recursive=False)
    if len(tds) != 2:
        return False
    return bool(td_has_participant_img(tds[0]) or td_has_participant_img(tds[1]))


def minimal_2col_tables(root: Tag) -> list[Tag]:
    all_t = [t for t in root.find_all("table") if is_2col_image_table(t)]
    return [t for t in all_t if not any(other != t and other in t.descendants for other in all_t)]


def unwrap_fonts(node: Tag) -> None:
    for font in list(node.find_all("font")):
        font.unwrap()


def inline_html(el: Tag) -> str:
    copy = BeautifulSoup(str(el), "html.parser").find(el.name)
    if not copy:
        return ""
    unwrap_fonts(copy)
    return "".join(str(c) for c in copy.children).strip()


def paragraph_html(p: Tag) -> str:
    inner = inline_html(p)
    if not BeautifulSoup(inner, "html.parser").get_text(strip=True):
        return ""
    return f"<p>{inner}</p>"


def span_as_paragraph(span: Tag) -> str:
    inner = inline_html(span)
    if not BeautifulSoup(inner, "html.parser").get_text(strip=True):
        return ""
    return f"<p>{inner}</p>"


def parse_figure(td: Tag) -> Figure | None:
    img = None
    for im in td.find_all("img"):
        if is_participant_img(im):
            img = im
            break
    if not img:
        return None
    w = int(img["width"]) if img.get("width") and str(img["width"]).isdigit() else None
    h = int(img["height"]) if img.get("height") and str(img["height"]).isdigit() else None
    caption = ""
    for p in td.find_all("p"):
        if p.find("img"):
            continue
        t = p.get_text(strip=True)
        if t:
            caption = t
            break
    alt = caption or "スリランカ・ネパール留学の体験写真"
    return Figure(src=img["src"].strip(), width=w, height=h, caption=caption)


def paragraphs_from_td(td: Tag) -> list[str]:
    out: list[str] = []
    for el in td.find_all(["p", "span"]):
        if el.find("img"):
            continue
        if el.name == "span" and el.find_parent("p"):
            continue
        h = paragraph_html(el) if el.name == "p" else span_as_paragraph(el)
        if h and h not in out:
            out.append(h)
    return out


def parse_2col_table(table: Tag) -> ImageBlock:
    tr = table.find("tr", recursive=False)
    assert tr is not None
    tds = tr.find_all("td", recursive=False)
    t0, t1 = tds[0], tds[1]
    if td_has_participant_img(t0) and not td_has_participant_img(t1):
        fig = parse_figure(t0)
        assert fig is not None
        return ImageBlock("left", fig, paragraphs_from_td(t1))
    if td_has_participant_img(t1) and not td_has_participant_img(t0):
        fig = parse_figure(t1)
        assert fig is not None
        return ImageBlock("right", fig, paragraphs_from_td(t0))
    if td_has_participant_img(t0) and td_has_participant_img(t1):
        figs = [f for f in (parse_figure(t0), parse_figure(t1)) if f]
        if figs:
            return FigureRowBlock(figures=figs)
    raise ValueError("2col table without image column")


def inside_minimal_2col(p: Tag, tables: list[Tag]) -> bool:
    table_ids = {id(t) for t in tables}
    anc = p.find_parent("table")
    while anc:
        if id(anc) in table_ids:
            return True
        anc = anc.find_parent("table")
    return False


def build_blocks(body_root: Tag) -> list[Block]:
    tables = minimal_2col_tables(body_root)
    items: list[tuple[int, str, Tag]] = []
    for t in tables:
        items.append((t.sourceline or 0, "table", t))
    for el in body_root.find_all(["p", "span"]):
        if not el.get_text(strip=True):
            continue
        if el.name == "span" and el.find_parent("p"):
            continue
        if inside_minimal_2col(el, tables):
            continue
        if el.find("img") and is_participant_img(el.find("img")):
            continue
        items.append((el.sourceline or 0, "p", el))
    items.sort(key=lambda x: (x[0], x[1] == "p"))

    blocks: list[Block] = []
    text_buf: list[str] = []

    def flush_text() -> None:
        nonlocal text_buf
        if text_buf:
            blocks.append(TextBlock(paragraphs=text_buf))
            text_buf = []

    for _, kind, el in items:
        if kind == "table":
            flush_text()
            blocks.append(parse_2col_table(el))
        else:
            h = paragraph_html(el) if el.name == "p" else span_as_paragraph(el)
            if h:
                text_buf.append(h)
    flush_text()
    return blocks


def render_figure(fig: Figure) -> str:
    w_attr = f' width="{fig.width}"' if fig.width else ""
    h_attr = f' height="{fig.height}"' if fig.height else ""
    alt = html.escape(fig.caption or "体験写真")
    cap = html.escape(fig.caption) if fig.caption else ""
    landscape = fig.width and fig.height and fig.width >= fig.height
    fig_class = "taiken-figure taiken-figure--block"
    if landscape:
        fig_class += " taiken-figure--landscape"
    cap_html = f"\n              <figcaption>{cap}</figcaption>" if cap else ""
    return f"""            <figure class="{fig_class}">
              <img src="{html.escape(fig.src)}"{w_attr}{h_attr} alt="{alt}" loading="lazy" decoding="async">{cap_html}
            </figure>"""


def render_blocks(blocks: list[Block]) -> str:
    parts: list[str] = []
    for b in blocks:
        if isinstance(b, TextBlock):
            paras = "\n              ".join(b.paragraphs)
            parts.append(
                f"""          <div class="taiken-block">
            <div class="taiken-block__text content-area">
              {paras}
            </div>
          </div>"""
            )
        elif isinstance(b, FigureRowBlock):
            figs = "\n            ".join(render_figure(f) for f in b.figures)
            parts.append(
                f"""          <div class="taiken-fig-row taiken-fig-row--2" role="group">
            {figs}
          </div>"""
            )
        elif isinstance(b, ImageBlock):
            fig_html = render_figure(b.figure)
            paras = "\n              ".join(b.paragraphs)
            if b.side == "left":
                parts.append(
                    f"""          <div class="taiken-block taiken-block--image-left" role="group">
            {fig_html}
            <div class="taiken-block__text content-area">
              {paras}
            </div>
          </div>"""
                )
            else:
                parts.append(
                    f"""          <div class="taiken-block taiken-block--image-right" role="group">
            <div class="taiken-block__text content-area">
              {paras}
            </div>
            {fig_html}
          </div>"""
                )
    return "\n\n".join(parts)


def short_h1(heading: str) -> str:
    t = re.sub(r"■■\s*", "", heading).replace("■■", "").strip()
    t = re.sub(r"^参加者の声：", "", t)
    t = re.sub(r"^スリランカ：\s*", "", t)
    t = re.sub(r"^ネパール：\s*", "", t)
    m = re.match(r"^(.+?)(?:\d{4}年|様|さま)", t)
    if m:
        name = m.group(1).strip()
        return f"参加者の声：{name}さま"
    return f"参加者の声：{t[:30]}"


def find_article_content_td(soup: BeautifulSoup) -> Tag | None:
    """Largest article cell (handles broken nested tables in late oldHP pages)."""
    best: Tag | None = None
    best_score = 0
    for td in soup.find_all("td"):
        if td.find("a", href=lambda x: x and "#up" in x):
            continue
        has_photo = td.find(
            "img",
            src=lambda s: s
            and not str(s).startswith("images/")
            and "spacer" not in str(s).lower(),
        )
        if not has_photo:
            continue
        score = len(re.sub(r"\s+", "", td.get_text() or ""))
        if score > best_score:
            best_score = score
            best = td
    return best if best_score > 100 else None


def collect_article_html(soup: BeautifulSoup, main: Tag) -> str:
    body_html = mig.collect_body_html(main)
    merged = collect_heading_table_html(soup)
    if merged and len(merged) > len(body_html) * 1.05:
        return merged
    td = find_article_content_td(soup)
    if td:
        direct = "".join(str(c) for c in td.children).strip()
        if len(direct) > len(body_html) * 1.05:
            return direct
    return body_html


def collect_heading_table_html(soup: BeautifulSoup) -> str:
    """All cells after the country heading row (includes malformed sibling <td> nodes)."""
    for strong in soup.find_all("strong"):
        t = strong.get_text()
        if "スリランカ：" not in t and "ネパール：" not in t:
            continue
        tr = strong.find_parent("tr")
        if not tr:
            continue
        table = tr.find_parent("table")
        if not table:
            continue
        parts: list[str] = []
        past_heading = False
        for child in table.children:
            if not isinstance(child, Tag):
                continue
            if child.name == "tr":
                if not past_heading:
                    if tr in child.descendants or child == tr:
                        past_heading = True
                    continue
                for td in child.find_all("td", recursive=False):
                    if td.find("a", href=lambda x: x and "#up" in x):
                        continue
                    chunk = "".join(str(c) for c in td.children).strip()
                    if chunk and "UP▲" not in chunk:
                        parts.append(chunk)
            elif child.name == "td" and past_heading:
                if child.find("a", href=lambda x: x and "#up" in x):
                    continue
                chunk = "".join(str(c) for c in child.children).strip()
                if chunk and "UP▲" not in chunk:
                    parts.append(chunk)
        if parts:
            return "\n".join(parts)
    return ""


def extract_from_old(num: int) -> tuple[str, list[Block], bool, str, str | None] | None:
    src = ROOT / "docs" / "oldHP" / f"taiken{num}.html"
    if not src.is_file():
        return None
    raw = src.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    main = mig.find_article_table(soup)
    if not main:
        return None
    h_raw = mig.find_heading_strong(main)
    if not h_raw:
        return None
    body_html = collect_article_html(soup, main)
    if not body_html.strip():
        return None
    body_clean = mig.clean_legacy(body_html)
    body_soup = BeautifulSoup(body_clean, "html.parser")
    blocks = build_blocks(body_soup)
    if not blocks:
        return None
    def block_has_portrait(b: Block) -> bool:
        if isinstance(b, ImageBlock):
            return b.figure.is_portrait
        if isinstance(b, FigureRowBlock):
            return any(f.is_portrait for f in b.figures)
        return False

    has_portrait = any(block_has_portrait(b) for b in blocks)
    cty, period = mig.build_meta(h_raw)
    h1_full = mig.h1_string(h_raw)
    return h1_full, blocks, has_portrait, cty, period


def page_html(
    num: int,
    h1_full: str,
    h1_short: str,
    blocks: list[Block],
    has_portrait: bool,
    cty: str,
    period: str | None,
) -> str:
    fn = f"taiken{num}.html"
    mod = "page-taiken-article--nepal" if "ネパール" in h1_full else "page-taiken-article--srilanka"
    natural = " page-taiken-blocks-natural" if has_portrait else ""
    all_paras: list[str] = []
    for b in blocks:
        if isinstance(b, TextBlock):
            all_paras.extend(b.paragraphs)
        elif isinstance(b, ImageBlock):
            all_paras.extend(b.paragraphs)
        elif isinstance(b, FigureRowBlock):
            pass
    desc = mig.plain_excerpt(BeautifulSoup("".join(all_paras), "html.parser"), 150)
    title = f"{h1_full} | Beインターナショナル"
    if len(title) > 110:
        title = f"{h1_full[:90]}… | Beインターナショナル"

    meta_lines = []
    if cty:
        meta_lines.append(f"          <li><strong>参加国</strong>：{html.escape(cty)}</li>")
    if period:
        meta_lines.append(f"          <li><strong>参加時期</strong>：{html.escape(period)}</li>")
    meta_block = "\n".join(meta_lines)

    art = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1_full,
        "inLanguage": "ja",
        "url": f"https://be-intl.com/{fn}",
        "description": desc,
        "isPartOf": {"@type": "WebSite", "name": "Beインターナショナル", "url": "https://be-intl.com/"},
    }
    json_ld = json.dumps(art, ensure_ascii=False, indent=2)
    indent_ld = "  " + json_ld.replace("\n", "\n  ")
    blocks_html = render_blocks(blocks)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
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
</head>
<body class="page-taiken-article {mod}{natural}">
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
        <a href="volunteer.html">ボランティア</a>
        <a href="program.html">料金</a>
        <a href="voices.html">参加者の声</a>
        <a href="living-basics.html">現地生活の基礎知識</a>
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
    <div class="taiken-head">
      <div class="layout-container">
        <h1 class="taiken-head__h1" id="taiken-h1">{html.escape(h1_short)}</h1>
        <ul class="taiken-meta">
{meta_block}
        </ul>
      </div>
    </div>

    <article class="taiken-article" aria-labelledby="taiken-h1">
      <div class="taiken-body taiken-body--blocks container">
        <div class="taiken-article__blocks">

{blocks_html}

        </div>

        <footer class="taiken-article__foot">
          <div class="taiken-article__actions">
            <a class="taiken-article__back" href="voices.html">参加者の声</a>
          </div>
        </footer>
      </div>
    </article>

    <section class="final-cta final-cta--accent" id="final-cta" aria-labelledby="final-cta-heading">
      <div class="layout-container">
        <h2 id="final-cta-heading">まずは気軽にご相談ください</h2>
        <p class="final-cta__btn">
          <a class="btn btn--accent" href="postmail.html">資料請求・お問い合わせはこちら</a>
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
  <script src="assets/js/back-to-top.js" defer></script>
  <script src="assets/js/card-visited.js" defer></script>
</body>
</html>
"""


def patch_blocks_natural(num: int) -> bool:
    """Add page-taiken-blocks-natural to existing blocks pages with portrait imgs in oldHP."""
    path = ROOT / f"taiken{num}.html"
    old = ROOT / "docs" / "oldHP" / f"taiken{num}.html"
    if not path.is_file() or not old.is_file():
        return False
    raw = path.read_text(encoding="utf-8", errors="replace")
    if "taiken-article__blocks" not in raw:
        return False
    if "page-taiken-blocks-natural" in raw:
        return False
    data = extract_from_old(num)
    if not data:
        return False
    _, _, has_portrait, _, _ = data
    if not has_portrait:
        return False
    new_raw = raw.replace(
        'class="page-taiken-article page-taiken-article--srilanka"',
        'class="page-taiken-article page-taiken-article--srilanka page-taiken-blocks-natural"',
    ).replace(
        'class="page-taiken-article page-taiken-article--nepal"',
        'class="page-taiken-article page-taiken-article--nepal page-taiken-blocks-natural"',
    )
    if new_raw == raw:
        return False
    path.write_text(new_raw, encoding="utf-8")
    return True


def restore_num(num: int, force: bool = False) -> str:
    path = ROOT / f"taiken{num}.html"
    old = ROOT / "docs" / "oldHP" / f"taiken{num}.html"
    if not old.is_file():
        return "no_old"
    data = extract_from_old(num)
    if not data:
        return "parse_fail"
    h1_full, blocks, has_portrait, cty, period = data
    if not force and path.is_file():
        from audit_taiken_vs_oldhp import new_article_text, old_article_text

        nt = new_article_text(path)
        ot = old_article_text(old)
        ratio = len(nt) / len(ot) if ot else 1.0
        raw = path.read_text(encoding="utf-8", errors="replace")
        needs_text = ratio < 0.75
        needs_natural = (
            "taiken-article__blocks" in raw
            and has_portrait
            and "page-taiken-blocks-natural" not in raw
        )
        if not needs_text and not needs_natural:
            return "skip_ok"

    h1_short = short_h1(h1_full)
    out = page_html(num, h1_full, h1_short, blocks, has_portrait, cty, period)
    path.write_text(out, encoding="utf-8")
    return "restored"


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    nums = DEFAULT_RANGE
    if args:
        nums = [int(x) for x in args]
    restored = patched = skipped = failed = 0
    for n in nums:
        old = ROOT / "docs" / "oldHP" / f"taiken{n}.html"
        if not old.is_file():
            continue
        r = restore_num(n, force=force)
        if r == "restored":
            restored += 1
            print(f"taiken{n}.html restored")
        elif r == "skip_ok":
            if patch_blocks_natural(n):
                patched += 1
                print(f"taiken{n}.html patched natural")
            else:
                skipped += 1
        else:
            failed += 1
            print(f"taiken{n}.html {r}", file=sys.stderr)
    print(f"DONE restored={restored} patched={patched} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
