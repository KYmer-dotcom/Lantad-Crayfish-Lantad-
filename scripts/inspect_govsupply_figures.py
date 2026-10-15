import docx
import os

doc = docx.Document('Documents/GovSupply CHAPTER 4.docx')
for i, p in enumerate(doc.paragraphs[:40]):
    blips = p._p.xpath('.//a:blip')
    if 'Figure' in p.text or len(blips) > 0:
        print(f"p[{i}] style={p.style.name} text='{p.text[:60]}' blips={len(blips)}")
