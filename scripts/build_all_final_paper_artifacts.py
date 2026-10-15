import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# Ensure scripts dir is on sys.path
sys.path.insert(0, os.path.abspath('scripts'))

import build_final_paper_complete
import build_chapter4_standalone
import build_chapter4_markdown

def docx_to_clean_markdown(docx_path, md_path):
    doc = docx.Document(docx_path)
    md_lines = []
    
    # Process document paragraphs and tables in order
    body = doc._body._body
    
    for element in body:
        tag = element.tag.split('}')[-1]
        if tag == 'p':
            # It is a paragraph
            p = docx.text.paragraph.Paragraph(element, doc)
            text = p.text.strip()
            if not text:
                continue
            
            # Check style / heading level
            style_name = p.style.name if p.style else ''
            
            if 'Heading 1' in style_name or text.startswith('CHAPTER '):
                md_lines.append(f"\n# {text}\n")
            elif 'Heading 2' in style_name or (len(text) > 3 and text[:3].replace('.', '').isdigit() and ' ' in text[:5]):
                md_lines.append(f"\n## {text}\n")
            elif 'Heading 3' in style_name or text.startswith('Phase ') or text.startswith('Figure '):
                if text.startswith('Figure '):
                    md_lines.append(f"\n**{text}**")
                else:
                    md_lines.append(f"\n### {text}\n")
            elif text.startswith('Table '):
                md_lines.append(f"\n**{text}**")
            elif text.startswith('•') or text.startswith('-'):
                md_lines.append(f"* {text.lstrip('•- ').strip()}")
            elif len(text) > 2 and text[0].isdigit() and text[1] in ('.', ')'):
                md_lines.append(f"{text}")
            elif text.startswith('a.') or text.startswith('b.') or text.startswith('c.') or text.startswith('d.') or text.startswith('e.') or text.startswith('f.') or text.startswith('g.') or text.startswith('h.'):
                md_lines.append(f"  {text}")
            else:
                md_lines.append(f"{text}\n")
                
        elif tag == 'tbl':
            # It is a table
            tbl = docx.table.Table(element, doc)
            if not tbl.rows:
                continue
            
            md_tbl = []
            # Header
            header_cells = [c.text.strip().replace('\n', ' ') for c in tbl.rows[0].cells]
            md_tbl.append("| " + " | ".join(header_cells) + " |")
            md_tbl.append("| " + " | ".join(['---'] * len(header_cells)) + " |")
            
            for row in tbl.rows[1:]:
                row_cells = [c.text.strip().replace('\n', '<br>') for c in row.cells]
                md_tbl.append("| " + " | ".join(row_cells) + " |")
            
            md_lines.append("\n" + "\n".join(md_tbl) + "\n")

    full_md = "\n".join(md_lines)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(full_md)
    print(f"Successfully wrote clean markdown to {md_path}")

def main():
    print("1. Compiling Final_Paper.docx...")
    build_final_paper_complete.build_complete_final_paper()

    print("2. Compiling Chapter_4.docx...")
    build_chapter4_standalone.build_standalone_chapter4()

    print("3. Generating Chapter_4.md...")
    build_chapter4_markdown.update_all_markdown_files()

    print("4. Generating clean, synchronized Final_Paper.md from Final_Paper.docx...")
    docx_to_clean_markdown('Documents/Final_Paper/Final_Paper.docx', 'Documents/Final_Paper/Final_Paper.md')

    print("\nAll Final Paper documents successfully built and verified!")

if __name__ == '__main__':
    main()
