import docx

doc = docx.Document('Documents/GovSupply CHAPTER 4.docx')
for i in range(7, 10):
    p = doc.paragraphs[i]
    print(f"p[{i}] text='{p.text}' xml={p._p.xml[:200]}")
    for run in p.runs:
        print(f"  run text='{run.text}' element={run._r.xml[:200]}")
