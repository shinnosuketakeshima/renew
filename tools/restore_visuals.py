import csv
import re
import os

tsv_path = 'tools/taiken_seo_preview.tsv'
voices_path = 'voices.html'

def main():
    if not os.path.exists(tsv_path):
        print("TSV not found")
        return

    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    # 1. voices.html への属性追加
    if os.path.exists(voices_path):
        with open(voices_path, 'r', encoding='utf-8') as f:
            voices_html = f.read()

        for row in rows:
            name = row['name'].strip()
            attr = row['年代（空欄または 40代女性 等を入力）'].strip()
            if not attr:
                continue

            name_sama = f"{name}さま"
            old_td = f'<td class="taiken-index__cell-name">{name_sama}</td>'
            new_td = f'<td class="taiken-index__cell-name">{name_sama} <span class="taiken-index__attr">（{attr}）</span></td>'
            
            # Since some names might have different spaces like "R. D", 
            # let's be more robust with regex if exact match fails
            if old_td in voices_html:
                voices_html = voices_html.replace(old_td, new_td)
            else:
                # regex fallback
                pattern = r'<td class="taiken-index__cell-name">' + re.escape(name_sama) + r'</td>'
                voices_html = re.sub(pattern, new_td, voices_html)

        with open(voices_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(voices_html)
        print("Updated voices.html table visuals")

    # 2. taiken*.html へのH1修正
    for row in rows:
        filename = row['filename'].strip()
        name = row['name'].strip()
        attr = row['年代（空欄または 40代女性 等を入力）'].strip()
        
        if not os.path.exists(filename):
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()

        name_sama = f"{name}さま"
        
        if attr:
            # Not putting () for H1, as original diff showed `金子さま <span class="taiken-head__attr">30代男性</span>`
            h1_inner = f'{name_sama} <span class="taiken-head__attr">{attr}</span>'
        else:
            h1_inner = f'{name_sama}'

        # Currently the H1 is like:
        # <h1 class="taiken-head__h1" id="taiken-h1">【30代男性】スリランカ ホームステイ留学体験談（2004年7月）</h1>
        # Or something similar set by patch_taiken_seo.py
        
        # We replace the content of the H1 tag completely
        new_html = re.sub(
            r'(<h1\s+class="taiken-head__h1"\s+id="taiken-h1">).*?(</h1>)',
            rf'\g<1>{h1_inner}\g<2>',
            html,
            flags=re.DOTALL
        )
        
        if new_html != html:
            with open(filename, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_html)
            print(f"Updated H1 in {filename}")

if __name__ == '__main__':
    main()
