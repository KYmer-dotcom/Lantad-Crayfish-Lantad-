import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

for i in range(36, 95):
    p = doc.paragraphs[i]
    pf = p.paragraph_format
    runs = [(r.text[:30], r.bold) for r in p.runs]
    print(f"P{i:03d} [{p.style.name}] (align={p.alignment}, ind={pf.first_line_indent.inches if pf.first_line_indent else 0}in, sb={pf.space_before}, sa={pf.space_after}): text='{p.text[:60]}...' | runs={runs}")
