import re

html_path = 'voices.html'

mapping = {
    "Ｒ. Ｄさま": "20代女性",
    "Ｓ. Iさま": "40代女性",
    "Ｔ. Ｎさま": "20代男性",
    "Ｙ. Ｔさま": "30代女性",
    "Ｎ. Ｏさま": "30代女性",
    "Ｔ．Ｒさま": "30代女性"
}

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

for name, attr in mapping.items():
    # Looking for: <td class="taiken-index__cell-name">Ｒ. Ｄさま</td>
    # Replace with: <td class="taiken-index__cell-name">Ｒ. Ｄさま <span class="taiken-index__attr">（20代女性）</span></td>
    
    old_td = f'<td class="taiken-index__cell-name">{name}</td>'
    new_td = f'<td class="taiken-index__cell-name">{name} <span class="taiken-index__attr">（{attr}）</span></td>'
    
    html = html.replace(old_td, new_td)

with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

print("Voices patched.")
