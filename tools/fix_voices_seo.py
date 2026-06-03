import csv
import json
import re
import os
from bs4 import BeautifulSoup

def convert_to_iso_date(date_str):
    match = re.search(r'(\d{4})年(\d{1,2})月', date_str)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        return f"{year}-{month}"
    return None

def process_voices():
    voices_path = 'voices.html'
    if not os.path.exists(voices_path):
        return

    with open(voices_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # If ItemList doesn't exist, inject it.
    if '"ItemList"' not in html:
        item_list = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "スリランカ・ネパール留学 体験談一覧",
            "numberOfItems": 84
        }
        json_str = json.dumps(item_list, indent=2, ensure_ascii=False)
        lines = json_str.split('\n')
        indented_lines = ['  ' + line for line in lines]
        script_str = '\n  <script type="application/ld+json">\n' + '\n'.join(indented_lines) + '\n  </script>\n'
        html = html.replace('</head>', script_str + '</head>')
        
        with open(voices_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print("Modified voices.html (Added ItemList)")

def main():
    process_voices()

if __name__ == '__main__':
    main()
