import os
from pathlib import Path

def replace_in_files(directory, replacements, extensions=('.py', '.html', '.md')):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                filepath = Path(root) / file
                try:
                    content = filepath.read_text(encoding='utf-8')
                    original_content = content
                    for old, new in replacements:
                        content = content.replace(old, new)
                    
                    if content != original_content:
                        filepath.write_text(content, encoding='utf-8')
                        print(f"Updated: {filepath}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

replacements = [
    # Python imports and INSTALLED_APPS
    ("apps.stock", "apps.stock"),
    ("apps.operations", "apps.operations"),
    
    # URL tags and namespaces
    ("url 'stock:", "url 'stock:"),
    ("url 'operations:", "url 'operations:"),
    ("namespace='stock'", "namespace='stock'"),
    ("namespace='operations'", "namespace='operations'"),
    
    # URL prefixes (urls.py)
    ("path('stock/", "path('stock/"),
    ("path('operations/", "path('operations/"),
]

project_dir = r"c:\Users\kymer\Desktop\Lantad ACarwfish Django\System"
replace_in_files(project_dir, replacements)
