import os
import re

TEMPLATES_DIR = 'System/templates'

def clean_template(content, file_path):
    orig = content
    
    # 1. Replace glass-card CSS linear-gradient & box-shadow
    content = re.sub(
        r'\.glass-card\s*\{[^}]*\}',
        '''.glass-card {
        background-color: #022118;
        border: 1px solid rgba(255, 255, 255, 0.10);
        box-shadow: none;
    }''',
        content
    )
    
    # 2. Replace linear-gradient & radial-gradient in inline styles
    content = re.sub(r'background:\s*linear-gradient\([^;]+;\s*', 'background-color: #022118; ', content)
    content = re.sub(r'background:\s*radial-gradient\([^;]+;\s*', 'background-color: #01140e; ', content)
    content = re.sub(r'style="background:\s*linear-gradient\([^"]+\)"', 'style="background-color: #01140e;"', content)
    content = re.sub(r'style="background:\s*radial-gradient\([^"]+\)"', 'style="background-color: #01140e;"', content)
    
    # 3. Replace Tailwind gradient classes
    # bg-gradient-to-r, bg-gradient-to-br, bg-gradient-to-b, bg-gradient-to-tl, etc.
    content = re.sub(r'\bbg-gradient-to-[a-z]+\b', '', content)
    content = re.sub(r'\bfrom-\[[^\]]+\]\b', '', content)
    content = re.sub(r'\bto-\[[^\]]+\]\b', '', content)
    content = re.sub(r'\bvia-\[[^\]]+\]\b', '', content)
    content = re.sub(r'\bfrom-[a-z0-9\-/]+', '', content)
    content = re.sub(r'\bto-[a-z0-9\-/]+', '', content)
    content = re.sub(r'\bvia-[a-z0-9\-/]+', '', content)
    
    # 4. Remove shadow classes from class attributes
    # shadow-sm, shadow-md, shadow-lg, shadow-xl, shadow-2xl, shadow-[...], shadow-emerald-..., shadow-[#...]/...
    content = re.sub(r'\bshadow-\[[^\]]+\]', '', content)
    content = re.sub(r'\bshadow-(?:2xl|xl|lg|md|sm|inner|none)\b', '', content)
    content = re.sub(r'\bshadow\b', '', content)
    content = re.sub(r'\bshadow-[a-z0-9\-/]+', '', content)
    content = re.sub(r'\bshadow-\[[^\]]+\]/[0-9]+', '', content)
    
    # 5. Remove box-shadow in <style> tags
    content = re.sub(r'box-shadow:\s*[^;]+;', 'box-shadow: none;', content)
    
    # 6. Clean up multiple spaces inside class="..."
    def clean_classes(m):
        cls_str = m.group(1)
        cleaned = ' '.join(cls_str.split())
        return f'class="{cleaned}"'
    
    content = re.sub(r'class="([^"]*)"', clean_classes, content)
    
    return content

def run():
    modified_count = 0
    total_files = 0
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for f in files:
            if f.endswith('.html'):
                total_files += 1
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8') as fh:
                    orig_content = fh.read()
                
                new_content = clean_template(orig_content, fpath)
                if new_content != orig_content:
                    with open(fpath, 'w', encoding='utf-8') as fh:
                        fh.write(new_content)
                    modified_count += 1
                    print(f"Updated: {fpath.replace(os.sep, '/')}")

    print(f"\nProcessing complete: {modified_count}/{total_files} HTML files updated to solid colors with no shadows.")

if __name__ == '__main__':
    run()
