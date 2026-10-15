import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Herbias, Hulleza, Opjer - GovSupply Connect_ A Municipal Procurement Transparency and Supply Distribution Monitoring System.docx')

for i in range(30, 36):
    p = doc.paragraphs[i]
    pf = p.paragraph_format
    print(f"--- P{i} ---")
    print(f"Text: '{p.text}'")
    print(f"Style: {p.style.name}")
    print(f"Align: {p.alignment}")
    print(f"Line Spacing: {pf.line_spacing}, Line Spacing Rule: {pf.line_spacing_rule}")
    print(f"Space Before: {pf.space_before}, Space After: {pf.space_after}")
    print(f"First Line Indent: {pf.first_line_indent.inches if pf.first_line_indent else None} in")
    print(f"Left Indent: {pf.left_indent.inches if pf.left_indent else None} in")
    for r in p.runs:
        print(f"  Run: text='{r.text}', font={r.font.name}, size={r.font.size.pt if r.font.size else None}, bold={r.bold}, all_caps={r.font.all_caps}")
