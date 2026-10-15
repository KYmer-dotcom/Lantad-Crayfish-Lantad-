import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

for i in range(78, 83):
    p = doc.paragraphs[i]
    print(f"=== Paragraph {i}: '{p.text[:40]}' ===")
    print(p._p.pPr.xml if p._p.pPr is not None else "No pPr")
