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

def insert_after_key(d, target_key, new_items):
    new_d = {}
    for k, v in d.items():
        new_d[k] = v
        if k == target_key:
            for nk, nv in new_items.items():
                new_d[nk] = nv
    if target_key not in d:
        for nk, nv in new_items.items():
            new_d[nk] = nv
    return new_d

def insert_before_key(d, target_key, new_items):
    new_d = {}
    if target_key not in d:
        for k, v in d.items():
            new_d[k] = v
        for nk, nv in new_items.items():
            new_d[nk] = nv
        return new_d
        
    for k, v in d.items():
        if k == target_key:
            for nk, nv in new_items.items():
                new_d[nk] = nv
        new_d[k] = v
    return new_d

def process_voices():
    voices_path = 'voices.html'
    if not os.path.exists(voices_path):
        print(f"File not found: {voices_path}")
        return

    with open(voices_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    modified = False
    
    # We will operate on a copy of the html string
    out_html = html
    
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            original_string = script.string
            if not original_string:
                continue
                
            js_data = json.loads(original_string)
            if isinstance(js_data, dict) and js_data.get('@type') == 'ItemList':
                if 'numberOfItems' not in js_data:
                    js_data = insert_after_key(js_data, '@type', {'numberOfItems': 84})
                    json_str = json.dumps(js_data, indent=2, ensure_ascii=False)
                    lines = json_str.split('\n')
                    indented_lines = ['  ' + line for line in lines]
                    new_string = '\n' + '\n'.join(indented_lines) + '\n  '
                    
                    # replace the exact block in the HTML string
                    # original block might have spaces, we can replace the whole tag to fix indentation
                    old_tag = str(script)
                    # we want to create a new tag with proper indentation
                    new_tag = f'<script type="application/ld+json">{new_string}</script>'
                    
                    # Instead of replacing just the string, let's find the tag in out_html and replace it.
                    # We will use regex to find the script tag containing the original_string
                    # Escape the original string carefully
                    escaped_old = re.escape(old_tag)
                    # But beautifulsoup's str(script) might not perfectly match original HTML if attributes were ordered differently.
                    # Actually, if we just use string replacement on original_string:
                    out_html = out_html.replace(original_string, new_string)
                    modified = True
        except Exception as e:
            pass

    if modified:
        # Fix indentation of the <script> tags:
        out_html = re.sub(r'^[ \t]*<script type="application/ld\+json">', '  <script type="application/ld+json">', out_html, flags=re.MULTILINE)
        out_html = re.sub(r'^[ \t]*</script>', '  </script>', out_html, flags=re.MULTILINE)
        
        with open(voices_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out_html)
        print(f"Modified {voices_path} (Added numberOfItems)")

def process_taiken(filename, rules):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    review_body = rules['proposed_desc']
    article = soup.find('article', class_='taiken-article')
    if article:
        for p in article.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) >= 30:
                review_body = text[:250]
                break

    modified = False
    out_html = html
    
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            original_string = script.string
            if not original_string:
                continue
                
            js_data = json.loads(original_string)
            if not isinstance(js_data, dict):
                continue
                
            t = js_data.get('@type')
            changed_this_script = False
            
            if t == 'Article':
                if 'author' not in js_data:
                    new_items = {"author": {"@type": "Person", "name": rules['name']}}
                    if rules['iso_date']:
                        new_items["datePublished"] = rules['iso_date']
                    js_data = insert_after_key(js_data, 'description', new_items)
                    changed_this_script = True
                    
            elif t == 'Review':
                if 'reviewRating' not in js_data:
                    new_items = {
                        "reviewRating": {
                            "@type": "Rating",
                            "ratingValue": 5,
                            "bestRating": 5,
                            "worstRating": 1
                        }
                    }
                    if rules['iso_date']:
                        new_items["datePublished"] = rules['iso_date']
                    js_data = insert_before_key(js_data, 'author', new_items)
                    changed_this_script = True
                
                if js_data.get('reviewBody') != review_body:
                    js_data['reviewBody'] = review_body
                    changed_this_script = True
                    
            elif t == 'TravelAgency':
                if 'image' in js_data:
                    del js_data['image']
                    changed_this_script = True
                if 'description' in js_data:
                    desc = js_data['description']
                    new_desc = desc.replace('21年の運営実績', '22年の運営実績').replace('21年', '22年')
                    if new_desc != desc:
                        js_data['description'] = new_desc
                        changed_this_script = True
                        
            if changed_this_script:
                json_str = json.dumps(js_data, indent=2, ensure_ascii=False)
                lines = json_str.split('\n')
                indented_lines = ['  ' + line for line in lines]
                new_string = '\n' + '\n'.join(indented_lines) + '\n  '
                
                # simple replacement of the contents
                out_html = out_html.replace(original_string, new_string)
                modified = True
                
        except Exception as e:
            pass

    if modified:
        # Fix indentation of the <script> tags themselves
        # Only target the tags for application/ld+json
        # We need to make sure we don't mess up inline js </script> tags.
        # It's safer to just fix the whole tag structure using regex replacement on the blocks
        
        # Regex to match <script type="application/ld+json">...</script>
        # and normalize its indentation to 2 spaces.
        def replacer(match):
            content = match.group(1)
            return f'  <script type="application/ld+json">{content}</script>'
            
        out_html = re.sub(r'^[ \t]*<script type="application/ld\+json">(.*?)</script>', replacer, out_html, flags=re.MULTILINE | re.DOTALL)
        
        with open(filename, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out_html)
        print(f"Modified {filename}")

def main():
    tsv_path = 'tools/taiken_seo_preview.tsv'
    if not os.path.exists(tsv_path):
        print(f"TSV file not found: {tsv_path}")
        return
        
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        data = list(reader)

    process_voices()

    for row in data:
        rules = {
            'name': row['name'] + 'さま',
            'date': row['date'],
            'iso_date': convert_to_iso_date(row['date']),
            'proposed_desc': row['proposed_desc']
        }
        process_taiken(row['filename'], rules)

if __name__ == '__main__':
    main()
