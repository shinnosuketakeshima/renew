"""
patch_taiken_seo.py  — taiken SEO一括パッチ

使い方:
  python tools/patch_taiken_seo.py --dry-run   差分を標準出力で確認（ファイル変更なし）
  python tools/patch_taiken_seo.py --apply     実際にファイルを書き換え

TSVの各列:
  filename / country / name / date /
  current_title / proposed_title /
  current_desc  / proposed_desc  /
  年代（空欄または 40代女性 等）
"""

import re
import json
import csv
import argparse
import difflib
from pathlib import Path

ROOT     = Path(__file__).resolve().parents[1]
TSV_PATH = ROOT / "tools" / "taiken_seo_preview.tsv"

TRAVEL_AGENCY_LD = {
    "@context": "https://schema.org",
    "@type": "TravelAgency",
    "@id": "https://be-intl.com/#organization",
    "name": "Beインターナショナル",
    "alternateName": "Be International",
    "url": "https://be-intl.com/",
    "image": "https://be-intl.com/SriLankaPhotos/CoconutP1011106.JPG",
    "description": "スリランカ・ネパールでのホームステイとマンツーマン英語レッスンを組み合わせたアジア語学留学。22年の運営実績。",
    "foundingDate": "2004",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "幡ヶ谷1-23-19 サンハイムミヤタ2F",
        "addressLocality": "渋谷区",
        "addressRegion": "東京都",
        "postalCode": "151-0072",
        "addressCountry": "JP"
    },
    "geo": {"@type": "GeoCoordinates", "latitude": "35.680", "longitude": "139.676"},
    "telephone": "+81-3-6770-6191",
    "email": "info@be-intl.com",
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+81-3-6770-6191",
        "contactType": "customer service",
        "email": "info@be-intl.com",
        "availableLanguage": "Japanese"
    }
}


def ld_block(obj: dict) -> str:
    return (
        '  <script type="application/ld+json">\n'
        + "  " + json.dumps(obj, ensure_ascii=False, indent=2).replace("\n", "\n  ")
        + "\n  </script>"
    )


def build_h1(age: str, country: str, date: str) -> str:
    """年代・国・参加時期 → H1テキスト生成"""
    # 日付は最初の区切り（～ , ・）前だけ使う
    date_short = re.split(r"[～,・]", date)[0].strip()
    if country == "スリランカ":
        label = "ホームステイ留学体験談"
    else:
        label = "英語留学・ボランティア体験談"
    prefix = f"【{age}】" if age else ""
    return f"{prefix}{country} {label}（{date_short}）"


def patch(content: str, filename: str, row: dict) -> str:
    proposed_title = row["proposed_title"].strip()
    proposed_desc  = row["proposed_desc"].strip()
    age            = row.get("年代（空欄または 40代女性 等を入力）", "").strip()
    country        = row["country"].strip()
    date           = row["date"].strip()
    name           = row["name"].strip()
    h1_text        = build_h1(age, country, date)

    # ── 1. <title> ──────────────────────────────────────────────────────────
    content = re.sub(
        r"<title>.*?</title>",
        f"<title>{proposed_title}</title>",
        content,
        flags=re.DOTALL
    )

    # ── 2. <meta name="description"> ───────────────────────────────────────
    content = re.sub(
        r'<meta name="description" content=".*?">',
        f'<meta name="description" content="{proposed_desc}">',
        content
    )

    # ── 3. H1 ───────────────────────────────────────────────────────────────
    content = re.sub(
        r'(<h1\s[^>]*id="taiken-h1"[^>]*>).*?(</h1>)',
        rf"\g<1>{h1_text}\g<2>",
        content,
        flags=re.DOTALL
    )

    # ── 4. Article JSON-LD の headline / description を更新 ─────────────────
    def _update_article(m: re.Match) -> str:
        try:
            obj = json.loads(m.group(1))
            if obj.get("@type") == "Article":
                obj["headline"]    = proposed_title
                obj["description"] = proposed_desc
                return ld_block(obj)
        except Exception:
            pass
        return m.group(0)

    content = re.sub(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        _update_article,
        content,
        flags=re.DOTALL
    )

    # ── 5. Organization → TravelAgency に差し替え ───────────────────────────
    content = re.sub(
        r'<script type="application/ld\+json">\s*\{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"Organization".*?\}\s*</script>',
        ld_block(TRAVEL_AGENCY_LD),
        content,
        flags=re.DOTALL
    )

    # ── 6. BreadcrumbList + Review を </head> 直前に挿入（重複防止） ──────────
    if '"BreadcrumbList"' not in content:
        breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "トップ",      "item": "https://be-intl.com/"},
                {"@type": "ListItem", "position": 2, "name": "参加者の声",  "item": "https://be-intl.com/voices.html"},
                {"@type": "ListItem", "position": 3, "name": h1_text,       "item": f"https://be-intl.com/{filename}"}
            ]
        }
        review = {
            "@context": "https://schema.org",
            "@type": "Review",
            "author":       {"@type": "Person", "name": f"{name}さま"},
            "reviewBody":   proposed_desc,
            "itemReviewed": {
                "@type":    "Service",
                "name":     f"{country}留学プログラム（ホームステイ＋マンツーマン英語レッスン）",
                "provider": {"@id": "https://be-intl.com/#organization"}
            }
        }
        injection = "\n" + ld_block(breadcrumb) + "\n" + ld_block(review) + "\n"
        content = content.replace("</head>", f"{injection}</head>")

    return content


def run(dry_run: bool) -> None:
    if not TSV_PATH.exists():
        print(f"ERROR: TSVが見つかりません → {TSV_PATH}")
        return

    with open(TSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    changed = 0
    for row in rows:
        filename  = row["filename"].strip()
        file_path = ROOT / filename
        if not file_path.exists():
            print(f"SKIP (not found): {filename}")
            continue

        original = file_path.read_text(encoding="utf-8-sig")
        patched  = patch(original, filename, row)

        if patched == original:
            print(f"  no-op : {filename}")
            continue

        if dry_run:
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                patched.splitlines(keepends=True),
                fromfile=f"a/{filename}",
                tofile=f"b/{filename}",
                n=2
            )
            print("".join(diff))
        else:
            file_path.write_text(patched, encoding="utf-8-sig", newline="\n")
            print(f"  patched: {filename}")
            changed += 1

    if not dry_run:
        print(f"\n完了: {changed}件 更新しました。")


def main() -> None:
    parser = argparse.ArgumentParser(description="taiken SEO一括パッチ")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="差分を表示するだけ（ファイル変更なし）")
    group.add_argument("--apply",   action="store_true", help="実際にファイルを書き換え")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
