#!/usr/bin/env python3
"""Write sitemap.xml at repo root. Excludes filenames listed in tools/data/seo-root-pages.json.
Supports priority and changefreq per page via the 'priorities' mapping in the same config."""
from __future__ import annotations

import datetime
import json
import re
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
    priorities: dict[str, dict] = cfg.get("priorities", {})
    default_priority = cfg.get("defaultPriority", "0.5")
    default_changefreq = cfg.get("defaultChangefreq", "monthly")
    taiken_priority = cfg.get("taikenPriority", "0.5")
    taiken_changefreq = cfg.get("taikenChangefreq", "yearly")

    taiken_re = re.compile(r"^taiken\d+\.html$")

    entries: list[dict] = []
    for p in sorted(REPO.glob("*.html")):
        if p.name in exclude:
            continue
        if p.name == "index.html":
            loc = f"{base}/"
        else:
            loc = f"{base}/{quote(p.name)}"

        if p.name in priorities:
            prio = priorities[p.name]["priority"]
            freq = priorities[p.name]["changefreq"]
        elif taiken_re.match(p.name):
            prio = taiken_priority
            freq = taiken_changefreq
        else:
            prio = default_priority
            freq = default_changefreq

        entries.append({"loc": loc, "priority": prio, "changefreq": freq})

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today = datetime.date.today().isoformat()
    for e in entries:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = e["loc"]
        ET.SubElement(u, "lastmod").text = today
        ET.SubElement(u, "changefreq").text = e["changefreq"]
        ET.SubElement(u, "priority").text = e["priority"]

    out = REPO / "sitemap.xml"
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(out, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {out} ({len(entries)} URLs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
