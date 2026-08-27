import os
from pathlib import Path

replacements = [
    ("'operations.", "'operations."),
    ('"operations.', '"operations.'),
    ("'stock.", "'stock."),
    ('"stock.', '"stock.'),
]

def replace_in_files(directory, replacements, extensions=('.py',)):
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
                        print(f'Updated ForeignKey refs in: {filepath}')
                except Exception as e:
                    pass

replace_in_files(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\System', replacements)
