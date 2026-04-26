#!/usr/bin/env python3
"""Write sitemap.xml at repo root. Excludes filenames listed in tools/data/seo-root-pages.json."""
from __future__ import annotations

import datetime
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[1]
CFG = REPO / "tools" / "data" / "seo-root-pages.json"


def main() -> int:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    base = str(cfg["baseUrl"]).rstrip("/")
    exclude = set(cfg.get("excludeFromSitemap", []))

    urls: list[str] = []
    for p in sorted(REPO.glob("*.html")):
        if p.name in exclude:
            continue
        if p.name == "index.html":
            urls.append(f"{base}/")
        else:
            urls.append(f"{base}/{quote(p.name)}")

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today = datetime.date.today().isoformat()
    for loc in urls:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = loc
        ET.SubElement(u, "lastmod").text = today

    out = REPO / "sitemap.xml"
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(out, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {out} ({len(urls)} URLs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
