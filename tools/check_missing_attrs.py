import csv
import re
import unicodedata

tsv_path = 'tools/taiken_seo_preview.tsv'

def normalize(text):
    text = unicodedata.normalize('NFKC', text)
    text = text.replace(' ', '').replace('　', '')
    text = text.replace('.', '').replace('．', '')
    text = text.replace('さま', '')
    return text.upper()

missing_names = [
    "Ｒ. Ｄさま",
    "Ｓ. Iさま",
    "Ｔ. Ｎさま",
    "Ｙ. Ｔさま",
    "Ｎ. Ｏさま",
    "Ｔ．Ｒさま",
    "松本直素さま"
]

with open(tsv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

mapping = {}

for name in missing_names:
    norm_name = normalize(name)
    found = False
    for row in rows:
        norm_row = normalize(row['name'])
        if norm_name == norm_row:
            print(f"Found {name}: {row['年代（空欄または 40代女性 等を入力）']}")
            mapping[name] = row['年代（空欄または 40代女性 等を入力）']
            found = True
            break
    if not found:
        print(f"NOT FOUND: {name}")

# Try to find 松本直素さま in old backup if it exists
import os
old_backup = 'docs/oldHP/taiken-legacy-root-backup.html'
if os.path.exists(old_backup):
    with open(old_backup, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
        if '松本直素' in html:
            # Try to see if there's an attribute near it
            idx = html.find('松本直素')
            print("Context for 松本直素:", html[idx-50:idx+50])
