import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

# Check styles element
styles_elem = doc.styles.element
for s in styles_elem.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}style'):
    style_id = s.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
    if style_id in ['normal', 'Normal', 'Heading1', 'Heading2', 'Heading3']:
        print(f"=== Style: {style_id} ===")
        print(s.xml)
