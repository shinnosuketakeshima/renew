# taiken1〜83: 旧 table 2 列の積み重ねを .taiken-article__blocks + .taiken-block へ
# 本文は子ノード移動で維持。該当する td 直下（同一親）の 1tr2td table のみ

from __future__ import annotations

import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent


def is_two_col_table(t: Tag) -> bool:
    if t.name != "table":
        return False
    trs = t.find_all("tr", recursive=False)
    if len(trs) != 1:
        return False
    tds = trs[0].find_all("td", recursive=False)
    return len(tds) == 2


def find_best_stacked_tables(root: Tag) -> list[Tag]:
    best: list[Tag] = []
    for td in root.find_all("td"):
        tables = [c for c in td.children if isinstance(c, Tag) and c.name == "table"]
        if len(tables) < 1:
            continue
        if not all(is_two_col_table(t) for t in tables):
            continue
        if len(tables) > len(best):
            best = list(tables)
    return best


def td_has_image(td: Tag) -> bool:
    return td.find("img", src=True) is not None


def _set_class(el: Tag, *classes: str) -> None:
    el["class"] = " ".join(classes)


def make_figure(soup: BeautifulSoup, td: Tag) -> Tag:
    fig = soup.new_tag("figure")
    _set_class(fig, "taiken-figure", "taiken-figure--block")
    im = td.find("img", src=True)
    if im:
        im = im.extract()
        if not im.get("alt"):
            im["alt"] = ""
        im["loading"] = "lazy"
        im["decoding"] = "async"
        if "height" in im.attrs:
            del im["height"]
        fig.append(im)
    for p in list(td.find_all("p", recursive=False)):
        if p.find("img") or p.find("picture"):
            continue
        if not p.get_text(strip=True):
            p.decompose()
            continue
        cap = soup.new_tag("figcaption")
        for ch in list(p.children):
            cap.append(ch.extract())
        p.decompose()
        if cap.get_text(strip=True):
            fig.append(cap)
    for p in list(td.find_all("p", recursive=False)):
        if not p.get_text(strip=True) and not p.find("img"):
            p.decompose()
    return fig


def make_text_block(soup: BeautifulSoup, td: Tag) -> Tag:
    box = soup.new_tag("div")
    _set_class(box, "taiken-block__text")
    for ch in list(td.children):
        box.append(ch.extract())
    return box


def build_block(soup: BeautifulSoup, table: Tag) -> Tag:
    tr = table.find("tr", recursive=False)
    assert tr is not None
    tds = tr.find_all("td", recursive=False)
    td0, td1 = tds[0], tds[1]
    h0, h1 = td_has_image(td0), td_has_image(td1)
    if h0 and not h1:
        b = soup.new_tag("div")
        _set_class(b, "taiken-block", "taiken-block--image-left")
        b["role"] = "group"
        b.append(make_figure(soup, td0))
        b.append(make_text_block(soup, td1))
    elif h1 and not h0:
        b = soup.new_tag("div")
        _set_class(b, "taiken-block", "taiken-block--image-right")
        b["role"] = "group"
        b.append(make_text_block(soup, td0))
        b.append(make_figure(soup, td1))
    elif h0 and h1:
        b = soup.new_tag("div")
        _set_class(b, "taiken-fig-row", "taiken-fig-row--2")
        b["role"] = "group"
        b.append(make_figure(soup, td0))
        b.append(make_figure(soup, td1))
    else:
        b = soup.new_tag("div")
        _set_class(b, "taiken-block", "taiken-block--split-text")
        b["role"] = "group"
        c0 = make_text_block(soup, td0)
        _set_class(c0, "taiken-block__text", "taiken-block__text--col")
        c1 = make_text_block(soup, td1)
        _set_class(c1, "taiken-block__text", "taiken-block__text--col")
        b.append(c0)
        b.append(c1)
    return b


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "taiken-legacy" not in text or "taiken-article__blocks" in text:
        return False
    soup = BeautifulSoup(text, "html.parser")
    body = soup.select_one("div.taiken-body.taiken-legacy")
    if not body:
        return False
    top_tables = [c for c in body.children if isinstance(c, Tag) and c.name == "table"]
    if not top_tables:
        return False
    first_table = top_tables[0]
    tables = find_best_stacked_tables(first_table)
    if len(tables) < 1:
        return False
    foot = body.find("footer", class_="taiken-article__foot")
    if not foot:
        return False
    before: list[Tag] = []
    for c in list(body.children):
        if c is foot:
            break
        if isinstance(c, NavigableString) and not str(c).strip():
            continue
        if isinstance(c, Tag):
            before.append(c)
    if first_table not in before:
        return False
    idx = before.index(first_table)
    head_part = before[:idx]
    tail_part = before[idx + 1 :]
    for n in list(body.children):
        if n is foot or (isinstance(n, Tag) and n.name == "footer"):
            break
        n.extract()
    wrap = soup.new_tag("div")
    _set_class(wrap, "taiken-article__blocks")
    for t in tables:
        wrap.append(build_block(soup, t))
    for h in head_part:
        body.append(h)
    body.append(wrap)
    for t in tail_part:
        body.append(t)
    body.append(foot)
    if body.get("class"):
        cl = [x for x in body["class"] if x != "taiken-legacy"]
    else:
        cl = []
    if "taiken-body" not in cl:
        cl.insert(0, "taiken-body")
    if "taiken-body--blocks" not in cl:
        cl.append("taiken-body--blocks")
    body["class"] = cl
    new_text = str(soup)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for i in range(1, 84):
        p = ROOT / f"taiken{i}.html"
        if not p.is_file():
            continue
        if process_file(p):
            n += 1
            print("converted", p.name, file=sys.stderr)
    print("TOTAL", n, file=sys.stderr)


if __name__ == "__main__":
    main()
