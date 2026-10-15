import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

for s in doc.styles:
    if s.name in ['Normal', 'Heading 1', 'Heading 2', 'Heading 3', 'Title', 'Subtitle', 'List Bullet']:
        f = s.font
        print(f"Style: {s.name} | font={f.name}, size={f.size.pt if f.size else None}, bold={f.bold}, italic={f.italic}")
