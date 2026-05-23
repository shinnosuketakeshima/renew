#!/usr/bin/env python3
"""
Convert legacy taiken*.html table-based layouts to modern div/flex layouts.
Converts HTML from .taiken-legacy with <table> to .taiken-body--blocks with modern structure.
"""

import re
import os
from pathlib import Path

# List of taiken files to convert (those with table layouts)
TAIKEN_FILES = [
    'taiken3.html', 'taiken4.html', 'taiken5.html', 'taiken6.html',
    'taiken7.html', 'taiken9.html', 'taiken10.html', 'taiken11.html',
    'taiken12.html', 'taiken13.html', 'taiken14.html', 'taiken15.html',
    'taiken16.html', 'taiken17.html', 'taiken20.html', 'taiken21.html',
    'taiken22.html', 'taiken23.html', 'taiken24.html'
]

def convert_taiken_file(filepath):
    """Convert a single taiken file from table to modern layout."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already converted (has taiken-body--blocks)
    if 'taiken-body--blocks' in content:
        print(f"[OK] {Path(filepath).name} - Already converted")
        return False

    # Replace the taiken-legacy body wrapper with modern structure
    # Match: <div class="taiken-body taiken-legacy"> ... </div>
    old_body_pattern = r'<div class="taiken-body taiken-legacy">(.*?)</div>\s*</article>'

    def replace_body(match):
        inner_content = match.group(1)

        # Extract article content and convert tables to blocks
        converted_content = convert_tables_to_blocks(inner_content)

        return f'''<div class="taiken-body taiken-body--blocks">
        <div class="taiken-article__blocks">
{converted_content}
        </div>
      </div>

      <footer class="taiken-article__foot">
        <div class="taiken-article__actions">
          <a class="taiken-article__back" href="voices.html">参加者の声</a>
        </div>
      </footer>
    </article>'''

    content_new = re.sub(old_body_pattern, replace_body, content, flags=re.DOTALL)

    # If no replacement was made, try simpler pattern
    if content_new == content:
        # Try alternate pattern without the closing tag
        old_body_pattern = r'<div class="taiken-body taiken-legacy">(.*)'
        def replace_body_alt(match):
            inner_content = match.group(1)
            converted_content = convert_tables_to_blocks(inner_content)

            return f'''<div class="taiken-body taiken-body--blocks">
        <div class="taiken-article__blocks">
{converted_content}
        </div>
      </div>

      <footer class="taiken-article__foot">
        <div class="taiken-article__actions">
          <a class="taiken-article__back" href="voices.html">参加者の声</a>
        </div>
      </footer>'''

        content_new = re.sub(old_body_pattern, replace_body_alt, content, flags=re.DOTALL)

    if content_new == content:
        print(f"[WARN] {Path(filepath).name} - No conversion pattern matched")
        return False

    # Add missing closing </article> and footer if needed
    if '</article>' not in content_new and '<footer' in content_new:
        content_new += '\n    </article>'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_new)

    print(f"[OK] {Path(filepath).name} - Converted")
    return True

def convert_tables_to_blocks(html):
    """Convert table elements to div-based block structure."""

    # Remove <table>, <tbody>, </tbody>, </table> tags
    html = re.sub(r'</?table[^>]*>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'</?tbody[^>]*>', '', html, flags=re.IGNORECASE | re.DOTALL)

    # Convert table rows to appropriate block elements
    # Split by <tr> tags
    blocks = []
    current_pos = 0

    for match in re.finditer(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE):
        # Add any text before this <tr>
        before_text = html[current_pos:match.start()].strip()
        if before_text:
            blocks.append(f'          <div>\n{before_text}\n          </div>')

        row_content = match.group(1)

        # Extract <td> cells
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_content, re.DOTALL | re.IGNORECASE)

        if len(cells) == 1:
            # Single cell - treat as text block or figure block
            cell_text = cells[0].strip()

            # Check if it contains an image
            if '<img' in cell_text:
                # Image cell
                blocks.append(convert_cell_to_figure(cell_text))
            else:
                # Text cell
                blocks.append(f'          <div>\n{cell_text}\n          </div>')

        elif len(cells) == 2:
            # Two cells - could be img+text or text+img
            cell1 = cells[0].strip()
            cell2 = cells[1].strip()

            has_img1 = '<img' in cell1
            has_img2 = '<img' in cell2

            if has_img1 and has_img2:
                # Two images - taiken-fig-row--2
                blocks.append(f'''          <div class="taiken-fig-row taiken-fig-row--2">
{convert_cell_to_figure(cell1, in_row=True)}
{convert_cell_to_figure(cell2, in_row=True)}
          </div>''')
            elif has_img1:
                # Image left, text right
                blocks.append(f'''          <div class="taiken-block taiken-block--image-left">
{convert_cell_to_figure(cell1, in_block=True)}
            <div>
{cell2}
            </div>
          </div>''')
            elif has_img2:
                # Text left, image right
                blocks.append(f'''          <div class="taiken-block taiken-block--image-right">
            <div>
{cell1}
            </div>
{convert_cell_to_figure(cell2, in_block=True)}
          </div>''')
            else:
                # Two text cells
                blocks.append(f'''          <div class="taiken-block taiken-block--split-text">
            <div>{cell1}</div>
            <div>{cell2}</div>
          </div>''')

        current_pos = match.end()

    # Add any remaining content after the last <tr>
    remaining = html[current_pos:].strip()
    if remaining:
        blocks.append(f'          <div>\n{remaining}\n          </div>')

    return '\n\n'.join(blocks)

def convert_cell_to_figure(cell_content, in_row=False, in_block=False):
    """Convert a table cell containing image(s) to modern figure element."""

    # Extract image and caption
    img_match = re.search(r'<img\s+([^>]*?)/?>', cell_content, re.IGNORECASE)
    if not img_match:
        return cell_content

    img_attrs = img_match.group(1)

    # Extract src
    src_match = re.search(r'src=["\']([^"\']*)["\']', img_attrs, re.IGNORECASE)
    src = src_match.group(1) if src_match else ''

    # Extract alt
    alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_attrs, re.IGNORECASE)
    alt = alt_match.group(1) if alt_match else ''

    # Extract caption from cell content (text between </img> and </td>, or from <p class="style2">)
    caption_match = re.search(r'<p[^>]*class=["\']style2["\'][^>]*>([^<]*)</p>', cell_content, re.IGNORECASE)
    caption = caption_match.group(1).strip() if caption_match else ''

    # If no caption found, look for any text after the image
    if not caption:
        after_img = cell_content[img_match.end():]
        text_match = re.search(r'>([^<]+)<', after_img)
        if text_match:
            caption = text_match.group(1).strip()

    # Build figure element
    indent = '            ' if in_block else '            ' if in_row else '            '

    if in_row:
        indent = '            '
        return f'''{indent}<figure class="taiken-figure">
{indent}  <img src="{src}" alt="{alt}" loading="lazy">
{indent}  <figcaption>{caption}</figcaption>
{indent}</figure>'''
    elif in_block:
        indent = '            '
        return f'''{indent}<figure class="taiken-figure taiken-figure--block">
{indent}  <img src="{src}" alt="{alt}" loading="lazy">
{indent}  <figcaption>{caption}</figcaption>
{indent}</figure>'''
    else:
        return f'''            <figure class="taiken-figure">
              <img src="{src}" alt="{alt}" loading="lazy">
              <figcaption>{caption}</figcaption>
            </figure>'''

def main():
    repo_root = Path(__file__).parent.parent

    converted_count = 0
    for filename in TAIKEN_FILES:
        filepath = repo_root / filename
        if filepath.exists():
            if convert_taiken_file(filepath):
                converted_count += 1
        else:
            print(f"[FAIL] {filename} - File not found")

    print(f"\n[DONE] Converted {converted_count}/{len(TAIKEN_FILES)} files")

if __name__ == '__main__':
    main()
