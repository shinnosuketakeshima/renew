import os
import re

# Standard external JS path
JS_REPLACEMENT = '<script src="assets/js/site-header-nav.js" defer></script>'

# A more generic pattern that matches various versions of the navigation script
GENERIC_NAV_PATTERN = re.compile(
    r'<script>\s*\(function \(\) \{.*?(?:var header|var h) = document\.querySelector\(\'\.site-header\'\).*?\}\)\(\);\s*</script>',
    re.MULTILINE | re.DOTALL
)

def update_files():
    count = 0
    for root, dirs, files in os.walk('.'):
        if 'node_modules' in dirs: dirs.remove('node_modules')
        if '.git' in dirs: dirs.remove('.git')
        if 'test2' in dirs: dirs.remove('test2')
        
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                # Skip files that already have the JS_REPLACEMENT
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if JS_REPLACEMENT in content:
                    continue
                
                # Special handling for taiken.html as it has filtering logic
                if file == 'taiken.html':
                    continue

                new_content = GENERIC_NAV_PATTERN.sub(JS_REPLACEMENT, content)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {path}")
                    count += 1
    print(f"Total updated: {count}")

if __name__ == "__main__":
    update_files()
