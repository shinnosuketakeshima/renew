import os
import re

def refactor_html(content):
    # 1. Remove font tags
    content = re.sub(r'<(?:/)?font[^>]*>', '', content)
    
    # 2. Remove spacer.gif and its containers if they are just for spacing
    content = re.sub(r'<img[^>]*spacer\.gif[^>]*>', '', content)
    
    # 3. Remove legacy table attributes
    content = re.sub(r'\s+(?:width|height|border|cellpadding|cellspacing|align|valign|bgcolor|leftmargin|topmargin|marginwidth|marginheight|background|text|onload)="[^"]*"', '', content)
    
    # 4. Remove empty spans or other junk
    content = re.sub(r'<span class="style2">\s*</span>', '', content)
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'<br\s*/?>\s*<br\s*/?>', '<br>', content) # Reduce double breaks
    
    # 5. Replace legacy tags
    content = content.replace('<b>', '<strong>').replace('</b>', '</strong>')
    content = content.replace('<i>', '<em>').replace('</i>', '</em>')
    
    # 6. Specific cleanup for taiken tables
    # If the table is inside taiken-legacy, we keep it as table for now because CSS handles it,
    # but we clean up its attributes.
    
    return content

def process_files():
    count = 0
    for file in os.listdir('.'):
        if file.startswith('taiken') and file.endswith('.html') and file != 'taiken.html':
            path = file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it has legacy elements
            if any(x in content for x in ['<font', 'spacer.gif', 'width=', 'height=', 'cellpadding=']):
                new_content = refactor_html(content)
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Refactored: {path}")
                    count += 1
    print(f"Total refactored: {count}")

if __name__ == "__main__":
    process_files()
