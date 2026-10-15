import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

for i in range(25, 46):
    p = doc.paragraphs[i]
    print(f"P{i:03d} [{p.style.name}] (align={p.alignment}): '{p.text}'")
    for r in p.runs:
        print(f"   Run: '{r.text}' | font={r.font.name} | size={r.font.size.pt if r.font.size else None} | bold={r.bold} | italic={r.italic}")
