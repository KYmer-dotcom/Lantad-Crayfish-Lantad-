import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

for i in [33, 34, 38, 39, 42, 65, 71]:
    p = doc.paragraphs[i]
    print(f"=== P{i}: {p.text[:30]} ===")
    print(p._p.pPr.xml)
